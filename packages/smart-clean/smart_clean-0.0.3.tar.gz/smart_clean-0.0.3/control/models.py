from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import logging
import psutil

class CleanStrategy(Enum):
    GENTLE = auto()
    NORMAL = auto()
    AGGRESSIVE = auto()
    EXTREME = auto()

    def calculate_duration(self, base_duration: float) -> float:
        """根据策略计算实际清理时间"""
        multipliers = {
            CleanStrategy.GENTLE: 0.8,
            CleanStrategy.NORMAL: 1.0,
            CleanStrategy.AGGRESSIVE: 1.5,
            CleanStrategy.EXTREME: 2.0
        }
        return base_duration * multipliers[self]

    def log_strategy_info(self):
        """记录策略相关日志"""
        messages = {
            CleanStrategy.GENTLE: "使用温和清理策略，清理时间可能较长",
            CleanStrategy.NORMAL: "使用标准清理策略",
            CleanStrategy.AGGRESSIVE: "使用激进清理策略，可能影响系统性能",
            CleanStrategy.EXTREME: "使用极限清理策略，可能导致系统不稳定"
        }
        level = logging.INFO if self in (CleanStrategy.GENTLE, CleanStrategy.NORMAL) else logging.WARNING
        logging.log(level, messages[self])

@dataclass
class CleaningStats:
    """清理统计信息"""
    start_time: datetime
    end_time: Optional[datetime] = None
    memory_before: float = 0.0
    memory_after: float = 0.0
    threads_before: int = 0
    threads_after: int = 0
    attempts: int = 0
    success: bool = False

    def update_memory_before(self):
        """更新清理前内存使用情况"""
        self.memory_before = psutil.Process().memory_info().rss / 1024 / 1024

    def update_memory_after(self):
        """更新清理后内存使用情况"""
        self.memory_after = psutil.Process().memory_info().rss / 1024 / 1024

    def log_results(self):
        """记录清理结果"""
        memory_diff = self.memory_before - self.memory_after
        logging.info(f"清理完成，内存释放: {memory_diff:.2f}MB")
        logging.debug(f"线程数变化: {self.threads_before} -> {self.threads_after}") 