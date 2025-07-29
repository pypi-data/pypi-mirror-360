"""
grid 异步任务处理插件

一个通用的异步任务处理框架，支持：
- RabbitMQ队列监听
- 任务重试机制
- 进度通知
- 回调通知
- MySQL持久化
- 飞书通知
"""

__version__ = "1.0.0"
__author__ = "grid"

from .core.task_handler import TaskHandler
from .core.task_processor import TaskProcessor
from .core.task_producer import TaskProducer
from .core.database_manager import DatabaseManager
from .core.notification_manager import NotificationManager
from .config.settings import Settings, ConfigurationError

__all__ = [
    "TaskHandler",
    "TaskProcessor", 
    "TaskProducer",
    "DatabaseManager",
    "NotificationManager",
    "Settings",
    "ConfigurationError"
] 