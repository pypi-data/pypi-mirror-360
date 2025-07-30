import time
import logging
from typing import Callable, TypeVar
from functools import wraps

T = TypeVar('T')

def with_retry(max_retries: int = 3, delay: float = 1.0) -> Callable:
    """重试装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logging.error(f"尝试 {attempt + 1}/{max_retries} 失败: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(delay)
            raise last_exception or RuntimeError("未知错误")
        return wrapper
    return decorator 