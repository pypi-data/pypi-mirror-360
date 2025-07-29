"""
配置管理模块

支持通过环境变量和.env文件进行配置
"""

import os
from typing import Optional, List
from pathlib import Path
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


class ConfigurationError(Exception):
    """配置错误异常"""
    pass


def find_env_files() -> List[str]:
    """
    动态查找.env文件位置
    
    Returns:
        可能的.env文件路径列表
    """
    possible_paths = []
    
    # 1. 当前工作目录
    cwd = Path.cwd()
    possible_paths.append(str(cwd / ".env"))
    
    # 2. 从当前工作目录向上查找，直到找到.env文件或到达根目录
    current_dir = cwd
    for _ in range(10):  # 限制查找深度，避免无限循环
        env_file = current_dir / ".env"
        if env_file.exists():
            possible_paths.append(str(env_file))
            break
        parent = current_dir.parent
        if parent == current_dir:  # 已到达根目录
            break
        current_dir = parent
    
    # 3. 检查常见的项目根目录标识文件，如果存在则在该目录查找.env
    common_root_indicators = [
        "requirements.txt", "setup.py", "pyproject.toml", 
        "package.json", ".git", "Dockerfile"
    ]
    
    current_dir = cwd
    for _ in range(10):
        for indicator in common_root_indicators:
            if (current_dir / indicator).exists():
                env_file = current_dir / ".env"
                possible_paths.append(str(env_file))
                break
        parent = current_dir.parent
        if parent == current_dir:
            break
        current_dir = parent
    
    # 去重并返回存在的文件
    unique_paths = []
    seen = set()
    for path in possible_paths:
        if path not in seen and Path(path).exists():
            unique_paths.append(path)
            seen.add(path)
    
    return unique_paths


class Settings(BaseSettings):
    """应用配置类"""
    
    # 使用SettingsConfigDict进行配置
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # RabbitMQ配置 - 必填项
    amqp_url: str = Field(env="GRID_ASYNC_TASK_AMQP_URL", description="AMQP连接URL，格式：amqp://username:password@host:port/vhost")
    rabbitmq_queue: str = Field(env="GRID_ASYNC_TASK_QUEUE", description="任务队列名称")
    rabbitmq_exchange: str = Field(default="", env="GRID_ASYNC_TASK_EXCHANGE", description="交换机名称")
    rabbitmq_routing_key: str = Field(default="", env="GRID_ASYNC_TASK_ROUTING_KEY", description="路由键")
    
    # MySQL配置 - 必填项
    mysql_url: str = Field(env="GRID_ASYNC_TASK_MYSQL_URL", description="MySQL连接URL，格式：mysql+pymysql://username:password@host:port/database?charset=utf8mb4")
    
    # 数据库表配置
    table_prefix: str = Field(default="", env="GRID_ASYNC_TASK_TABLE_PREFIX", description="数据库表前缀，避免表名冲突")
    table_name: str = Field(default="grid_async_tasks", env="GRID_ASYNC_TASK_TABLE_NAME", description="任务表名称（不含前缀）")
    
    # 连接池配置
    db_pool_size: int = Field(default=10, env="GRID_ASYNC_TASK_DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, env="GRID_ASYNC_TASK_DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, env="GRID_ASYNC_TASK_DB_POOL_TIMEOUT")
    db_pool_recycle: int = Field(default=3600, env="GRID_ASYNC_TASK_DB_POOL_RECYCLE")
    
    # 任务配置
    max_retry_count: int = Field(default=0, env="GRID_ASYNC_TASK_MAX_RETRY_COUNT")
    retry_delay: int = Field(default=1, env="GRID_ASYNC_TASK_RETRY_DELAY")
    task_timeout: int = Field(default=3600, env="GRID_ASYNC_TASK_TIMEOUT")
    prefetch_count: int = Field(default=1, env="GRID_ASYNC_TASK_PREFETCH_COUNT")
    
    # 日志配置
    log_level: str = Field(default="INFO", env="GRID_ASYNC_TASK_LOG_LEVEL")
    log_dir: str = Field(default="logs", env="GRID_ASYNC_TASK_LOG_DIR")
    log_max_size: str = Field(default="100 MB", env="GRID_ASYNC_TASK_LOG_MAX_SIZE")
    log_retention: str = Field(default="30 days", env="GRID_ASYNC_TASK_LOG_RETENTION")
    
    # 通知配置
    feishu_webhook_url: Optional[str] = Field(default=None, env="GRID_ASYNC_TASK_FEISHU_WEBHOOK_URL")
    progress_interval: int = Field(default=10, env="GRID_ASYNC_TASK_PROGRESS_INTERVAL")
    
    # 回调配置
    callback_timeout: int = Field(default=30, env="GRID_ASYNC_TASK_CALLBACK_TIMEOUT")
    callback_retry_count: int = Field(default=3, env="GRID_ASYNC_TASK_CALLBACK_RETRY_COUNT")
    
    # 健康检查配置
    health_check_interval: int = Field(default=60, env="GRID_ASYNC_TASK_HEALTH_CHECK_INTERVAL")
    
    # 空闲超时配置
    idle_timeout: int = Field(default=0, env="GRID_ASYNC_TASK_IDLE_TIMEOUT", description="空闲超时秒数，0表示永不退出")
    
    def __init__(self, **kwargs):
        # 动态加载.env文件
        env_files = find_env_files()
        for env_file in env_files:
            try:
                load_dotenv(env_file, override=False)  # 不覆盖已存在的环境变量
            except Exception as e:
                print(f"警告: 无法加载 {env_file}: {e}")
        

        # 修复pydantic-settings v2的环境变量读取问题
        # 当传递kwargs时，pydantic-settings不会自动从环境变量读取，需要手动构建配置
        env_config = {}
        
        # 必填字段 - 如果kwargs中没有提供且环境变量存在，则从环境变量获取
        required_env_mappings = {
            'amqp_url': 'GRID_ASYNC_TASK_AMQP_URL',
            'rabbitmq_queue': 'GRID_ASYNC_TASK_QUEUE', 
            'mysql_url': 'GRID_ASYNC_TASK_MYSQL_URL'
        }
        
        for field_name, env_name in required_env_mappings.items():
            if field_name not in kwargs:
                env_value = os.environ.get(env_name)
                if env_value:
                    env_config[field_name] = env_value
        
        # 可选字段 - 如果kwargs中没有提供且环境变量存在，则从环境变量获取
        optional_env_mappings = {
            'rabbitmq_exchange': 'GRID_ASYNC_TASK_EXCHANGE',
            'rabbitmq_routing_key': 'GRID_ASYNC_TASK_ROUTING_KEY',
            'table_prefix': 'GRID_ASYNC_TASK_TABLE_PREFIX',
            'table_name': 'GRID_ASYNC_TASK_TABLE_NAME',
            'db_pool_size': 'GRID_ASYNC_TASK_DB_POOL_SIZE',
            'db_max_overflow': 'GRID_ASYNC_TASK_DB_MAX_OVERFLOW',
            'db_pool_timeout': 'GRID_ASYNC_TASK_DB_POOL_TIMEOUT',
            'db_pool_recycle': 'GRID_ASYNC_TASK_DB_POOL_RECYCLE',
            'max_retry_count': 'GRID_ASYNC_TASK_MAX_RETRY_COUNT',
            'retry_delay': 'GRID_ASYNC_TASK_RETRY_DELAY',
            'task_timeout': 'GRID_ASYNC_TASK_TIMEOUT',
            'prefetch_count': 'GRID_ASYNC_TASK_PREFETCH_COUNT',
            'log_level': 'GRID_ASYNC_TASK_LOG_LEVEL',
            'log_dir': 'GRID_ASYNC_TASK_LOG_DIR',
            'log_max_size': 'GRID_ASYNC_TASK_LOG_MAX_SIZE',
            'log_retention': 'GRID_ASYNC_TASK_LOG_RETENTION',
            'feishu_webhook_url': 'GRID_ASYNC_TASK_FEISHU_WEBHOOK_URL',
            'progress_interval': 'GRID_ASYNC_TASK_PROGRESS_INTERVAL',
            'callback_timeout': 'GRID_ASYNC_TASK_CALLBACK_TIMEOUT',
            'callback_retry_count': 'GRID_ASYNC_TASK_CALLBACK_RETRY_COUNT',
            'health_check_interval': 'GRID_ASYNC_TASK_HEALTH_CHECK_INTERVAL',
            'idle_timeout': 'GRID_ASYNC_TASK_IDLE_TIMEOUT'
        }
        
        for field_name, env_name in optional_env_mappings.items():
            if field_name not in kwargs:
                env_value = os.environ.get(env_name)
                if env_value is not None:
                    # 对数字字段进行类型转换
                    if field_name in ['db_pool_size', 'db_max_overflow', 'db_pool_timeout', 'db_pool_recycle',
                                     'max_retry_count', 'retry_delay', 'task_timeout', 'prefetch_count',
                                     'progress_interval', 'callback_timeout', 'callback_retry_count',
                                     'health_check_interval', 'idle_timeout']:
                        try:
                            env_config[field_name] = int(env_value)
                        except ValueError:
                            # 如果转换失败，使用默认值
                            pass
                    else:
                        env_config[field_name] = env_value
        
        # 合并环境变量配置和传入的kwargs，kwargs优先级更高
        final_config = {**env_config, **kwargs}

        try:
            super().__init__(**final_config)
        except ValidationError as e:
            # 提供友好的配置错误提示
            missing_fields = []
            for error in e.errors():
                if error['type'] == 'missing':
                    field_name = error['loc'][0]
                    missing_fields.append(field_name)
            
            if missing_fields:
                # 显示查找到的.env文件信息
                env_info = f"已查找的.env文件: {env_files}" if env_files else "未找到.env文件"
                
                raise ConfigurationError(
                    f"Grid异步任务插件配置错误：缺少必需的环境变量配置\n"
                    f"缺少的配置项：{', '.join(missing_fields)}\n"
                    f"{env_info}\n\n"
                    f"请配置以下环境变量：\n"
                    f"• GRID_ASYNC_TASK_AMQP_URL (RabbitMQ连接地址)\n"
                    f"• GRID_ASYNC_TASK_QUEUE (任务队列名称)\n" 
                    f"• GRID_ASYNC_TASK_MYSQL_URL (MySQL连接地址)\n\n"
                    f"配置示例请参考项目目录下的 env_example.txt 文件\n"
                    f"详细说明请查看 https://gitee.com/shenzhen-grid/grid-async-task-plugin"
                ) from e
            else:
                # 其他验证错误，重新抛出
                raise
    
    @property
    def rabbitmq_url(self) -> str:
        """获取RabbitMQ连接URL（兼容旧接口）"""
        return self.amqp_url
    
    @property
    def full_table_name(self) -> str:
        """获取完整的表名（包含前缀）"""
        return f"{self.table_prefix}{self.table_name}"
    
    def get_log_config(self) -> dict:
        """获取日志配置"""
        return {
            "level": self.log_level,
            "format": ("{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | "
                      "task_id:{extra[task_id]!s:>8} | {message}"),
            "sink": os.path.join(self.log_dir, "task_{time:YYYY-MM-DD}.log"),
            "rotation": self.log_max_size,
            "retention": self.log_retention,
            "compression": "zip",
            "enqueue": True,
            "backtrace": True,
            "diagnose": True,
            "filter": self._log_filter
        }
    
    def _log_filter(self, record):
        """日志过滤器，为没有task_id的记录添加默认值"""
        if 'task_id' not in record['extra']:
            record['extra']['task_id'] = 'SYSTEM'
        return True


# 全局配置实例 - 延迟初始化
settings = None

def get_settings() -> Settings:
    """获取配置实例（延迟初始化）"""
    global settings
    if settings is None:
        settings = Settings()
    return settings

# 兼容性：保持旧的全局变量
def _init_global_settings():
    global settings
    try:
        settings = Settings()
    except Exception:
        # 如果配置不完整，保持None状态
        settings = None

# 尝试初始化全局settings，如果配置不完整则跳过
try:
    settings = Settings()
except ConfigurationError:
    # 配置错误时保持None，让错误在首次使用时抛出
    settings = None
except Exception:
    # 其他错误也保持None，避免模块导入失败
    settings = None 