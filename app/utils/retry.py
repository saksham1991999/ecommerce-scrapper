import functools
import logging
import time
from typing import Any, Callable, TypeVar

from app.constants import MAX_RETRY_ATTEMPTS
from app.exceptions.scraper_exceptions import ScraperException

logger = logging.getLogger(__name__)

T = TypeVar('T')

def retry_decorator(max_attempts: int = MAX_RETRY_ATTEMPTS, delay: int = 1) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    A decorator that retries a function if it raises a ScraperException.

    Args:
        max_attempts (int): The maximum number of retry attempts. Defaults to MAX_RETRY_ATTEMPTS.
        delay (int): The initial delay between retries in seconds. Defaults to 1.

    Returns:
        Callable: A decorator function.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """
        The actual decorator function.

        Args:
            func (Callable[..., T]): The function to be decorated.

        Returns:
            Callable[..., T]: The wrapped function with retry logic.
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            """
            The wrapper function that implements the retry logic.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                T: The return value of the decorated function.

            Raises:
                ScraperException: If the maximum number of retry attempts is reached.
            """
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
                    time.sleep(delay * (2 ** (attempts - 1)))  # Exponential backoff
            raise RuntimeError(f"Unexpected state reached in {func.__name__}")  # This should never be reached
        return wrapper
    return decorator
