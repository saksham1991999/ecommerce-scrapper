from app.notifications.base_notifier import BaseNotifier


class ConsoleNotifier(BaseNotifier):
    """
    ConsoleNotifier is a concrete implementation of the BaseNotifier class
    that sends notifications to the console.

    Inherits from BaseNotifier and implements the notify method to print
    messages to the console.
    """

    async def notify(self, message: str) -> None:
        """
        Sends a notification message to the console.

        Args:
            message (str): The message to be notified.

        Returns:
            None
        """
        print(f"Notification: {message}")
