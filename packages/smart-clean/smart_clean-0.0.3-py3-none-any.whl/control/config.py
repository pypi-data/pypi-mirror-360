import logging
from typing import Dict, Any

# 默认配置
DEFAULT_CONFIG: Dict[str, Any] = {
    "default_duration": 5.0,
    "max_retries": 3,
    "retry_delay": 1.0,
    "log_level": logging.INFO,
    "enable_memory_tracking": True,
    "enable_thread_tracking": True,
}

# 日志格式配置
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' 