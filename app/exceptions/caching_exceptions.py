class CacheException(Exception):
    """Exception raised for caching-related errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
