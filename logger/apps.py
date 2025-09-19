from django.apps import AppConfig


class LoggerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "logger"

    def ready(self):
        # 确保日志目录存在
        try:
            from .conf import settings as log_settings
            Path(log_settings.LOG_DIR).mkdir(parents=True, exist_ok=True)
        except Exception:
            # 避免启动阶段因日志目录创建失败而阻塞
            pass