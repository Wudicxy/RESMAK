from dataclasses import dataclass
from pathlib import Path
from django.conf import settings as dj_settings
import logging

@dataclass(frozen=True)
class _Settings:
    # 日志根目录：默认 BASE_DIR/logs
    LOG_DIR: Path = Path(getattr(dj_settings, "BASE_DIR", ".")) / getattr(dj_settings, "APP_LOGGER_DIR_NAME", "logs")
    # 默认级别
    LEVEL: int = getattr(dj_settings, "APP_LOGGER_LEVEL", logging.ERROR)
    # 单文件最大尺寸（字节）
    MAX_BYTES: int = getattr(dj_settings, "APP_LOGGER_MAX_BYTES", 5 * 1024 * 1024)
    # 轮转备份数量
    BACKUP_COUNT: int = getattr(dj_settings, "APP_LOGGER_BACKUP_COUNT", 5)
    # 日志格式
    FORMAT: str = getattr(
        dj_settings,
        "APP_LOGGER_FORMAT",
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    # 是否在控制台也输出（开发期可开）
    CONSOLE: bool = getattr(dj_settings, "APP_LOGGER_CONSOLE", False)

settings = _Settings()
