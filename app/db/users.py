from app.db.utils import serialize_item
from app.db import DB
import bcrypt
import secrets
from app.db import TRAINERCODES, TELEGRAM_BOT_USERNAME

USER_COLLECTION = "users"

FULL_NAME = "full_name"
USERNAME = "username"
EMAIL = "email"
PASSWORD_HASH = "password_hash"
ROLE = "role"
TELEGRAM_CONNECT_TOKEN = "telegram_connect_token"
TELEGRAM_CHAT_ID = "telegram_chat_id"

def make_connect_token():
    return "connect_" + secrets.token_urlsafe(18).replace("-", "_")[:24]

class UserResource:

    def __init__(self):
        self.collection = DB.get_collection(USER_COLLECTION)

    def get_user(self, username: str):
        user = self.collection.find_one({USERNAME: username})
        return serialize_item(user)

    def get_user_by_email(self, email: str):
        user = self.collection.find_one({EMAIL: email})
        return serialize_item(user)
    
    def get_user_telegram_token(self, username: str):
        user = self.get_user(username=username)
        if not isinstance(user, dict):
            return None
        return user.get(TELEGRAM_CONNECT_TOKEN)

    def get_user_telegram_chat_id(self, username: str):
        user = self.get_user(username=username)
        if not isinstance(user, dict):
            return None
        return user.get(TELEGRAM_CHAT_ID)

    def has_user_telegram_chat_id(self, username: str) -> bool:
        chat_id = self.get_user_telegram_chat_id(username)
        return isinstance(chat_id, str) and len(chat_id.strip()) > 0
        
    
    def create_user(self, full_name: str, username: str, email: str, password: str, trainer_code: str | None = None):
        
        # hash password and check trainer code
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # make connect token and link for telegram sync
        telegram_connect_token = make_connect_token()
        telegram_link = f"https://t.me/{TELEGRAM_BOT_USERNAME}?start={telegram_connect_token}"

        user_data = {
            FULL_NAME: full_name,
            USERNAME: username,
            EMAIL: email,
            ROLE: "trainer" if trainer_code in TRAINERCODES else "member",
            PASSWORD_HASH: password_hash,
            TELEGRAM_CONNECT_TOKEN: telegram_connect_token
        }

        result = self.collection.insert_one(user_data)
        return result.inserted_id, telegram_link
    
    def append_telegram_chat_id(self, username: str, telegram_chat_id: str):
        result = self.collection.update_one(
            {USERNAME: username},
            {"$set": {TELEGRAM_CHAT_ID: telegram_chat_id}},
        )
        return result.matched_count == 1

    def remove_telegram_connect_token(self, username: str):
        result = self.collection.update_one(
            {USERNAME: username},
            {"$unset": {TELEGRAM_CONNECT_TOKEN: ""}},
        )
        return result.matched_count == 1
    
    def check_password(self, username: str, password: str) -> bool:
        user = self.collection.find_one({USERNAME: username})
        if not user:
            return False
        
        return bcrypt.checkpw(password.encode('utf-8'), user.get("password_hash"))
    
    
# User Model
    # _id 
    # username
    # email
    # telegram_connect_token
    # telegram_chat_id (to be appended)
    # full_name
    # role 
    # password_hash
