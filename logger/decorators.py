import functools
import traceback
from typing import Callable, Any, Optional
from .logger import get_logger

def log_exceptions(logger=None, re_raise=True, prefix: Optional[str]=None):
    """
    装饰器：自动捕获并记录函数内异常。
    - logger: 传入既有 logger；不传则基于调用处模块自动创建。
    - re_raise: 记录后是否继续抛出异常（默认 True，保持原有行为）。
    - prefix: 自定义前缀，如 "用户下单"；最终日志形如："{prefix} xxx文件 xxx 报错: <异常>"
    """
    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or get_logger(func.__code__.co_filename)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                file_path = func.__code__.co_filename
                msg_prefix = f"{prefix} " if prefix else ""
                _logger.error(f"{msg_prefix}{file_path} 文件 报错: {e}\n{traceback.format_exc()}")
                if re_raise:
                    raise
                return None
        return wrapper
    return decorator
