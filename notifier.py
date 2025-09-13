from abc import ABC, abstractmethod

class Notifier(ABC):
    """Abstract base class for sending notifications."""

    @abstractmethod
    def send(self, to_phone_number: str, message: str) -> None:
        """Send a notification to the given phone number."""
        raise NotImplementedError
