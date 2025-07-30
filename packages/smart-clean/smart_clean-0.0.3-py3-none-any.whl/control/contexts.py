import time
import logging
from contextlib import contextmanager
from datetime import datetime
from .models import CleanStrategy, CleaningStats
from .managers import ResourceMonitor

class CleaningContext:
    """清理上下文管理器"""
    def __init__(self, strategy: CleanStrategy, force: bool):
        self.strategy = strategy
        self.force = force
        self.stats = CleaningStats(start_time=datetime.now())
        self.monitor = ResourceMonitor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stats.end_time = datetime.now()
        self.monitor.record_stats(self.stats)

@contextmanager
def timing_context():
    """计时上下文管理器"""
    start_time = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start_time
        logging.debug(f"操作耗时: {duration:.2f}秒") 