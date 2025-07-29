"""
通知管理器

负责任务进度通知、回调通知和飞书告警通知
"""

import json
import traceback
import os
import socket
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime
import requests
import pika
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from loguru import logger
from urllib.parse import urlparse

from ..config.settings import get_settings, ConfigurationError


class NotificationManager:
    """通知管理器"""
    
    def __init__(self):
        settings = get_settings()
        self.feishu_webhook_url = settings.feishu_webhook_url
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        self._init_rabbitmq_connection()
    
    def _init_rabbitmq_connection(self):
        """初始化RabbitMQ连接（用于回调通知）"""
        try:
            settings = get_settings()
            if settings.amqp_url:
                connection_params = pika.URLParameters(settings.amqp_url)
                connection_params.heartbeat = 600
                connection_params.blocked_connection_timeout = 300
                
                self.rabbitmq_connection = pika.BlockingConnection(connection_params)
                self.rabbitmq_channel = self.rabbitmq_connection.channel()
                logger.info("RabbitMQ回调连接初始化成功")
        except Exception as e:
            logger.warning(f"RabbitMQ回调连接初始化失败: {e}")
            self.rabbitmq_connection = None
            self.rabbitmq_channel = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.RequestException, requests.Timeout))
    )
    def send_http_callback(self, callback_url: str, task_data: Dict[str, Any]) -> bool:
        """
        发送HTTP回调通知
        
        Args:
            callback_url: 回调URL
            task_data: 任务数据
            
        Returns:
            发送是否成功
        """
        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'grid-AsyncTask/1.0.0'
            }
            
            settings = get_settings()
            response = requests.post(
                callback_url,
                json=task_data,
                headers=headers,
                timeout=settings.callback_timeout
            )
            
            if response.status_code == 200:
                logger.info(f"HTTP回调发送成功: {callback_url}")
                return True
            else:
                logger.warning(f"HTTP回调返回非200状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"HTTP回调发送失败: {callback_url}, 错误: {e}")
            raise
    
    def send_rabbitmq_callback(self, task_data: Dict[str, Any], 
                              queue_name: str = "callback_queue") -> bool:
        """
        发送RabbitMQ回调通知
        
        Args:
            task_data: 任务数据
            queue_name: 队列名称
            
        Returns:
            发送是否成功
        """
        try:
            if not self.rabbitmq_channel:
                logger.warning("RabbitMQ连接未初始化，无法发送回调")
                return False
            
            # 声明队列
            self.rabbitmq_channel.queue_declare(queue=queue_name, durable=True)
            
            # 发送消息
            self.rabbitmq_channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(task_data, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 消息持久化
                    content_type='application/json'
                )
            )
            
            logger.info(f"RabbitMQ回调发送成功: {queue_name}")
            return True
            
        except Exception as e:
            logger.error(f"RabbitMQ回调发送失败: {e}")
            # 尝试重新连接
            self._init_rabbitmq_connection()
            return False
    
    def send_task_callback(self, task_id: str, task_status: str, 
                          task_result: Any, callback_url: Optional[str] = None,
                          callback_type: str = "http", 
                          callback_data: Optional[Dict] = None) -> bool:
        """
        发送任务完成回调
        
        Args:
            task_id: 任务ID
            task_status: 任务状态
            task_result: 任务结果
            callback_url: 回调URL
            callback_type: 回调类型 (http/rabbitmq)
            callback_data: 附加回调数据
            
        Returns:
            发送是否成功
        """
        if not callback_url and callback_type == "http":
            logger.debug(f"任务 {task_id} 无回调URL，跳过回调通知")
            return True
        
        # 构建回调数据
        payload = {
            "task_id": task_id,
            "status": task_status,
            "result": task_result,
            "timestamp": datetime.utcnow().isoformat(),
            "callback_data": callback_data or {}
        }
        
        try:
            if callback_type == "http" and callback_url:
                return self.send_http_callback(callback_url, payload)
            elif callback_type == "rabbitmq":
                queue_name = callback_data.get("queue_name", "callback_queue") if callback_data else "callback_queue"
                return self.send_rabbitmq_callback(payload, queue_name)
            else:
                logger.warning(f"不支持的回调类型: {callback_type}")
                return False
                
        except Exception as e:
            logger.error(f"任务回调发送失败: {task_id}, 错误: {e}")
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.RequestException, requests.Timeout))
    )
    def send_feishu_notification(self, title: str, content: str, 
                                task_id: Optional[str] = None) -> bool:
        """
        发送飞书通知
        
        Args:
            title: 通知标题
            content: 通知内容
            task_id: 任务ID
            
        Returns:
            发送是否成功
        """
        if not self.feishu_webhook_url:
            logger.debug("飞书webhook URL未配置，跳过飞书通知")
            return True
        
        try:
            # 构建飞书消息格式
            message = {
                "msg_type": "interactive",
                "card": {
                    "config": {
                        "wide_screen_mode": True
                    },
                    "header": {
                        "title": {
                            "content": title,
                            "tag": "plain_text"
                        },
                        "template": "red"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "content": content,
                                "tag": "plain_text"
                            }
                        }
                    ]
                }
            }
            
            # 添加任务ID信息
            if task_id:
                message["card"]["elements"].append({
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**任务ID**: {task_id}",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                "tag": "lark_md"
                            }
                        }
                    ]
                })
            
            response = requests.post(
                self.feishu_webhook_url,
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"飞书通知发送成功: {title}")
                return True
            else:
                logger.warning(f"飞书通知发送失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"飞书通知发送失败: {e}")
            raise
    
    def notify_task_failed(self, task_id: str, error_message: str, 
                          task_data: Optional[Dict] = None, 
                          exception: Optional[Exception] = None) -> bool:
        """
        通知任务失败
        
        Args:
            task_id: 任务ID
            error_message: 错误信息
            task_data: 任务数据
            exception: 原始异常对象（用于获取堆栈信息）
            
        Returns:
            通知是否成功
        """
        title = "任务异常"
        
        # 构建详细的错误信息
        content_parts = [
            f"任务执行失败，请及时处理！",
            f"",
            f"**错误信息**: {error_message}"
        ]
        
        # 添加堆栈信息
        if exception:
            try:
                # 获取异常的完整堆栈跟踪
                tb_str = ''.join(traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                ))
                # 限制堆栈信息长度，避免通知过长
                if len(tb_str) > 5000:
                    tb_str = tb_str[:5000] + "...\n(堆栈信息已截断)"
                content_parts.extend([
                    f"",
                    f"**错误详情**:",
                    f"```",
                    tb_str,
                    f"```"
                ])
            except Exception as e:
                logger.warning(f"获取异常堆栈信息失败: {e}")
        
        # 添加任务信息
        if task_data:
            task_type = task_data.get('task_type', '未知')
            content_parts.append(f"**任务类型**: {task_type}")
            
            # 添加更多上下文信息
            if 'priority' in task_data:
                content_parts.append(f"**任务优先级**: {task_data['priority']}")
            
            if 'created_at' in task_data:
                content_parts.append(f"**创建时间**: {task_data['created_at']}")
            
            # 截取部分任务数据作为上下文（避免太长）
            if 'data' in task_data:
                data_str = str(task_data['data'])[:200]
                if len(str(task_data['data'])) > 200:
                    data_str += "..."
                content_parts.append(f"**任务数据**: {data_str}")
        
        # 添加Docker节点信息
        node_info = self._get_system_info()
        if node_info:
            content_parts.extend([
                f"",
                f"**系统信息**:",
                f"- 主机名: {node_info.get('hostname', '未知')}",
                f"- 容器ID: {node_info.get('container_id', '未知')}",
                f"- 镜像: {node_info.get('image', '未知')}",
                f"- 节点IP: {node_info.get('node_ip', '未知')}"
            ])
        
        content = "\n".join(content_parts)
        
        return self.send_feishu_notification(title, content, task_id)
    
    def notify_task_retry_exhausted(self, task_id: str, retry_count: int, 
                                   error_message: str, 
                                   exception: Optional[Exception] = None) -> bool:
        """
        通知任务重试次数耗尽
        
        Args:
            task_id: 任务ID
            retry_count: 重试次数
            error_message: 错误信息
            exception: 原始异常对象（用于获取堆栈信息）
            
        Returns:
            通知是否成功
        """
        title = "任务异常"
        
        # 构建详细的重试耗尽信息
        content_parts = [
            f"任务已重试 **{retry_count}** 次仍然失败，已停止重试。",
            f"",
            f"**最后失败原因**: {error_message}",
        ]
        
        # 添加堆栈信息
        if exception:
            try:
                # 获取异常的完整堆栈跟踪
                tb_str = ''.join(traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                ))
                # 限制堆栈信息长度，避免通知过长
                if len(tb_str) > 1000:
                    tb_str = tb_str[:1000] + "...\n(堆栈信息已截断)"
                content_parts.extend([
                    f"",
                    f"**错误详情**:",
                    f"```",
                    tb_str,
                    f"```"
                ])
            except Exception as e:
                logger.warning(f"获取异常堆栈信息失败: {e}")
        
        # 添加Docker节点信息
        node_info = self._get_system_info()
        if node_info:
            content_parts.extend([
                f"",
                f"**系统信息**:",
                f"- 主机名: {node_info.get('hostname', '未知')}",
                f"- 容器ID: {node_info.get('container_id', '未知')}",
                f"- 镜像: {node_info.get('image', '未知')}",
                f"- 节点IP: {node_info.get('node_ip', '未知')}"
            ])
        
        content_parts.extend([
            f"",
            f"请检查任务逻辑、数据格式或外部依赖是否正常。"
        ])
        
        content = "\n".join(content_parts)
        
        return self.send_feishu_notification(title, content, task_id)
    
    def _get_system_info(self) -> Optional[Dict[str, str]]:
        """获取系统和容器信息"""
        try:
            info = {}
            
            # 获取主机名
            info['hostname'] = socket.gethostname()
            
            # 获取本机IP
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    info['node_ip'] = s.getsockname()[0]
            except:
                info['node_ip'] = '未知'
            
            # 检查是否在Docker容器中
            if os.path.exists('/.dockerenv'):
                # 尝试获取容器ID
                try:
                    with open('/proc/self/cgroup', 'r') as f:
                        cgroup_data = f.read()
                        for line in cgroup_data.split('\n'):
                            if 'docker' in line:
                                container_id = line.split('/')[-1][:12]  # 取前12位
                                info['container_id'] = container_id
                                break
                        else:
                            info['container_id'] = '未知'
                except:
                    info['container_id'] = '未知'
                
                # 尝试获取镜像信息
                try:
                    # 从环境变量获取（如果有设置）
                    info['image'] = os.environ.get('DOCKER_IMAGE', '未知')
                except:
                    info['image'] = '未知'
            else:
                info['container_id'] = '非容器环境'
                info['image'] = '非容器环境'
            
            return info
            
        except Exception as e:
            logger.warning(f"获取系统信息失败: {e}")
            return None
    
    def notify_system_error(self, error_message: str, error_traceback: str = None) -> bool:
        """
        通知系统错误
        
        Args:
            error_message: 错误信息
            error_traceback: 错误堆栈
            
        Returns:
            通知是否成功
        """
        title = "🔥 系统异常"
        content = f"系统发生异常，请及时处理！\n\n错误信息: {error_message}"
        
        if error_traceback:
            content += f"\n\n错误堆栈:\n```\n{error_traceback[:1000]}...\n```"
        
        return self.send_feishu_notification(title, content)
    
    def close(self):
        """关闭连接"""
        try:
            if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
                self.rabbitmq_connection.close()
                logger.info("RabbitMQ回调连接已关闭")
        except Exception as e:
            logger.warning(f"关闭RabbitMQ回调连接失败: {e}")

 