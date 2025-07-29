import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from rich.logging import RichHandler

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def simple_logger_setup(
    level="debug",
    name=None,
    use_rich=False,
    log_to_file=False,
    file_path="app.log",
    json_output=False,
    max_bytes=1_000_000,
    backup_count=3,
):
    logger = logging.getLogger(name or __name__)
    if logger.hasHandlers():
        return logger

    env_level = os.getenv("LOG_LEVEL", level).lower()
    logger.setLevel(LEVELS.get(env_level, logging.DEBUG))

    formatter = None
    handler = None

    if use_rich:
        handler = RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=True,
            show_level=True,
            show_path=True,
        )
        formatter = logging.Formatter("%(message)s")

    elif json_output:
        handler = logging.StreamHandler(sys.stdout)
        formatter = JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%S")
    else:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if log_to_file:
        file_handler = RotatingFileHandler(
            file_path, maxBytes=max_bytes, backupCount=backup_count
        )
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    logger.debug("Logger initialized with level '%s'", env_level.upper())
    return logger
