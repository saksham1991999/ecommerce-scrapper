import asyncio
from functools import wraps
from typing import Callable, Any
from app.exceptions.scraper_exceptions import ScraperException

def retry_async(max_attempts: int = 3, delay: int = 5):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except ScraperException as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(delay)
                    print(f"Retrying {func.__name__} (attempt {attempt + 2}/{max_attempts})...")
            return None
        return wrapper
    return decorator