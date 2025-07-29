"""
任务处理器基类

提供任务执行的通用接口和进度报告功能
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from loguru import logger


class TaskHandler(ABC):
    """任务处理器抽象基类"""
    
    def __init__(self):
        self.task_id: Optional[str] = None
        self.task_data: Optional[Dict[str, Any]] = None
        self._processor = None
    
    def setup(self, task_id: str, task_data: Dict[str, Any], processor):
        """设置任务信息和处理器引用"""
        self.task_id = task_id
        self.task_data = task_data
        self._processor = processor
    
    @abstractmethod
    def execute(self, task_data: Dict[str, Any]) -> Any:
        """
        执行任务的核心方法
        
        Args:
            task_data: 任务数据
            
        Returns:
            任务执行结果
            
        Raises:
            Exception: 任务执行异常
        """
        raise NotImplementedError("子类必须实现 execute 方法")
    
    def report_progress(self, progress: int, message: str = "") -> None:
        """
        报告任务进度
        
        Args:
            progress: 进度百分比 (0-100)
            message: 进度描述信息
        """
        if not self.task_id:
            logger.warning("无法报告进度，任务ID为空")
            return
        
        # 限制进度范围
        progress = max(0, min(100, progress))
        
        if self._processor:
            self._processor.report_progress(self.task_id, progress, message)
        
        logger.info(f"任务进度更新: {self.task_id} -> {progress}% | {message}")
    
    def get_task_id(self) -> Optional[str]:
        """获取当前任务ID"""
        return self.task_id
    
    def get_task_data(self) -> Optional[Dict[str, Any]]:
        """获取当前任务数据"""
        return self.task_data
    
    def validate_task_data(self, task_data: Dict[str, Any]) -> bool:
        """
        验证任务数据
        
        子类可以重写此方法来实现自定义验证逻辑
        
        Args:
            task_data: 任务数据
            
        Returns:
            验证结果
        """
        return True
    
    def on_task_start(self) -> None:
        """
        任务开始前的钩子方法
        
        子类可以重写此方法来实现初始化逻辑
        """
        pass
    
    def on_task_complete(self, result: Any) -> None:
        """
        任务完成后的钩子方法
        
        子类可以重写此方法来实现清理逻辑
        
        Args:
            result: 任务执行结果
        """
        pass
    
    def on_task_error(self, error: Exception) -> None:
        """
        任务出错时的钩子方法
        
        子类可以重写此方法来实现错误处理逻辑
        
        Args:
            error: 异常对象
        """
        pass
    
    def should_retry(self, error: Exception) -> bool:
        """
        判断是否应该重试
        
        子类可以重写此方法来实现自定义重试逻辑
        
        Args:
            error: 异常对象
            
        Returns:
            是否应该重试
        """
        return True 