"""
任务生产者

负责向RabbitMQ队列发送任务消息，并同时创建数据库记录
"""

import json
import uuid
from typing import Dict, Any, Optional, List
import pika
from pika.exceptions import AMQPConnectionError
from loguru import logger

from ..config.settings import get_settings, ConfigurationError
from .database_manager import DatabaseManager


class TaskProducer:
    """任务生产者"""
    
    def __init__(self, default_queue: Optional[str] = None):
        """
        初始化任务生产者
        
        Args:
            default_queue: 默认队列名称，如果不提供则使用配置文件中的队列名称
        """
        self.connection = None
        self.channel = None
        self.default_queue = default_queue
        self.declared_queues = set()  # 已声明的队列集合
        self.db_manager = DatabaseManager()
        self._connect()
    
    def _connect(self):
        """连接RabbitMQ"""
        try:
            settings = get_settings()
            connection_params = pika.URLParameters(settings.amqp_url)
            
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            
            # 声明默认队列
            default_queue_name = self.default_queue or settings.rabbitmq_queue
            self._declare_queue(default_queue_name)
            
            logger.info("任务生产者连接RabbitMQ成功")
            
        except Exception as e:
            logger.error(f"任务生产者连接RabbitMQ失败: {e}")
            raise
    
    def _declare_queue(self, queue_name: str, durable: bool = True) -> None:
        """
        声明队列（如果尚未声明）
        
        Args:
            queue_name: 队列名称
            durable: 是否持久化队列
        """
        if queue_name not in self.declared_queues:
            try:
                self.channel.queue_declare(queue=queue_name, durable=durable)
                self.declared_queues.add(queue_name)
                logger.info(f"队列声明成功: {queue_name}")
            except Exception as e:
                logger.error(f"队列声明失败 {queue_name}: {e}")
                raise
    
    def _get_queue_name(self, queue_name: Optional[str] = None) -> str:
        """
        获取要使用的队列名称
        
        Args:
            queue_name: 指定的队列名称
            
        Returns:
            最终使用的队列名称
        """
        if queue_name:
            return queue_name
        elif self.default_queue:
            return self.default_queue
        else:
            settings = get_settings()
            return settings.rabbitmq_queue

    def send_task(self, task_data: Dict[str, Any], task_id: Optional[str] = None, 
                  queue_name: Optional[str] = None) -> str:
        """
        发送任务到指定队列并创建数据库记录
        
        Args:
            task_data: 任务数据
            task_id: 任务ID，如果不提供则自动生成
            queue_name: 队列名称，如果不提供则使用默认队列
            
        Returns:
            任务ID
        """
        if not task_id:
            task_id = str(uuid.uuid4())
        
        # 确定使用的队列名称
        target_queue = self._get_queue_name(queue_name)
        
        # 确保目标队列已声明
        self._declare_queue(target_queue)
        
        # 构建完整的任务消息
        settings = get_settings()
        message = {
            "task_id": task_id,
            "task_type": task_data.get("task_type", "default"),
            "data": task_data.get("data", {}),
            "max_retry_count": task_data.get("max_retry_count", settings.max_retry_count),
            "callback_url": task_data.get("callback_url"),
            "callback_type": task_data.get("callback_type", "http"),
            "callback_data": task_data.get("callback_data"),
            "queue_name": target_queue  # 添加队列信息到消息中
        }
        
        try:
            # 首先创建数据库记录，状态为pending
            logger.info(f"创建任务数据库记录: {task_id}")
            task = self.db_manager.create_task(message)
            
            # 然后发送消息到指定队列
            self.channel.basic_publish(
                exchange=settings.rabbitmq_exchange,
                routing_key=target_queue,
                body=json.dumps(message, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 消息持久化
                    content_type='application/json'
                )
            )
            
            logger.info(f"任务发送成功: {task_id} -> 队列: {target_queue}")
            return task_id
            
        except Exception as e:
            logger.error(f"任务发送失败: {e}")
            # 如果发送失败，尝试删除已创建的数据库记录或标记为失败
            try:
                self.db_manager.update_task_status(
                    task_id, 'failed', 
                    error_message=f"任务发送失败: {str(e)}"
                )
            except Exception as cleanup_e:
                logger.error(f"清理失败任务记录时出错: {cleanup_e}")
            raise
    
    def send_task_to_queue(self, task_data: Dict[str, Any], queue_name: str, 
                          task_id: Optional[str] = None) -> str:
        """
        发送任务到指定队列的便捷方法
        
        Args:
            task_data: 任务数据
            queue_name: 目标队列名称
            task_id: 任务ID，如果不提供则自动生成
            
        Returns:
            任务ID
        """
        return self.send_task(task_data, task_id, queue_name)
    
    def batch_send_tasks(self, tasks: List[Dict[str, Any]], 
                        queue_name: Optional[str] = None) -> List[str]:
        """
        批量发送任务到指定队列
        
        Args:
            tasks: 任务数据列表，每个元素包含task_data和可选的task_id
            queue_name: 队列名称，如果不提供则使用默认队列
            
        Returns:
            任务ID列表
        """
        task_ids = []
        target_queue = self._get_queue_name(queue_name)
        
        # 预先声明队列
        self._declare_queue(target_queue)
        
        for task in tasks:
            task_data = task.get('task_data', {})
            task_id = task.get('task_id')
            
            try:
                result_task_id = self.send_task(task_data, task_id, target_queue)
                task_ids.append(result_task_id)
            except Exception as e:
                logger.error(f"批量发送任务失败，任务数据: {task_data}, 错误: {e}")
                # 继续处理其他任务
                continue
        
        logger.info(f"批量发送任务完成，成功: {len(task_ids)}/{len(tasks)}")
        return task_ids
    
    def get_declared_queues(self) -> set:
        """
        获取已声明的队列列表
        
        Returns:
            已声明的队列名称集合
        """
        return self.declared_queues.copy()
    
    def is_queue_declared(self, queue_name: str) -> bool:
        """
        检查队列是否已声明
        
        Args:
            queue_name: 队列名称
            
        Returns:
            是否已声明
        """
        return queue_name in self.declared_queues

    def close(self):
        """关闭连接"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("任务生产者RabbitMQ连接已关闭")
        except Exception as e:
            logger.warning(f"关闭任务生产者RabbitMQ连接失败: {e}")
        
        # 关闭数据库连接
        try:
            self.db_manager.close()
        except Exception as e:
            logger.warning(f"关闭任务生产者数据库连接失败: {e}") 