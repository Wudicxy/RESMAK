from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
import traceback
from .logger import get_logger

class ExceptionLoggingMiddleware(MiddlewareMixin):
    """
    自动记录未处理异常：请求方法、路径、用户、视图文件等信息。
    """
    def process_exception(self, request: HttpRequest, exception):
        logger = get_logger(__file__)
        user_repr = getattr(request, "user", None)
        user_str = f"{user_repr}" if user_repr else "Anonymous"
        logger.error(
            f"{__file__} 文件 报错: {exception} | "
            f"method={request.method} path={request.path} user={user_str}\n"
            f"{traceback.format_exc()}"
        )
        # 返回 None 让 Django 继续原有异常处理流程（如 debug 页面或自定义 handler）
        return None
