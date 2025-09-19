from .logger import get_logger
from .decorators import log_exceptions

__all__ = ["get_logger", "log_exceptions"]
default_app_config = "app_logger.apps.AppLoggerConfig"