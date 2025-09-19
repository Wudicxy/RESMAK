import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .conf import settings as log_settings

def _safe_module_name(current_file: str) -> str:
    base = os.path.basename(current_file)
    return os.path.splitext(base)[0] or "app"

def get_logger(current_file: str) -> logging.Logger:
    """
    传入当前文件路径（一般用 __file__），返回专属 logger。
    日志路径：<LOG_DIR>/<module>.log
    """
    module_name = _safe_module_name(current_file)
    logger = logging.getLogger(f"app_logger.{module_name}")
    logger.setLevel(log_settings.LEVEL)

    if not logger.handlers:
        Path(log_settings.LOG_DIR).mkdir(parents=True, exist_ok=True)
        log_file = Path(log_settings.LOG_DIR) / f"{module_name}.log"

        file_handler = RotatingFileHandler(
            str(log_file),
            maxBytes=log_settings.MAX_BYTES,
            backupCount=log_settings.BACKUP_COUNT,
            encoding="utf-8",
        )
        formatter = logging.Formatter(log_settings.FORMAT)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        if log_settings.CONSOLE:
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            logger.addHandler(console)

        # 避免向 root logger 传播导致重复打印
        logger.propagate = False

    return logger
