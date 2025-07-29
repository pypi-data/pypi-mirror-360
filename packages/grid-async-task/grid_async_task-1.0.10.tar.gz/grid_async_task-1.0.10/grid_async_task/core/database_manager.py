"""
数据库管理模块

负责任务的持久化存储和数据库连接管理
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Generator
from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from loguru import logger

from ..config.settings import get_settings, ConfigurationError

Base = declarative_base()


def create_async_task_model(table_name: str):
    """创建动态表名的AsyncTask模型"""
    
    class AsyncTask(Base):
        """异步任务表模型"""
        
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}
        
        # 基本字段
        id = Column(Integer, primary_key=True, autoincrement=True, comment='自增主键ID')
        task_id = Column(String(255), unique=True, nullable=False, index=True, comment='任务唯一标识')
        task_type = Column(String(100), nullable=False, comment='任务类型')
        status = Column(
            SQLEnum('pending', 'running', 'success', 'failed', 'retrying', name='task_status'),
            default='pending',
            comment='任务状态'
        )
        
        # 任务数据
        data = Column(JSON, comment='任务数据')
        result = Column(JSON, comment='任务结果')
        error_message = Column(Text, comment='错误信息')
        
        # 进度相关
        progress = Column(Integer, default=0, comment='任务进度(0-100)')
        progress_message = Column(String(500), comment='进度描述')
        
        # 重试相关
        retry_count = Column(Integer, default=0, comment='已重试次数')
        max_retry_count = Column(Integer, default=0, comment='最大重试次数')
        
        # 回调相关
        callback_url = Column(String(500), comment='回调URL')
        callback_type = Column(
            SQLEnum('http', 'rabbitmq', name='callback_type'),
            default='http',
            comment='回调类型'
        )
        callback_data = Column(JSON, comment='回调附加数据')
        
        # 时间字段
        created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
        started_at = Column(DateTime, comment='开始时间')
        completed_at = Column(DateTime, comment='完成时间')
        
        def to_dict(self) -> dict:
            """转换为字典格式"""
            return {
                'id': self.id,
                'task_id': self.task_id,
                'task_type': self.task_type,
                'status': self.status,
                'data': self.data,
                'result': self.result,
                'error_message': self.error_message,
                'progress': self.progress,
                'progress_message': self.progress_message,
                'retry_count': self.retry_count,
                'max_retry_count': self.max_retry_count,
                'callback_url': self.callback_url,
                'callback_type': self.callback_type,
                'callback_data': self.callback_data,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None
            }
    
    return AsyncTask


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.AsyncTask = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库连接"""
        try:
            settings = get_settings()
            
            # 创建动态表模型
            self.AsyncTask = create_async_task_model(settings.full_table_name)
            
            # 创建数据库引擎
            self.engine = create_engine(
                settings.mysql_url,
                poolclass=QueuePool,
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_max_overflow,
                pool_timeout=settings.db_pool_timeout,
                pool_recycle=settings.db_pool_recycle,
                echo=settings.log_level == 'DEBUG'
            )
            
            # 创建会话工厂
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # 创建表
            Base.metadata.create_all(bind=self.engine)
            
            logger.info(f"数据库初始化成功，表名: {settings.full_table_name}")
            
        except ConfigurationError as e:
            logger.error(f"数据库初始化失败 - 配置错误:\n{e}")
            raise
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """获取数据库会话上下文管理器"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    def create_task(self, task_data: Dict[str, Any]):
        """创建新任务"""
        with self.get_session() as session:
            task = self.AsyncTask(
                task_id=task_data['task_id'],
                task_type=task_data.get('task_type', 'default'),
                data=task_data.get('data'),
                max_retry_count=task_data.get('max_retry_count', get_settings().max_retry_count),
                callback_url=task_data.get('callback_url'),
                callback_type=task_data.get('callback_type', 'http'),
                callback_data=task_data.get('callback_data')
            )
            session.add(task)
            session.flush()
            
            # 强制加载所有属性并从session中分离
            _ = (task.id, task.task_id, task.task_type, task.status, task.data, task.result, 
                 task.error_message, task.progress, task.progress_message,
                 task.retry_count, task.max_retry_count, task.callback_url,
                 task.callback_type, task.callback_data, task.created_at,
                 task.updated_at, task.started_at, task.completed_at)
            session.expunge(task)
            
            logger.info(f"创建任务成功: {task.task_id}")
            return task
    
    def get_task(self, task_id: str):
        """获取任务信息"""
        with self.get_session() as session:
            task = session.query(self.AsyncTask).filter(self.AsyncTask.task_id == task_id).first()
            if task:
                # 强制加载所有属性到内存中，避免DetachedInstanceError
                # 触发所有属性的加载
                _ = (task.id, task.task_id, task.task_type, task.status, task.data, task.result, 
                     task.error_message, task.progress, task.progress_message,
                     task.retry_count, task.max_retry_count, task.callback_url,
                     task.callback_type, task.callback_data, task.created_at,
                     task.updated_at, task.started_at, task.completed_at)
                
                # 使用expunge将对象从session中分离，但保持已加载的属性
                session.expunge(task)
            return task
    
    def update_task_status(self, task_id: str, status: str, **kwargs) -> bool:
        """更新任务状态"""
        with self.get_session() as session:
            task = session.query(self.AsyncTask).filter(self.AsyncTask.task_id == task_id).first()
            if not task:
                logger.warning(f"任务不存在: {task_id}")
                return False
            
            task.status = status
            
            # 更新其他字段
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            # 根据状态设置时间字段
            if status == 'running' and not task.started_at:
                task.started_at = datetime.utcnow()
            elif status in ['success', 'failed'] and not task.completed_at:
                task.completed_at = datetime.utcnow()
            
            session.flush()
            logger.info(f"更新任务状态成功: {task_id} -> {status}")
            return True
    
    def update_task_progress(self, task_id: str, progress: int, message: str = "") -> bool:
        """更新任务进度"""
        with self.get_session() as session:
            task = session.query(self.AsyncTask).filter(self.AsyncTask.task_id == task_id).first()
            if not task:
                logger.warning(f"任务不存在: {task_id}")
                return False
            
            task.progress = progress
            task.progress_message = message
            session.flush()
            logger.debug(f"更新任务进度: {task_id} -> {progress}%")
            return True
    
    def update_task_result(self, task_id: str, result: Any) -> bool:
        """更新任务结果"""
        with self.get_session() as session:
            task = session.query(self.AsyncTask).filter(self.AsyncTask.task_id == task_id).first()
            if not task:
                logger.warning(f"任务不存在: {task_id}")
                return False
            
            task.result = result if isinstance(result, dict) else {"data": result}
            session.flush()
            logger.info(f"更新任务结果成功: {task_id}")
            return True
    
    def increment_retry_count(self, task_id: str) -> bool:
        """增加重试次数"""
        with self.get_session() as session:
            task = session.query(self.AsyncTask).filter(self.AsyncTask.task_id == task_id).first()
            if not task:
                logger.warning(f"任务不存在: {task_id}")
                return False
            
            task.retry_count += 1
            session.flush()
            logger.info(f"任务重试次数增加: {task_id} -> {task.retry_count}")
            return True
    
    def get_failed_tasks(self, limit: int = 100):
        """获取失败的任务列表"""
        with self.get_session() as session:
            tasks = session.query(self.AsyncTask).filter(
                self.AsyncTask.status == 'failed'
            ).order_by(self.AsyncTask.id.desc()).limit(limit).all()
            
            # 预加载所有属性并从session中分离
            for task in tasks:
                _ = (task.id, task.task_id, task.task_type, task.status, task.data, task.result, 
                     task.error_message, task.progress, task.progress_message,
                     task.retry_count, task.max_retry_count, task.callback_url,
                     task.callback_type, task.callback_data, task.created_at,
                     task.updated_at, task.started_at, task.completed_at)
                session.expunge(task)
            
            return tasks
    
    def get_pending_retry_tasks(self, limit: int = 100):
        """获取待重试的任务列表"""
        with self.get_session() as session:
            tasks = session.query(self.AsyncTask).filter(
                self.AsyncTask.status == 'retrying'
            ).order_by(self.AsyncTask.id.desc()).limit(limit).all()
            
            # 预加载所有属性并从session中分离
            for task in tasks:
                _ = (task.id, task.task_id, task.task_type, task.status, task.data, task.result, 
                     task.error_message, task.progress, task.progress_message,
                     task.retry_count, task.max_retry_count, task.callback_url,
                     task.callback_type, task.callback_data, task.created_at,
                     task.updated_at, task.started_at, task.completed_at)
                session.expunge(task)
            
            return tasks
    
    def get_tasks_by_status(self, status: str, limit: int = 100, offset: int = 0):
        """根据状态获取任务列表（支持分页）"""
        with self.get_session() as session:
            tasks = session.query(self.AsyncTask).filter(
                self.AsyncTask.status == status
            ).order_by(self.AsyncTask.id.desc()).offset(offset).limit(limit).all()
            
            # 预加载所有属性并从session中分离
            for task in tasks:
                _ = (task.id, task.task_id, task.task_type, task.status, task.data, task.result, 
                     task.error_message, task.progress, task.progress_message,
                     task.retry_count, task.max_retry_count, task.callback_url,
                     task.callback_type, task.callback_data, task.created_at,
                     task.updated_at, task.started_at, task.completed_at)
                session.expunge(task)
            
            return tasks
    
    def get_recent_tasks(self, limit: int = 100):
        """获取最近的任务列表"""
        with self.get_session() as session:
            tasks = session.query(self.AsyncTask).order_by(
                self.AsyncTask.id.desc()
            ).limit(limit).all()
            
            # 预加载所有属性并从session中分离
            for task in tasks:
                _ = (task.id, task.task_id, task.task_type, task.status, task.data, task.result, 
                     task.error_message, task.progress, task.progress_message,
                     task.retry_count, task.max_retry_count, task.callback_url,
                     task.callback_type, task.callback_data, task.created_at,
                     task.updated_at, task.started_at, task.completed_at)
                session.expunge(task)
            
            return tasks

    def cleanup_old_tasks(self, days: int = 30) -> int:
        """清理旧任务记录"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with self.get_session() as session:
            count = session.query(self.AsyncTask).filter(
                self.AsyncTask.created_at < cutoff_date,
                self.AsyncTask.status.in_(['success', 'failed'])
            ).count()
            
            session.query(self.AsyncTask).filter(
                self.AsyncTask.created_at < cutoff_date,
                self.AsyncTask.status.in_(['success', 'failed'])
            ).delete()
            
            session.flush()
            logger.info(f"清理旧任务记录: {count} 条")
            return count
    
    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭") 