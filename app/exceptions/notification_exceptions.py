class NotificationException(Exception):
    """Exception raised for errors during notification sending."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
