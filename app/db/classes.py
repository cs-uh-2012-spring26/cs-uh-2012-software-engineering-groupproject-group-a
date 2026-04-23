from app.apis import MSG
from app.db.utils import serialize_item, serialize_items
from app.db import DB
from bson import ObjectId
from bson.errors import InvalidId
from enum import Enum
from http import HTTPStatus
import uuid
from datetime import datetime, timezone, timedelta

CLASS_COLLECTION = "classes"
class ClassResult(Enum):
    SUCCESS = "booked"
    INVALID_ID = "invalid_class_id"
    NOT_FOUND = "class_not_found"
    TRAINER_OWNED = "trainer_cannot_book"
    ALREADY_BOOKED = "already_booked"
    CLASS_FULL = "class_full"
    FAIL = "booking_failed"
    NOT_OWNED = "not_your_class"

    def resolves(self):
        mapping = {
            ClassResult.SUCCESS: ({MSG: "Class booked successfully"}, HTTPStatus.OK),
            ClassResult.INVALID_ID: ({MSG: "Invalid class id"}, HTTPStatus.UNPROCESSABLE_ENTITY),
            ClassResult.NOT_FOUND: ({MSG: "Class not found"}, HTTPStatus.NOT_FOUND),
            ClassResult.TRAINER_OWNED: ({MSG: "Trainer cannot book their own class"}, HTTPStatus.FORBIDDEN),
            ClassResult.ALREADY_BOOKED: ({MSG: "User already booked this class"}, HTTPStatus.CONFLICT),
            ClassResult.CLASS_FULL: ({MSG: "Class is full"}, HTTPStatus.FORBIDDEN),
            ClassResult.FAIL: ({MSG: "Failed to book class"}, HTTPStatus.BAD_REQUEST),
            ClassResult.NOT_OWNED: ({MSG: "Only the trainer of this class can view its members"}, HTTPStatus.FORBIDDEN)
        }
        return mapping.get(self, ({MSG: "Unknown error"}, HTTPStatus.BAD_REQUEST)) 
                                      
class ClassResource:

    def __init__(self):
        self.collection = DB.get_collection(CLASS_COLLECTION)

    def create_class(self, class_name: str, start_date: str, end_date: str, location: str, capacity: int, trainer_id: str, recurrence_group_id :str | None = None):
        class_data = {
            "class_name": class_name,
            "start_date": start_date,
            "end_date": end_date,
            "location": location,
            "capacity": capacity,
            "trainer_id": trainer_id,
            "member_list": [],   
        }
        # reccuring classes are group by reccurence id
        if recurrence_group_id is not None:
            class_data["recurrence_group_id"] = recurrence_group_id

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
            return ClassResult.INVALID_ID

        fitness_class = self.collection.find_one({"_id": class_oid})
        if not fitness_class:
            return ClassResult.NOT_FOUND

        return serialize_item(fitness_class)
      
    def get_class_members(self, class_id: str, requesting_trainer_id: str | None = None): # get members of some specific class
        try:
            class_oid = ObjectId(class_id) # mongodb stores ids as objectid type, try to conver
        except (InvalidId, TypeError):
            return ClassResult.INVALID_ID # cannot convert to object id type

        fitness_class = self.collection.find_one({"_id": class_oid}) # look for the class in the database
        if not fitness_class:
            return ClassResult.NOT_FOUND

        # check that the requesting trainer owns this class
        if requesting_trainer_id is not None and fitness_class.get("trainer_id") != requesting_trainer_id:
            return ClassResult.NOT_OWNED

        return fitness_class.get("member_list", []) # extract member list from

    def book_class(self, username: str, class_id: str, user_id: str | None = None):
        try:
            class_oid = ObjectId(class_id)
        except (InvalidId, TypeError):
            return ClassResult.INVALID_ID

        # look for class
        fitness_class = self.collection.find_one({"_id": class_oid})
        
        if not fitness_class:
            return ClassResult.NOT_FOUND

        if user_id is not None and fitness_class.get("trainer_id") == user_id:
            return ClassResult.TRAINER_OWNED
        
        member_list = fitness_class.get("member_list", [])
        if username in member_list:
            return ClassResult.ALREADY_BOOKED
    
        capacity = fitness_class.get("capacity", 0)
        if len(member_list) >= capacity:
            return ClassResult.CLASS_FULL
        result = self.collection.update_one(
            {"_id": class_oid},
            {"$push": {"member_list": username}}
        )
        if result.modified_count == 1:
            return ClassResult.SUCCESS
        
        return ClassResult.FAIL

    def create_recurring_classes(self, class_name, start_date,
                                end_date, location, capacity, trainer_id,
                                recurrence_type, recurrence_count):
        delta = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1), "monthly": timedelta(days=30)}[recurrence_type] # dictionary of how much time to shift wach occurence
        group_id = str(uuid.uuid4()) # unique id shared by all occurences of this class
        start_dt = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) # convert to actual datetime objects
        end_dt = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        created = [] # each iteration of the loop adds result of one create_class
        for i in range(recurrence_count):
            result = self.create_class(class_name=class_name, start_date=start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    end_date=end_dt.strftime("%Y-%m-%dT%H:%M:%SZ"), location = location,
                                    capacity = capacity, trainer_id = trainer_id,
                                    recurrence_group_id=group_id
                                    ) # stores return value after creating class
            created.append(result)
            start_dt += delta
            end_dt += delta
        return created, group_id # list of created class dictionaries and the group id