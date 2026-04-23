import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

class TelegramService():
    @staticmethod
    def get_user_chat_id(user_token: str):
        resp = requests.get(
            f"{TELEGRAM_API}/getUpdates",
            params={"timeout": 1},
            timeout=10,
            )
        resp.raise_for_status()

        data = resp.json()
        print(data)
        if not data.get("ok"):
            return None

        for update in data.get("result", []):
            message = update.get("message") or {}
            text = (message.get("text") or "").strip()

            if text == f"/start {user_token}":
                chat = message.get("chat") or {}
                chat_id = chat.get("id")
                if chat_id is not None:
                    return str(chat_id)

        return None