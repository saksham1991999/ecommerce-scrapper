import asyncio
import logging
from functools import wraps
from typing import Any, Callable, TypeVar

from app.exceptions.scraper_exceptions import ScraperException

logger = logging.getLogger(__name__)

T = TypeVar('T')

def retry_async(max_attempts: int = 3, delay: int = 5) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    A decorator that retries an asynchronous function if it raises a ScraperException.

    Args:
        max_attempts (int): The maximum number of attempts to retry the function. Defaults to 3.
        delay (int): The delay in seconds between retry attempts. Defaults to 5.

    Returns:
        Callable: A decorated function that implements the retry logic.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except ScraperException as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Max retry attempts reached for {func.__name__}. Error: {str(e)}")
                        raise
                    await asyncio.sleep(delay)
                    logger.warning(f"Retrying {func.__name__} (attempt {attempt + 2}/{max_attempts})...")
            raise RuntimeError(f"Unexpected state reached in {func.__name__}")
        return wrapper
    return decorator
