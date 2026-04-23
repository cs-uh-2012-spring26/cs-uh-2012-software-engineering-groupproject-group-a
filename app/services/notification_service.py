from abc import ABC, abstractmethod

class NotificationStrategy(ABC):
    @abstractmethod
    def send(self, user_data, message_body):
        pass

class EmailNotification(NotificationStrategy):
    def send(self, user_data, message_body):
        pass

class TelegramNotification(NotificationStrategy):
    def send(self, user_data, message_body):
        pass

class NotificationEngine:
    def __init__(self, strategies=None):
        self._strategies = strategies or []

    def broadcast(self, user_data, message):
        results = []
        for strategy in self._strategies:
            success, error = strategy.send(user_data, message)
            results.append({"method": strategy.__class__.__name__, "success": success, "error": error})
        return results
