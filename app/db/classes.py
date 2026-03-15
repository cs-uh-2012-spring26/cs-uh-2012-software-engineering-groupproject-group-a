from app.db.utils import serialize_item, serialize_items
from app.db import DB
from bson import ObjectId
from bson.errors import InvalidId

CLASS_COLLECTION = "classes"

class ClassResource:

    def __init__(self):
        self.collection = DB.get_collection(CLASS_COLLECTION)

    def create_class(self, class_name: str, start_date: str, end_date: str, location: str, capacity: int, trainer_id: str):
        class_data = {
            "class_name": class_name,
            "start_date": start_date,
            "end_date": end_date,
            "location": location,
            "capacity": capacity,
            "trainer_id": trainer_id,
            "member_list": []
        }

        result = self.collection.insert_one(class_data)
        created = self.collection.find_one({"_id": result.inserted_id})
        return serialize_item(created)

    def get_all_classes(self):
        classes = list(self.collection.find()) # finding all classes
        return serialize_items(classes) # converts mongoDB objects to string so we can return as json

    def get_class_by_id(self, class_id: str):
        try:
            class_oid = ObjectId(class_id)
        except (InvalidId, TypeError):
            return "invalid_class_id"

        fitness_class = self.collection.find_one({"_id": class_oid})
        if not fitness_class:
            return "class_not_found"

        return serialize_item(fitness_class)
      
    def get_class_members(self, class_id: str, requesting_trainer_id: str | None = None): # get members of some specific class
        try:
            class_oid = ObjectId(class_id) # mongodb stores ids as objectid type, try to conver
        except (InvalidId, TypeError):
            return "invalid_class_id" # cannot convert to object id type

        fitness_class = self.collection.find_one({"_id": class_oid}) # look for the class in the database
        if not fitness_class:
            return "class_not_found"

        # check that the requesting trainer owns this class
        if requesting_trainer_id is not None and fitness_class.get("trainer_id") != requesting_trainer_id:
            return "not_your_class"

        return fitness_class.get("member_list", []) # extract member list from

    def book_class(self, username: str, class_id: str, user_id: str | None = None) -> str:
        try:
            class_oid = ObjectId(class_id)
        except (InvalidId, TypeError):
            return "invalid_class_id"

        # look for class
        fitness_class = self.collection.find_one({"_id": class_oid})
        
        if not fitness_class:
            return "class_not_found"

        if user_id is not None and fitness_class.get("trainer_id") == user_id:
            return "trainer_cannot_book"

        # get member list of the class
        member_list = fitness_class.get("member_list", [])
        # conflict
        if username in member_list:
            return "already_booked"

        # if not in list, push to it
        result = self.collection.update_one(
            {"_id": class_oid},
            {"$push": {"member_list": username}},
        )
        # check if update worked
        if result.modified_count == 1:
            return "booked"
        return "booking_failed"
