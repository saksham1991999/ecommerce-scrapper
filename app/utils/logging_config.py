import logging
from logging.config import dictConfig
from typing import Any, Dict


def setup_logging() -> None:
    """
    Set up logging configuration for the application.

    This function configures logging with both console and file handlers.
    Console handler is set to INFO level, while file handler is set to DEBUG level.
    Logs are formatted with timestamp, logger name, log level, and message.

    Returns:
        None
    """
    logging_config: Dict[str, Any] = {
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
                "level": logging.INFO,
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "app.log",
                "formatter": "default",
                "level": logging.DEBUG,
            },
        },
        "root": {"level": logging.INFO, "handlers": ["console", "file"]},
    }
    dictConfig(logging_config)
    logging.info("Logging setup completed.")
