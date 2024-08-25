import logging
from logging.config import dictConfig


def setup_logging():
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "app.log",
                "formatter": "default",
                "level": "DEBUG",
            },
        },
        "root": {"level": "INFO", "handlers": ["console", "file"]},
    }
    dictConfig(logging_config)
