import logging
from typing import List

from app.exceptions.notification_exceptions import NotificationException
from app.notifications.base_notifier import BaseNotifier

logger = logging.getLogger(__name__)

class NotificationService:
    """
    A service class for managing and sending notifications through multiple notifiers.
    """

    def __init__(self, notifiers: List[BaseNotifier]):
        """
        Initialize the NotificationService with a list of notifiers.

        Args:
            notifiers (List[BaseNotifier]): A list of notifier objects implementing the BaseNotifier interface.
        """
        self.notifiers: List[BaseNotifier] = notifiers

    async def notify_all(self, message: str) -> None:
        """
        Send a notification message through all registered notifiers.

        Args:
            message (str): The message to be sent as a notification.

        Raises:
            NotificationException: If there's an error sending notifications through any notifier.

        Returns:
            None
        """
        for notifier in self.notifiers:
            try:
                await notifier.notify(message)
                logger.info(f"Notification sent successfully through {notifier.__class__.__name__}")
            except Exception as e:
                error_message = f"Error sending notification through {notifier.__class__.__name__}: {str(e)}"
                logger.error(error_message)
                raise NotificationException(error_message) from e
