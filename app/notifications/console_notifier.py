from app.notifications.base_notifier import BaseNotifier

class ConsoleNotifier(BaseNotifier):
    async def notify(self, message: str) -> None:
        print(f"Notification: {message}")