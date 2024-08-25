import functools
import time
import logging
from typing import Callable, Any
from app.exceptions.scraper_exceptions import ScraperException
from app.constants import MAX_RETRY_ATTEMPTS

logger = logging.getLogger(__name__)

def retry_decorator(max_attempts: int = MAX_RETRY_ATTEMPTS, delay: int = 1) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except ScraperException as e:
                    attempts += 1
                    if attempts == max_attempts:
                        logger.error(f"Max retry attempts reached. Function: {func.__name__}, Error: {str(e)}")
                        raise
                    logger.warning(f"Retry attempt {attempts} for function: {func.__name__}, Error: {str(e)}")
                    time.sleep(delay * attempts)  # Exponential backoff
            return None
        return wrapper
    return decorator
