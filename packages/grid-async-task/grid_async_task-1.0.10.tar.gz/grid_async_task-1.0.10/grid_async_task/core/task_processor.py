"""
任务处理器核心引擎

负责从RabbitMQ队列消费任务、执行任务、处理重试、进度报告等
"""

import json
import signal
import time
import traceback
import threading
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError
from loguru import logger

from .task_handler import TaskHandler
from .database_manager import DatabaseManager
from .notification_manager import NotificationManager
from ..config.settings import get_settings, ConfigurationError


class TaskRetryExhaustedException(Exception):
    """重试次数耗尽异常"""
    def __init__(self, task_id: str, retry_count: int, original_error: str, original_exception: Exception = None):
        self.task_id = task_id
        self.retry_count = retry_count
        self.original_error = original_error
        self.original_exception = original_exception  # 保留原始异常对象
        super().__init__(f"任务 {task_id} 重试次数已耗尽 ({retry_count}次)，最后错误: {original_error}")


class TaskNotRetryableException(Exception):
    """任务不符合重试条件异常"""
    def __init__(self, task_id: str, reason: str, original_error: str, original_exception: Exception = None):
        self.task_id = task_id
        self.reason = reason
        self.original_error = original_error
        self.original_exception = original_exception  # 保留原始异常对象
        super().__init__(f"任务 {task_id} 不符合重试条件: {reason}，原始错误: {original_error}")


class TaskProcessor:
    """任务处理器"""
    
    def __init__(self, handler: TaskHandler, **kwargs):
        self.handler = handler
        self.db_manager = DatabaseManager()
        self.notification_manager = NotificationManager()
        
        # 获取设置
        try:
            self.settings = get_settings()
        except ConfigurationError as e:
            logger.error(f"配置错误: {e}")
            raise
        
        # 配置参数
        self.max_retry_count = kwargs.get('max_retry_count', self.settings.max_retry_count)
        self.retry_delay = kwargs.get('retry_delay', self.settings.retry_delay)
        self.prefetch_count = kwargs.get('prefetch_count', self.settings.prefetch_count)
        self.task_timeout = kwargs.get('task_timeout', self.settings.task_timeout)
        self.idle_timeout = kwargs.get('idle_timeout', self.settings.idle_timeout)
        
        # 连接相关
        self.connection = None
        self.channel = None
        self.is_running = False
        self.current_task_id = None
        
        # 空闲检测相关
        self.last_activity_time = time.time()
        self.is_idle = False
        
        # 进度报告线程
        self.progress_thread = None
        self.progress_stop_event = threading.Event()
        
        # 设置日志上下文
        self._setup_logging()
        
        # 注册信号处理（仅在主线程中注册）
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except ValueError as e:
            # 在非主线程中会抛出ValueError，这是正常的
            logger.debug(f"信号处理器注册失败（非主线程）: {e}")
    
    def _setup_logging(self):
        """设置日志配置"""
        import os
        
        # 确保日志目录存在
        os.makedirs(self.settings.log_dir, exist_ok=True)
        
        # 配置loguru
        logger.remove()  # 移除默认处理器
        
        # 添加文件处理器
        log_config = self.settings.get_log_config()
        logger.add(**log_config)
        
        # 添加控制台处理器
        logger.add(
            sink=lambda msg: print(msg, end=""),
            level=self.settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            colorize=True
        )
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"接收到信号 {signum}，准备优雅关闭...")
        self.stop()
    
    def _update_activity_time(self):
        """更新最后活动时间"""
        self.last_activity_time = time.time()
        if self.is_idle:
            self.is_idle = False
            logger.info("退出空闲状态")
    
    def _check_idle_timeout(self) -> bool:
        """检查是否超过空闲时间，返回True表示应该退出"""
        if self.idle_timeout <= 0:
            return False  # 0表示永不退出
        
        if self.current_task_id is not None:
            # 有任务在执行，不算空闲，重置空闲状态
            if self.is_idle:
                self.is_idle = False
                logger.info("有任务执行，退出空闲状态")
            return False
        
        # 计算空闲时长
        idle_duration = time.time() - self.last_activity_time
        
        if idle_duration >= self.idle_timeout:
            if not self.is_idle:
                logger.info(f"检测到空闲超时：已空闲 {idle_duration:.1f} 秒，超过设定值 {self.idle_timeout} 秒")
                self.is_idle = True
            return True
        else:
            # 还没到超时时间，如果之前是空闲状态则退出空闲状态
            if self.is_idle:
                self.is_idle = False
                logger.info("空闲时间未到阈值，退出空闲状态")
        
        return False
    
    def _connect_rabbitmq(self) -> bool:
        """连接RabbitMQ"""
        try:
            # 使用AMQP URL连接
            connection_params = pika.URLParameters(self.settings.amqp_url)
            connection_params.heartbeat = 600
            connection_params.blocked_connection_timeout = 300
            
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            
            # 设置QoS，每次只处理一个消息
            self.channel.basic_qos(prefetch_count=self.prefetch_count)
            
            # 声明队列
            self.channel.queue_declare(queue=self.settings.rabbitmq_queue, durable=True)
            
            logger.info("RabbitMQ连接建立成功")
            return True
            
        except Exception as e:
            logger.error(f"RabbitMQ连接失败: {e}")
            return False
    
    def _reconnect_rabbitmq(self, max_retries: int = 5) -> bool:
        """重连RabbitMQ"""
        for attempt in range(max_retries):
            logger.info(f"尝试重连RabbitMQ... (第 {attempt + 1}/{max_retries} 次)")
            
            try:
                if self.connection and not self.connection.is_closed:
                    self.connection.close()
            except:
                pass
            
            if self._connect_rabbitmq():
                return True
            
            time.sleep(min(2 ** attempt, 30))  # 指数退避
        
        logger.error("RabbitMQ重连失败")
        return False
    
    def _process_message(self, channel, method, properties, body):
        """处理单个消息"""
        # 更新活动时间
        self._update_activity_time()
        
        try:
            # 解析消息
            try:
                task_data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"消息解析失败: {e}")
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            task_id = task_data.get('task_id')
            if not task_id:
                logger.error("消息中缺少task_id字段")
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            self.current_task_id = task_id
            
            # 设置日志上下文
            with logger.contextualize(task_id=task_id):
                logger.info(f"开始处理任务: {task_id}")
                
                # 获取任务记录（应该已经由生产者创建）
                task = self.db_manager.get_task(task_id)
                if not task:
                    # 如果任务记录不存在，可能是旧版本发送的任务，创建一个新的
                    logger.warning(f"任务记录不存在，创建新记录: {task_id}")
                    task = self.db_manager.create_task(task_data)
                else:
                    logger.info(f"找到已存在的任务记录: {task_id}, 状态: {task.status}")
                
                # 执行任务
                success = self._execute_task(task_id, task_data)
                
                if success:
                    # 确认消息
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"任务处理完成: {task_id}")
                else:
                    # 任务失败，根据重试策略决定是否重新入队
                    task = self.db_manager.get_task(task_id)
                    if task and task.retry_count < task.max_retry_count and task.status == 'retrying':
                        # 重新入队
                        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                        logger.info(f"任务重新入队: {task_id}")
                    else:
                        # 不再重试，确认消息（_execute_task中已经处理了所有的失败逻辑）
                        channel.basic_ack(delivery_tag=method.delivery_tag)
                        logger.info(f"任务彻底失败: {task_id}")
        
        except Exception as e:
            logger.error(f"消息处理异常: {e}\n{traceback.format_exc()}")
            # 发送系统错误通知
            self.notification_manager.notify_system_error(
                str(e), traceback.format_exc()
            )
            # 确认消息以避免死循环
            channel.basic_ack(delivery_tag=method.delivery_tag)
        finally:
            self.current_task_id = None
            # 任务处理完成后，重置空闲计时器
            self._update_activity_time()
    
    def _execute_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """执行任务"""
        try:
            # 更新任务状态为运行中
            self.db_manager.update_task_status(task_id, 'running')
            
            # 设置任务处理器
            self.handler.setup(task_id, task_data, self)
            
            # 验证任务数据
            if not self.handler.validate_task_data(task_data.get('data', {})):
                raise ValueError("任务数据验证失败")
            
            # 执行任务开始钩子
            self.handler.on_task_start()
            
            # 执行任务
            logger.info(f"开始执行任务逻辑: {task_id}")
            result = self.handler.execute(task_data.get('data', {}))
            
            # 更新任务结果和状态
            self.db_manager.update_task_result(task_id, result)
            self.db_manager.update_task_status(task_id, 'success')
            self.db_manager.update_task_progress(task_id, 100, "任务完成")
            
            # 执行任务完成钩子
            self.handler.on_task_complete(result)
            
            # 发送回调通知
            task = self.db_manager.get_task(task_id)
            if task:
                self.notification_manager.send_task_callback(
                    task_id=task_id,
                    task_status='success',
                    task_result=result,
                    callback_url=task.callback_url,
                    callback_type=task.callback_type,
                    callback_data=task.callback_data
                )
            
            logger.info(f"任务执行成功: {task_id}")
            return True
            
        except Exception as e:
            # 统一的异常处理入口
            return self._handle_task_failure(task_id, task_data, e)
    
    def _handle_task_failure(self, task_id: str, task_data: Dict[str, Any], exception: Exception) -> bool:
        """统一处理任务失败"""
        error_message = str(exception)
        logger.error(f"任务执行失败: {task_id}, 错误: {error_message}")
        
        # 执行任务错误钩子
        self.handler.on_task_error(exception)
        
        # 获取当前任务信息
        task = self.db_manager.get_task(task_id)
        if not task:
            return False
        
        try:
            # 先增加重试次数
            self.db_manager.increment_retry_count(task_id)
            
            # 重新获取任务信息（包含更新后的重试次数）
            task = self.db_manager.get_task(task_id)
            
            # 判断是否应该重试
            should_retry = (task.retry_count < task.max_retry_count and 
                          self.handler.should_retry(exception))
            
            if should_retry:
                # 更新状态为重试中
                self.db_manager.update_task_status(
                    task_id, 'retrying', 
                    error_message=error_message
                )
                logger.info(f"任务将重试: {task_id}, 当前重试次数: {task.retry_count}")
                return False  # 返回False表示需要重新入队
                
            else:
                # 不再重试，抛出相应的异常让上层统一处理
                if task.retry_count >= task.max_retry_count:
                    logger.info(f"任务重试次数已耗尽: {task_id}, 重试次数: {task.retry_count}/{task.max_retry_count}")
                    raise TaskRetryExhaustedException(task_id, task.retry_count, error_message, exception)
                else:
                    logger.info(f"任务不符合重试条件: {task_id}, 重试次数: {task.retry_count}/{task.max_retry_count}")
                    raise TaskNotRetryableException(task_id, "不符合重试条件", error_message, exception)
                    
        except (TaskRetryExhaustedException, TaskNotRetryableException) as final_exception:
            # 处理最终失败
            return self._handle_final_task_failure(task_id, task_data, task, final_exception)
        except Exception as e:
            logger.error(f"处理任务失败时出现异常: {e}")
            return False
    
    def _handle_final_task_failure(self, task_id: str, task_data: Dict[str, Any], 
                                 task: Any, final_exception: Exception) -> bool:
        """处理任务最终失败（不再重试）"""
        try:
            # 更新任务状态为失败
            logger.info(f"任务彻底失败，更新状态为failed: {task_id}")
            self.db_manager.update_task_status(
                task_id, 'failed', 
                error_message=str(final_exception)
            )
            
            # 根据异常类型安全地构建回调数据
            callback_result = self._build_safe_callback_result(task, final_exception)
            
            # 根据异常类型发送不同的通知（内部通知可以包含详细信息）
            if isinstance(final_exception, TaskRetryExhaustedException):
                # 重试耗尽通知
                self.notification_manager.notify_task_retry_exhausted(
                    task_id, final_exception.retry_count, final_exception.original_error, 
                    final_exception.original_exception
                )
                
            elif isinstance(final_exception, TaskNotRetryableException):
                # 普通失败通知
                self.notification_manager.notify_task_failed(
                    task_id, final_exception.original_error, task_data, 
                    final_exception.original_exception
                )
            else:
                # 其他异常
                self.notification_manager.notify_task_failed(
                    task_id, str(final_exception), task_data, final_exception
                )
            
            # 发送安全的失败回调（不包含敏感信息）
            self.notification_manager.send_task_callback(
                task_id=task_id,
                task_status='failed',
                task_result=callback_result,
                callback_url=task.callback_url,
                callback_type=task.callback_type,
                callback_data=task.callback_data
            )
            
            logger.info(f"任务最终失败处理完成: {task_id}")
            return False
            
        except Exception as e:
            logger.error(f"处理任务最终失败时出现异常: {e}")
            return False
    
    def _build_safe_callback_result(self, task: Any, final_exception: Exception) -> Dict[str, Any]:
        """构建安全的回调结果，避免泄露敏感信息"""
        
        # 基础回调数据
        base_result = {
            "task_id": task.task_id,
            "retry_count": task.retry_count,
            "max_retry_count": task.max_retry_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 根据异常类型确定错误类型和消息
        if isinstance(final_exception, TaskRetryExhaustedException):
            # 重试耗尽：返回内部错误信息
            base_result.update({
                "error_type": "retry_exhausted",
                "error_code": "TASK_RETRY_EXHAUSTED",
                "error_message": f"任务执行失败，已重试 {final_exception.retry_count} 次",
                "retry_exhausted": True
            })
            
        elif isinstance(final_exception, TaskNotRetryableException):
            # 不可重试：根据原始异常类型判断是否返回详细信息
            if self._is_validation_error(final_exception.original_exception):
                # 参数校验错误：可以返回详细信息帮助调用方修正
                base_result.update({
                    "error_type": "validation_error",
                    "error_code": "INVALID_PARAMETERS",
                    "error_message": final_exception.original_error,
                    "retry_exhausted": False
                })
            else:
                # 其他不可重试错误：返回通用错误信息
                base_result.update({
                    "error_type": "non_retryable_error",
                    "error_code": "TASK_EXECUTION_FAILED",
                    "error_message": "任务执行失败，无法重试",
                    "retry_exhausted": False
                })
        else:
            # 其他异常：返回通用内部错误
            base_result.update({
                "error_type": "internal_error",
                "error_code": "INTERNAL_ERROR",
                "error_message": "内部错误，请稍后重试",
                "retry_exhausted": False
            })
        
        return base_result
    
    def _is_validation_error(self, exception: Exception) -> bool:
        """判断是否为参数校验错误（基于异常类型而非字符串匹配）"""
        if exception is None:
            return False
            
        # 常见的参数校验异常类型
        validation_exception_types = (
            ValueError,           # 值错误
            TypeError,           # 类型错误  
            AttributeError,      # 属性错误
            KeyError,           # 键错误（缺少必要参数）
            IndexError,         # 索引错误
        )
        
        # 直接基于异常类型判断（最准确的方式）
        if isinstance(exception, validation_exception_types):
            return True
            
        # 如果是其他自定义异常，检查异常名称
        exception_class_name = exception.__class__.__name__
        validation_class_names = [
            'ValidationError',
            'ParameterError', 
            'InvalidParameterError',
            'SchemaError',
            'FormatError'
        ]
        
        if exception_class_name in validation_class_names:
            return True
            
        # 最后通过错误消息判断（作为兜底方案）
        error_str = str(exception)
        validation_indicators = [
            '参数',
            '校验',
            '验证',
            'validation',
            'invalid parameter',
            'missing required',
            'parameter is required',
            'invalid format',
            'invalid value'
        ]
        
        return any(indicator.lower() in error_str.lower() for indicator in validation_indicators)
    
    def report_progress(self, task_id: str, progress: int, message: str = ""):
        """报告任务进度"""
        try:
            self.db_manager.update_task_progress(task_id, progress, message)
            logger.debug(f"进度更新: {task_id} -> {progress}% | {message}")
        except Exception as e:
            logger.warning(f"进度更新失败: {e}")
    
    def start(self):
        """启动任务处理器"""
        logger.info("启动任务处理器...")
        
        if not self._connect_rabbitmq():
            raise RuntimeError("无法连接到RabbitMQ")
        
        self.is_running = True
        
        try:
            # 设置消息消费者
            self.channel.basic_consume(
                queue=self.settings.rabbitmq_queue,
                on_message_callback=self._process_message
            )
            
            logger.info(f"开始监听队列: {self.settings.rabbitmq_queue}")
            if self.idle_timeout > 0:
                logger.info(f"空闲超时设置: {self.idle_timeout} 秒")
            else:
                logger.info("空闲超时禁用")
            
            # 开始消费消息
            while self.is_running:
                try:
                    self.connection.process_data_events(time_limit=1)
                    
                    # 检查空闲超时
                    if self._check_idle_timeout():
                        logger.info("空闲超时，准备退出程序")
                        break
                        
                except (AMQPConnectionError, AMQPChannelError) as e:
                    logger.error(f"RabbitMQ连接中断: {e}")
                    if self.is_running and not self._reconnect_rabbitmq():
                        break
                except KeyboardInterrupt:
                    logger.info("接收到中断信号")
                    break
                except Exception as e:
                    logger.error(f"消息处理异常: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            logger.error(f"任务处理器异常: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self):
        """停止任务处理器"""
        if not self.is_running:
            return
            
        logger.info("停止任务处理器...")
        self.is_running = False
        
        # 等待当前任务完成
        if self.current_task_id:
            logger.info(f"等待当前任务完成: {self.current_task_id}")
            timeout = 30  # 30秒超时
            while self.current_task_id and timeout > 0:
                time.sleep(1)
                timeout -= 1
        
        # 关闭连接
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.stop_consuming()
            
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                
        except Exception as e:
            logger.warning(f"关闭RabbitMQ连接失败: {e}")
        
        # 关闭数据库连接
        self.db_manager.close()
        
        # 关闭通知管理器
        self.notification_manager.close()
        
        logger.info("任务处理器已停止")
    
    def get_status(self) -> Dict[str, Any]:
        """获取处理器状态"""
        return {
            "is_running": self.is_running,
            "current_task_id": self.current_task_id,
            "rabbitmq_connected": (self.connection and 
                                 not self.connection.is_closed),
            "settings": {
                "max_retry_count": self.max_retry_count,
                "retry_delay": self.retry_delay,
                "prefetch_count": self.prefetch_count,
                "task_timeout": self.task_timeout
            }
        } 