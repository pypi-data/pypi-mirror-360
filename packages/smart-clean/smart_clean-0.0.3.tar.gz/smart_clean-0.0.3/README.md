# Thread Cleaning Utility

高级线程资源清理工具，提供多种清理策略和完整的资源监控功能。

## 特性

- 多种清理策略（温和/正常/激进/极限）
- 完整的资源监控
- 线程安全
- 异常处理和重试机制
- 详细的日志记录

## 使用方法

```python
from control import clean_, CleanStrategy

# 基本使用
clean_(duration=5.0)

# 使用激进策略
clean_(duration=5.0, strategy=CleanStrategy.AGGRESSIVE)

# 强制清理
clean_(duration=5.0, force=True)
```

## 配置

可以通过 `config.py` 修改默认配置：

- default_duration: 默认清理时间
- max_retries: 最大重试次数
- retry_delay: 重试延迟
- log_level: 日志级别
- enable_memory_tracking: 是否启用内存跟踪
- enable_thread_tracking: 是否启用线程跟踪

## 许可证

MIT License 