from abc import ABC, abstractmethod
from app.services.email_service import EmailService
from app.services.telegram_service import TelegramService
from app.db.users import UserResource

def _resolve_member_email(user_data):
    if not isinstance(user_data, dict):
        return None
    return user_data.get("email")

def _resolve_member_telegram_chat_id(user_data):
    if not isinstance(user_data, dict):
        return None
    return user_data.get("telegram_chat_id")

# interface 
class NotificationStrategy(ABC):
    @abstractmethod
    def send(self, user_data, message_body) -> tuple[bool, str | None]:
        pass

class EmailNotification(NotificationStrategy):
    def send(self, user_data, message_body) -> tuple[bool, str | None]:
        member_email = _resolve_member_email(user_data)
        if not isinstance(member_email, str) or len(member_email.strip()) == 0:
            return False, "missing email"

        return EmailService.send_class_reminder(member_email, message_body)

class TelegramNotification(NotificationStrategy):
    def send(self, user_data, message_body) -> tuple[bool, str | None]:
        user_telegram_chat_id = _resolve_member_telegram_chat_id(user_data)
        if not isinstance(user_telegram_chat_id, str) or len(user_telegram_chat_id.strip()) == 0:
            return False, "missing telegram chat id"
        message_body = f"Reminder: Your class '{message_body}' is coming up soon!"
        return TelegramService.send_telegram_message(user_telegram_chat_id, message_body)

class NotificationEngine:
    def __init__(self, strategies=None):
        self._strategies = strategies or []

    def broadcast(self, user_data, message):
        results = [] # array of tuples for each strategy (True|False, ErrorMsg|None)
        for strategy in self._strategies:
            success, error = strategy.send(user_data, message)
            results.append({"method": strategy.__class__.__name__, "success": success, "error": error})
        return results


def send_reminders(members, class_name, user_resource, strategies=None):
    active_strategies = strategies if isinstance(strategies, list) and len(strategies) > 0 else [EmailNotification()]
    engine = NotificationEngine(active_strategies)

    strategy_names = [strategy.__class__.__name__ for strategy in active_strategies]
    strategy_results = {}

    for member in members:
        member_user = user_resource.get_user(member)
        results = engine.broadcast(member_user, class_name)

        for result in results:
            strategy_name = result.get("method")
            result_key = f"{strategy_name}_results"
            if result_key not in strategy_results:
                strategy_results[result_key] = {"success": 0, "fail": 0}

            if result.get("success") is True:
                strategy_results[result_key]["success"] += 1
            else:
                strategy_results[result_key]["fail"] += 1

    response_payload = {"notification_strategies": strategy_names, **strategy_results}

    return response_payload
