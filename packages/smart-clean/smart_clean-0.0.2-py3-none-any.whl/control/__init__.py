import time
import threading
import logging
import psutil
import warnings
from typing import Optional, Dict, List
from enum import Enum
from datetime import datetime

from .core import clean_
from .managers import ThreadManager, ResourceMonitor
from .models import CleanStrategy, CleaningStats
from .exceptions import CleaningError, ResourceBusyError, TimeoutError

__version__ = "1.0.0"
__all__ = [
    'clean_',
    'ThreadManager',
    'ResourceMonitor',
    'CleanStrategy',
    'CleaningStats',
    'CleaningError',
    'ResourceBusyError',
    'TimeoutError'
]

class CleanStrategy(Enum):
    GENTLE = "gentle"
    NORMAL = "normal"
    AGGRESSIVE = "aggressive"

def _get_thread_info() -> Dict[str, int]:
    return {
        "active": threading.active_count(),
        "total_system": len(threading.enumerate()),
        "daemon": sum(1 for t in threading.enumerate() if t.daemon)
    }

def clean_(
    duration: float = 5.0,
    force: bool = False,
    timeout: Optional[float] = None,
    strategy: CleanStrategy = CleanStrategy.NORMAL,
    retry_count: int = 3,
    ignore_errors: bool = False
) -> bool:
    """线程资源清理函数
    
    在多线程操作后清理冗余的线程资源，确保系统资源得到及时释放。
    等待指定时间以确保所有线程相关资源完全释放。
    支持多种清理策略和错误处理机制。
    
    Args:
        duration: 清理等待时间（秒），时间越长清理越彻底
        force: 是否强制清理所有资源，包括活跃线程
        timeout: 超时时间，None 表示使用默认超时时间
        strategy: 清理策略，可选 GENTLE/NORMAL/AGGRESSIVE
        retry_count: 清理失败时的重试次数
        ignore_errors: 是否忽略非致命错误
    
    Returns:
        bool: 清理操作是否成功完成
    
    Raises:
        CleaningError: 清理过程中发生严重错误
    """
    start_time = datetime.now()
    attempt = 0
    
    while attempt < retry_count:
        try:
            # 记录清理开始状态
            logging.debug(f"开始第 {attempt + 1} 次清理尝试")
            logging.debug(f"清理策略: {strategy.value}, 等待时间: {duration}秒")
            
            # 获取系统状态
            thread_info = _get_thread_info()
            memory_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            logging.info(f"当前线程状态: {thread_info}")
            logging.info(f"当前内存使用: {memory_before:.2f}MB")
            
            if thread_info['active'] < 2 and not force:
                warnings.warn("当前活跃线程数较少，清理操作可能无必要", RuntimeWarning)
            
            # 根据策略执行不同的清理操作
            if strategy == CleanStrategy.AGGRESSIVE:
                logging.warning("使用激进清理策略，可能影响系统性能")
            elif strategy == CleanStrategy.GENTLE:
                logging.info("使用温和清理策略，清理时间可能较长")
            
            if force:
                logging.warning("正在执行强制清理操作...")
            time.sleep(duration)
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024
            memory_diff = memory_before - memory_after
            
            logging.info(f"清理完成，内存变化: {memory_diff:.2f}MB")
            logging.debug(f"清理耗时: {(datetime.now() - start_time).total_seconds():.2f}秒")
            
            return True
            
        except Exception as e:
            attempt += 1
            logging.error(f"清理过程发生错误: {str(e)}")
            if attempt < retry_count:
                logging.info(f"将在 1 秒后进行第 {attempt + 1} 次重试")
                time.sleep(1)
            else:
                if not ignore_errors:
                    raise CleaningError(f"清理失败，已重试 {retry_count} 次") from e
                return False
