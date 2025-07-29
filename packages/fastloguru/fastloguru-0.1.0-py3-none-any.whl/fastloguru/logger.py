from loguru import logger as base_logger
import os
import sys
from pathlib import Path

# Keep track of added logger names to avoid re-adding sinks
_existing_loggers = set()

def get_logger(name: str, log_dir: str = "logs", prefix: str = "", tag: str = None):
    logger = base_logger.bind()

    # Ensure log directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    file_base = f"{prefix + '_' if prefix else ''}{name}"
    plain_log = os.path.join(log_dir, f"{file_base}.log")

    # Avoid adding sinks multiple times
    if file_base not in _existing_loggers:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level:<8}</level> | "
            "{name}:{function}:{line} - <level>{message}</level>"
        )
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | "
            "{name}:{function}:{line} - {message}"
        )

        logger.add(sys.stdout, level="INFO", format=log_format, colorize=True)

        logger.add(plain_log, level="DEBUG", rotation="100 MB", retention="90 days",
                   format=file_format, colorize=False)


        _existing_loggers.add(file_base)

    if tag:
        return logger.bind(tag=tag)
    return logger
