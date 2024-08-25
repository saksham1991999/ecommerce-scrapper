from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    @abstractmethod
    async def notify(self, message: str) -> None:
        pass