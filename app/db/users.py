from app.db.utils import serialize_item, serialize_items
from app.db import DB

USER_COLLECTION = "users"

USERNAME = "username"
ROLE = "role"

class UserResource:

    def __init__(self):
        self.collection = DB.get_collection(USER_COLLECTION)

    def get_user(self, username: str):
        user = self.collection.find_one({USERNAME: username})
        return serialize_item(user)
    
# User Model
    # _id 
    # username
    # full_name
    # role 
    # password_hash
