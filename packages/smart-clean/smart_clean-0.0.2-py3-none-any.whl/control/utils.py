from typing import Dict, Union
from .managers import ResourceMonitor

def get_cleaning_statistics() -> Dict[str, Union[float, int]]:
    """获取清理统计信息"""
    monitor = ResourceMonitor()
    latest_stats = monitor.get_latest_stats()
    if not latest_stats:
        return {}
    
    return {
        "average_memory_improvement": monitor.get_average_memory_improvement(),
        "last_cleaning_duration": (
            latest_stats.end_time - latest_stats.start_time
        ).total_seconds() if latest_stats.end_time else 0,
        "success_rate": monitor.get_success_rate()
    } 