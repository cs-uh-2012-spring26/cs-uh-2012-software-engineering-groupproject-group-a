from abc import ABC, abstractmethod
from app.services.email_service import EmailService


def _resolve_member_email(user_data):
    if not isinstance(user_data, dict):
        return None
    return user_data.get("email")

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
        return False, "telegram strategy not implemented"


class NotificationEngine:
    def __init__(self, strategies=None):
        self._strategies = strategies or []

    def broadcast(self, user_data, message):
        results = []
        for strategy in self._strategies:
            success, error = strategy.send(user_data, message)
            results.append({"method": strategy.__class__.__name__, "success": success, "error": error})
        return results


def send_email_reminders(members, class_name, user_resource, strategies=None):
    active_strategies = strategies if isinstance(strategies, list) and len(strategies) > 0 else [EmailNotification()]
    engine = NotificationEngine(active_strategies)

    sent = 0
    failed = 0
    errors = []

    for member in members:
        member_user = user_resource.get_user(member)
        member_email = _resolve_member_email(member_user)
        results = engine.broadcast(member_user, class_name)

        if len(results) == 0:
            failed += 1
            errors.append(f"{member}: no notification strategies configured")
            continue

        success = results[0].get("success")
        error = results[0].get("error")

        if success:
            sent += 1
            continue

        failed += 1
        if error == "missing email":
            errors.append(f"{member}: missing email")
            continue

        if isinstance(error, str) and len(error) > 0 and isinstance(member_email, str) and len(member_email) > 0:
            errors.append(f"{member_email}: {error}")

    message = (
        f"All {sent} reminder emails sent successfully"
        if failed == 0
        else "Reminder process completed with some failed emails"
    )

    response_payload = {
        "message": message,
        "sent": sent,
        "failed": failed,
    }

    if len(errors) > 0:
        response_payload["errors"] = errors

    return response_payload
