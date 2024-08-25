from typing import List
from app.notifications.base_notifier import BaseNotifier

class NotificationService:
    def __init__(self, notifiers: List[BaseNotifier]):
        self.notifiers = notifiers

    async def notify_all(self, message: str) -> None:
        for notifier in self.notifiers:
            await notifier.notify(message)