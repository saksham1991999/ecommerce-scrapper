class AuthenticationException(Exception):
    """Exception raised for authentication errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
