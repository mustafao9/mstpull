import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

class SensitiveDataFilter(logging.Filter):
    """Hassas bilgilerin (token, auth, password vb.) loglara yazılmasını engeller."""
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            msg = record.msg
            for sensitive_key in ["token=", "key=", "auth=", "password="]:
                if sensitive_key in msg.lower():
                    parts = msg.split(sensitive_key)
                    msg = parts[0] + sensitive_key + "[MASKED]"
            record.msg = msg
        return True

def setup_logging(log_dir: str, log_level: int = logging.INFO) -> logging.Logger:
    """Teknik günlükleme sistemini yapılandırır ve başlatır."""
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "mstpull.log")

    logger = logging.getLogger("MstPull")
    logger.setLevel(log_level)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(SensitiveDataFilter())

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def get_logger() -> logging.Logger:
    """Mevcut yapılandırılmış loglayıcıyı döndürür."""
    return logging.getLogger("MstPull")
