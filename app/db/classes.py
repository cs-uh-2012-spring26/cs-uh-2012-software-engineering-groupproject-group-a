from app.db.utils import serialize_item, serialize_items
from app.db import DB

CLASS_COLLECTION = "classes"

class ClassResource:

    def __init__(self):
        self.collection = DB.get_collection(CLASS_COLLECTION)

    # TODO: 
    #   - method for adding class
    #   - method for adding user to class
    #   - method for viewing all users in a particular class
    #   - etc...

# Class Model:
    # _id 
    # class_name
    # member_list
    # trainer_id
    # capacity
    # start_date
    # end_date
    # location

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

    # def get_class(self, class_id):
    #     item = self.collection.find_one({"_id": class_id})
    #     return serialize_item(item)