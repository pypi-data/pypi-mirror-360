import time
import logging
import select
from typing import Optional, Callable
from .models import CleanStrategy, CleaningStats
from .managers import ThreadManager, ResourceMonitor
from .exceptions import ResourceBusyError
from .decorators import with_retry
from .contexts import CleaningContext, timing_context

@with_retry()
def clean_(
    thread_num: int = 5,
    force: bool = False,
    timeout: Optional[float] = None,
    strategy: CleanStrategy = CleanStrategy.NORMAL,
    retry_count: int = 3,
    ignore_errors: bool = False,
    callback: Optional[Callable[[CleaningStats], None]] = None
) -> bool:
    """增强版线程资源清理函数
    
    在多线程操作后清理冗余的线程资源，确保系统资源得到及时释放。
    支持多种清理策略、错误处理机制和资源监控。
    
    Args:
        thread_num: 清理等待时间（秒），时间越长清理越彻底
        force: 是否强制清理所有资源，包括活跃线程
        timeout: 超时时间，None 表示使用默认超时时间
        strategy: 清理策略，可选 GENTLE/NORMAL/AGGRESSIVE/EXTREME
        retry_count: 清理失败时的重试次数
        ignore_errors: 是否忽略非致命错误
        callback: 清理完成后的回调函数
    
    Returns:
        bool: 清理操作是否成功完成
    """
    with CleaningContext(strategy, force) as ctx:
        with timing_context():
            thread_manager = ThreadManager()
            
            if not thread_manager.is_safe_to_clean() and not force:
                raise ResourceBusyError("当前线程状态不适合清理")

            # 获取初始状态
            thread_info = thread_manager.get_thread_info()
            ctx.stats.threads_before = thread_info["active"]
            ctx.stats.update_memory_before()

            # 策略处理
            thread_num = strategy.calculate_duration(thread_num)
            strategy.log_strategy_info()

            # 核心清理操作
            select.select([], [], [], thread_num)

            # 更新统计信息
            ctx.stats.update_memory_after()
            ctx.stats.threads_after = thread_manager.get_thread_info()["active"]
            ctx.stats.success = True

            if callback:
                callback(ctx.stats)

            ctx.stats.log_results()
            return True 