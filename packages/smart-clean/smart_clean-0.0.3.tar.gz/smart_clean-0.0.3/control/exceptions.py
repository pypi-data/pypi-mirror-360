class CleaningError(Exception):
    """清理过程中的基础异常类"""
    pass

class ResourceBusyError(CleaningError):
    """资源占用异常"""
    pass

class TimeoutError(CleaningError):
    """清理超时异常"""
    pass

class ConfigurationError(CleaningError):
    """配置错误异常"""
    pass 