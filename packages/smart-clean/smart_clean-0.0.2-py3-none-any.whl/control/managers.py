import threading
import queue
from typing import Dict, List, Optional
import psutil
from .models import CleaningStats

class ThreadManager:
    """线程管理器"""
    @staticmethod
    def get_thread_info() -> Dict[str, int]:
        return {
            "active": threading.active_count(),
            "total_system": len(threading.enumerate()),
            "daemon": sum(1 for t in threading.enumerate() if t.daemon),
            "main_thread_id": threading.main_thread().ident or 0
        }

    @staticmethod
    def is_safe_to_clean() -> bool:
        return threading.active_count() > 1

    @staticmethod
    def get_thread_names() -> List[str]:
        return [t.name for t in threading.enumerate()]

class ResourceMonitor:
    """资源监控器"""
    def __init__(self):
        self._stats_queue = queue.Queue()
        self._history: List[CleaningStats] = []

    def record_stats(self, stats: CleaningStats):
        self._stats_queue.put(stats)
        self._history.append(stats)

    def get_latest_stats(self) -> Optional[CleaningStats]:
        return self._history[-1] if self._history else None

    def get_average_memory_improvement(self) -> float:
        if not self._history:
            return 0.0
        improvements = [(s.memory_before - s.memory_after) 
                       for s in self._history if s.success]
        return sum(improvements) / len(improvements) if improvements else 0.0

    def get_success_rate(self) -> float:
        if not self._history:
            return 0.0
        return len([s for s in self._history if s.success]) / len(self._history) 