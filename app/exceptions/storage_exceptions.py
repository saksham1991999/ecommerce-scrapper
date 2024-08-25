class StorageException(Exception):
    """Exception raised for errors during data storage operations."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
