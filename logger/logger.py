import os
import logging
from logging.handlers import RotatingFileHandler

def get_logger(current_file: str):
    # 取文件名
    file_name = os.path.basename(current_file).replace(".py", "")

    # 日志目录（项目根目录/logs）
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 日志文件路径
    log_file = os.path.join(log_dir, f"{file_name}.log")

    # 创建 logger
    logger = logging.getLogger(file_name)
    logger.setLevel(logging.ERROR)  # 只记录错误及以上级别

    # 避免重复添加 handler
    if not logger.handlers:
        handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
