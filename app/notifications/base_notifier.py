from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    """
    Abstract base class for notification services.

    This class defines the interface for sending notifications.
    Concrete implementations should provide the specific logic for
    notifying users through various channels (e.g., email, SMS, etc.).

    Methods:
        notify(message: str) -> None: Sends a notification with the given message.
    """

    @abstractmethod
    async def notify(self, message: str) -> None:
        """
        Sends a notification with the specified message.

        Args:
            message (str): The message to be sent in the notification.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        pass
