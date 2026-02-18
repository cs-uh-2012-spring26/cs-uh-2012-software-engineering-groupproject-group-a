from app.db.utils import serialize_item, serialize_items
from app.db import DB
import bcrypt
from app.db import TRAINERCODES

USER_COLLECTION = "users"

FULL_NAME = "full_name"
USERNAME = "username"
PASSWORD_HASH = "password_hash"
ROLE = "role"

class UserResource:

    def __init__(self):
        self.collection = DB.get_collection(USER_COLLECTION)

    def get_user(self, username: str):
        user = self.collection.find_one({USERNAME: username})
        return serialize_item(user)
    
    def create_user(self, full_name: str, username: str, password: str, trainer_code: str | None = None):
        existing_user = self.get_user(username)
        if existing_user:
            return -1
        
        # hash password and check trainer code
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user_data = {
            FULL_NAME: full_name,
            USERNAME: username,
            ROLE: "trainer" if trainer_code in TRAINERCODES else "member",
            "password_hash": password_hash
        }

        result = self.collection.insert_one(user_data)
        return result.inserted_id
    
    def check_password(self, username: str, password: str) -> bool:
        user = self.collection.find_one({USERNAME: username})
        if not user:
            return False
        
        return bcrypt.checkpw(password.encode('utf-8'), user.get("password_hash"))
    
    
# User Model
    # _id 
    # username
    # full_name
    # role 
    # password_hash
