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
    # capactiy
    # start_date
    # end_date
    # location