from abc import ABC, abstractmethod


class ISender(ABC):
    """
    Interface for notification services.
    """

    @abstractmethod
    def send(self, message: str) -> None:
        """
        Отправить сообщение.
        """
        pass

