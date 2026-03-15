import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

class EmailService:
    @staticmethod
    def _get_sendgrid_client() -> SendGridAPIClient:
        api_key = os.environ.get("SENDGRID_API_KEY")
        if not api_key:
            raise ValueError("Missing SendGrid API key")
        return SendGridAPIClient(api_key)

    @staticmethod
    def _get_sender_email() -> str:
        sender = os.environ.get("SENDGRID_FROM_EMAIL")
        if not isinstance(sender, str) or len(sender.strip()) == 0:
            raise ValueError("Missing SENDGRID_FROM_EMAIL")
        return sender.strip()

    @staticmethod
    def build_reminder_message(recipient_email: str, class_name: str) -> Mail:
        from_email = EmailService._get_sender_email()
        normalized_recipient = recipient_email.strip().lower()
        return Mail(
            from_email=from_email,
            to_emails=normalized_recipient,
            subject="Fitness Class Booking Reminder!",
            html_content=(
                f"This is a reminder about your upcoming fitness class: {class_name}."
            ),
        )

    @staticmethod
    def send_class_reminder(recipient_email: str, class_name: str) -> tuple[bool, str | None]:
        try:
            client = EmailService._get_sendgrid_client()
            message = EmailService.build_reminder_message(recipient_email, class_name)
            response = client.send(message)
            status = int(response.status_code)
            if 200 <= status < 300:
                return True, None
            body = response.body.decode("utf-8", errors="ignore") if isinstance(response.body, (bytes, bytearray)) else str(response.body)
            return False, f"SendGrid returned status {status}: {body}"
        except Exception as error:
            return False, str(error)