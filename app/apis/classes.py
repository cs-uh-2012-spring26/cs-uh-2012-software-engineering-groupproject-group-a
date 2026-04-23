from abc import ABC, abstractmethod

from flask_restx import Namespace, Resource, fields
import uuid
from flask import request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from http import HTTPStatus
from datetime import datetime, timezone
from app import DAILY, WEEKLY, MONTHLY
from app.apis import MSG, MEMBER, TRAINER, FORBIDDEN_ROLE_MESSAGE, are_non_empty_strings, require_roles
from app.db.users import UserResource
from app.db.classes import ClassResult, ClassResource
from app.services.email_service import EmailService

api = Namespace(
    "classes", description="API endpoints for class viewing and creation"
)

# input model for creating a class
create_class_model = api.model("CreateClass", {
    "class_name": fields.String(required=True, description="Class name/title", example="Morning Yoga"),
    "start_date": fields.String(required=True, description="Start datetime (ISO format, must be in the future)", example="2026-05-20T09:00:00Z"),
    "end_date": fields.String(required=True, description="End datetime (ISO, must be after start_date)", example="2026-05-20T10:00:00Z"),
    "location": fields.String(required=True, description="Location of class", example="Studio A"),
    "capacity": fields.Integer(required=True, description="Maximum capacity", example=20),
    "is_recurring": fields.Boolean(required=False, description="Whether this class repeats", example=True),
    "recurrence_type": fields.String(required=False, description="Recurrence type: daily, weekly or monthly", example="weekly"),
    "recurrence_count": fields.Integer(required=False, description="How many times it repeats, including the first class", example=10),
})

create_class_success = api.model("CreateClassSuccess", {
    MSG: fields.String(example="Class created successfully"),
    "class_id": fields.String(example="605c3c2f9f1b2c3d4e5f6a7b")
})

create_class_error = api.model("CreateClassError", {
    MSG: fields.String(example="Invalid value provided for one of the fields")
})

create_class_forbidden = api.model("CreateClassForbidden", {
    MSG: fields.String(example=FORBIDDEN_ROLE_MESSAGE)
})

create_class_bad_request = api.model("CreateClassBadRequest", {
    MSG: fields.String(example="Failed to create class")
})

book_class_success = api.model("BookClassSuccess", {
    MSG: fields.String(example="Class booked successfully")
})

book_class_invalid_id = api.model("BookClassInvalidId", {
    MSG: fields.String(example="Invalid class id")
})

book_class_not_found = api.model("BookClassNotFound", {
    MSG: fields.String(example="Class not found")
})

book_class_conflict = api.model("BookClassConflict", {
    MSG: fields.String(example="User already booked this class")
})

book_class_class_full = api.model("BookClassFull", {
    MSG: fields.String(example="Class is full")
})

book_class_forbidden = api.model("BookClassForbidden", {
    MSG: fields.String(example=FORBIDDEN_ROLE_MESSAGE)
})

book_class_bad_request = api.model("BookClassBadRequest", {
    MSG: fields.String(example="Failed to book class")
})

remind_class_success = api.model("RemindClassSuccess", {
    MSG: fields.String(example="Reminder process completed"),
    "sent": fields.Integer(example=8),
    "failed": fields.Integer(example=2),
    "errors": fields.List(fields.String, description="Send failure details", required=False),
})

remind_class_invalid_id = api.model("RemindClassInvalidId", {
    MSG: fields.String(example="Invalid class id")
})

remind_class_not_found = api.model("RemindClassNotFound", {
    MSG: fields.String(example="Class not found")
})

remind_class_forbidden = api.model("RemindClassForbidden", {
    MSG: fields.String(example="Only the trainer of this class can send reminders")
})

remind_class_bad_request = api.model("RemindClassBadRequest", {
    MSG: fields.String(example="Class is in the past or has invalid date")
})

# documented response schema for swagger
# defines required fields, data types, brief description
class_model = api.model("Class", { # Swagger documentation for UI
    "_id": fields.String(description="Class ID"),
    "class_name": fields.String(description="Class name"),
    "start_date": fields.String(description="Start datetime"),
    "end_date": fields.String(description="End datetime"),
    "location": fields.String(description="Location"),
    "capacity": fields.Integer(description="Capacity"),
    "trainer_id": fields.String(description="Trainer ID"),
    "member_list": fields.List(fields.String, description="Booked usernames"),
})

# for swagger documentation
# list of classes. each item has shape of class_model defined above

view_classes_success = api.model("ViewClassesSuccess", {
    "classes": fields.List(fields.Nested(class_model))
})

@api.route("") # default for GET/classes
class ClassList(Resource):
    @api.doc(description="Get all available classes (publicly available)")
    @api.response(HTTPStatus.OK, "List of classes", view_classes_success)
    def get(self):
        class_resource = ClassResource() # instance of class resource class in db/classes.py for talking to
        classes = class_resource.get_all_classes() # use function defined in db/classes.py
        return {"classes": classes}, HTTPStatus.OK

class SingleClassStrategy:
    def create(self, class_resource, class_name, start_date, end_date, location, capacity, trainer_id, **kwargs): # kwards needed to receive recurrence_type and recurrence_count without using them
        # ideas is that we can call both single and recurring class strategies with the same arguments
        result = class_resource.create_class(
            class_name=class_name, start_date=start_date, end_date=end_date,
            location=location, capacity=capacity, trainer_id=trainer_id,
        )
        if result:
            return {MSG: "Class created successfully", "class_id": result.get("_id")}, HTTPStatus.CREATED
        return {MSG: "Failed to create class"}, HTTPStatus.BAD_REQUEST

class RecurringClassStrategy:
    def create(self, class_resource, class_name, start_date, end_date, location, capacity, trainer_id, recurrence_type, recurrence_count, **kwargs):
        created, group_id = class_resource.create_recurring_classes(
            class_name=class_name, start_date=start_date, end_date=end_date,
            location=location, capacity=capacity, trainer_id=trainer_id,
            recurrence_type=recurrence_type, recurrence_count=recurrence_count,
        )
        if created:
            return {MSG: "Recurring classes created successfully", "group_id": group_id, "classes_created": len(created)}, HTTPStatus.CREATED
        return {MSG: "Failed to create classes"}, HTTPStatus.BAD_REQUEST

@api.route("/create-class")

class CreateClass(Resource):
    def __init__(self, api=None, *args, **kwargs):
        user_resource = kwargs.pop("user_resource", None)
        class_resource = kwargs.pop("class_resource", None)
        super().__init__(api, *args, **kwargs)
        self.user_resource = user_resource if user_resource is not None else UserResource()
        self.class_resource = class_resource if class_resource is not None else ClassResource()

    @jwt_required()
    @require_roles(TRAINER)
    @api.doc(security='Bearer', params={
        "class_name": "Name/title of the class",
        "start_date": "Start datetime for the class (must be in the future)",
        "end_date": "End datetime for the class (must be after start_date)",
        "location": "Location for the class",
        "capacity": "Maximum number of participants",
        "is_recurring":"Indicates wether class is recurring",
        "recurrence_type":"Indicates if it recurrs: daily, weekly, or monthly",
        "recurrence_count":"Indicates the amount of times it recurres, including the first class",
    }, description="Create a new class (trainers only)")
    @api.response(HTTPStatus.CREATED, "Class created", create_class_success)
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Invalid input", create_class_error)
    @api.response(HTTPStatus.FORBIDDEN, FORBIDDEN_ROLE_MESSAGE, create_class_forbidden)
    @api.response(HTTPStatus.BAD_REQUEST, "Failed to create class", create_class_bad_request)
    @api.expect(create_class_model, validate=True)
        
    def post(self):
        current_user = get_jwt_identity()

        assert isinstance(request.json, dict)

        class_name = request.json.get("class_name")
        start_date = request.json.get("start_date")
        end_date = request.json.get("end_date")
        location = request.json.get("location")
        capacity = request.json.get("capacity")
        is_recurring = request.json.get("is_recurring", False)
        recurrence_type = request.json.get("recurrence_type", None)
        recurrence_count = request.json.get("recurrence_count", None)

        if not (
            are_non_empty_strings(class_name, start_date, end_date, location)
            and isinstance(capacity, int) and capacity > 0
        ):
            return {MSG: "Invalid value provided for one of the fields"}, HTTPStatus.NOT_ACCEPTABLE

        # Validate that start_date is in the future and end_date > start_date
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            end_dt = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if start_dt <= now:
                return {MSG: "Class start date must be in the future"}, HTTPStatus.NOT_ACCEPTABLE
            if end_dt <= start_dt:
                return {MSG: "Class end date must be after start date"}, HTTPStatus.NOT_ACCEPTABLE
        except ValueError:
            return {MSG: "Invalid date format"}, HTTPStatus.NOT_ACCEPTABLE

        # get trainer id from user record if available
        user = self.user_resource.get_user(current_user)
        trainer_id = user.get("_id") if isinstance(user, dict) and user.get("_id") else current_user
        assert isinstance(trainer_id, str)

        # check if class is recurring or not
        if is_recurring:
            if recurrence_type not in [DAILY, WEEKLY, MONTHLY]:
                return {MSG: "recurrence_type must be daily, weekly, or monthly"}, HTTPStatus.NOT_ACCEPTABLE
            if not isinstance(recurrence_count, int) or recurrence_count <= 0: # recurrence count must be positive integer
                return {MSG: "recurrence_count must be a positive integer"}, HTTPStatus.NOT_ACCEPTABLE
            strategy = RecurringClassStrategy()
            
        else:
            strategy = SingleClassStrategy()
            
        return strategy.create(self.class_resource, class_name=class_name, start_date=start_date,
                                    end_date=end_date, location=location, capacity=capacity,
                                    trainer_id=trainer_id, recurrence_type=recurrence_type,
                                    recurrence_count=recurrence_count,
                                    ) # we can use the same input regardless on whether it is single class or recurring

@api.route("/<string:class_id>/book")
class ClassBooking(Resource):
    @jwt_required()
    @api.doc(
        security="Bearer",
        params={
            "class_id": "Class ID to book (Mongo ObjectId string)"
        },
        description="Book an existing class (members and trainers only)",
    )
    @api.response(HTTPStatus.OK, "Class booked", book_class_success)
    @api.response(HTTPStatus.UNPROCESSABLE_ENTITY, "Invalid class id", book_class_invalid_id)
    @api.response(HTTPStatus.NOT_FOUND, "Class not found", book_class_not_found)
    @api.response(HTTPStatus.CONFLICT, "Already booked", book_class_conflict)
    @api.response(HTTPStatus.FORBIDDEN, "Class full", book_class_class_full)
    @api.response(HTTPStatus.FORBIDDEN, FORBIDDEN_ROLE_MESSAGE, book_class_forbidden)
    @api.response(HTTPStatus.BAD_REQUEST, "Booking failed", book_class_bad_request)
    
    @require_roles(TRAINER, MEMBER)
    
    def post(self, class_id):
        current_user = get_jwt_identity()

        user_resource = UserResource()
        user = user_resource.get_user(current_user)
        if not isinstance(user, dict) or not user.get("_id"):
            return {MSG: "User not found"}, HTTPStatus.NOT_FOUND

        user_id = user.get("_id")

        class_resource = ClassResource()
        outcome = class_resource.book_class(current_user, class_id, user_id)

        if isinstance(outcome, ClassResult):
            return outcome.resolves()

view_members_success = api.model("ViewMembersSuccess", {
    "members": fields.List(fields.String, description="List of usernames booked in the class")
}) # swagger ui response for success

view_members_not_found = api.model("ViewMembersNotFound", {
    MSG: fields.String(example="Class not found")
}) # swagger ui response for no class found

view_members_invalid_id = api.model("ViewMembersInvalidId", {
    MSG: fields.String(example="Invalid class id")
}) # swagger ui response for invalid class id

view_members_forbidden = api.model("ViewMembersForbidden", {
    MSG: fields.String(example="Only the trainer of this class can view its members")
}) # swagger ui response for unauthorized role


# def _members_error_response(result): # handles the various errors we expect to have when getting class members
#     if result in (BookingResult.INVALID_ID, "invalid_class_id"):
#         return {MSG: "Invalid class id"}, HTTPStatus.UNPROCESSABLE_ENTITY
#     if result in (BookingResult.NOT_FOUND, "class_not_found"):
#         return {MSG: "Class not found"}, HTTPStatus.NOT_FOUND
#     if result in (BookingResult.NOT_OWNED, "not_your_class"):
#         return {MSG: "Only the trainer of this class can view its members"}, HTTPStatus.FORBIDDEN
#     return None

def _get_trainer_id():
    current_user = get_jwt_identity()
    user = UserResource().get_user(current_user)
    return user.get("_id") if isinstance(user, dict) and user.get("_id") else None


def _prepare_reminder_context(class_id, trainer_id, class_resource):
    members = class_resource.get_class_members(class_id, trainer_id)

    if isinstance(members, ClassResult):
        if members == ClassResult.NOT_OWNED:
            return None, None, ({MSG: "Only the trainer of this class can send reminders"}, HTTPStatus.FORBIDDEN)
        
        return None, None, members.resolves()

    class_info = class_resource.get_class_by_id(class_id)
    class_name_raw = class_info.get("class_name") if isinstance(class_info, dict) else None
    class_name = class_name_raw if isinstance(class_name_raw, str) and len(class_name_raw) > 0 else "your upcoming class"

    # check that class is not in the past
    start_date_raw = class_info.get("start_date") if isinstance(class_info, dict) else None
    if isinstance(start_date_raw, str) and len(start_date_raw) > 0:
        try:
            start_dt = datetime.fromisoformat(start_date_raw.replace("Z", "+00:00"))
            if start_dt < datetime.now(timezone.utc):
                return None, None, ({MSG: "Cannot send reminders for a class that has already passed"}, HTTPStatus.BAD_REQUEST)
        except ValueError:
            return None, None, ({MSG: "Class has an invalid start date format"}, HTTPStatus.BAD_REQUEST)

    return members, class_name, None


def _send_reminder_emails(members, class_name, user_resource):
    sent = 0
    failed = 0
    errors = []
    for member in members:
        member_user = user_resource.get_user(member)
        member_email = member_user.get("email") if isinstance(member_user, dict) else None

        if not isinstance(member_email, str) or len(member_email.strip()) == 0:
            failed += 1
            errors.append(f"{member}: missing email")
            continue

        success, error = EmailService.send_class_reminder(member_email, class_name)
        if success:
            sent += 1
        else:
            failed += 1
            if isinstance(error, str) and len(error) > 0:
                errors.append(f"{member_email}: {error}")

    message = (
        f"All {sent} reminder emails sent successfully"
        if failed == 0
        else "Reminder process completed with some failed emails"
    )

    response_payload = {
        MSG: message,
        "sent": sent,
        "failed": failed,
    }

    if len(errors) > 0:
        response_payload["errors"] = errors

    return response_payload

@api.route("/<string:class_id>/members")
class ClassMembers(Resource):
    @jwt_required()
    @require_roles(TRAINER)
    @api.doc(
        security="Bearer",
        params={"class_id": "Class ID (Mongo ObjectId string)"},
        description="View member list of a class (trainers only)"
    )
    @api.response(HTTPStatus.OK, "Member list", view_members_success) 
    @api.response(HTTPStatus.NOT_FOUND, "Class not found", view_members_not_found)
    @api.response(HTTPStatus.UNPROCESSABLE_ENTITY, "Invalid class id", view_members_invalid_id)
    @api.response(HTTPStatus.FORBIDDEN, "Role not allowed", view_members_forbidden)
    
    def get(self, class_id):
        
        trainer_id = _get_trainer_id()

        class_resource = ClassResource()
        result = class_resource.get_class_members(class_id, trainer_id) # get class members for this class

        if isinstance(result, ClassResult):
            return result.resolves()
        
        # if isinstance(result, BookingResult):
        #     response_data, status_code = BOOKING_RESPONSE_MAP.get(
        #         result, 
        #         ({MSG: "An error occurred"}, HTTPStatus.BAD_REQUEST)
        #     )
        #     return response_data, status_code

        return {"members": result}, HTTPStatus.OK # otherwise return result, all went well
    
#########################################################################
class NotificationStrategy(ABC):
    @abstractmethod
    def send(self, user_data, message_body):
        pass

class EmailNotification(NotificationStrategy):
    def send(self, user_data, message_body):
        pass

class TelegramNotification(NotificationStrategy):
    def send(self, user_data, message_body):
        pass

class NotificationEngine:
    def __init__(self, strategies=None):
        self._strategies = strategies or []

    def broadcast(self, user_data, message):
        results = []
        for strategy in self._strategies:
            success, error = strategy.send(user_data, message)
            results.append({"method": strategy.__class__.__name__, "success": success, "error": error})
        return results
##############################################################################

@api.route("/remind/<string:class_id>")
class ClassReminder(Resource):
    @jwt_required()
    @require_roles(TRAINER)
    @api.doc(
        security="Bearer",
        params={"class_id": "Class ID (Mongo ObjectId string)"},
        description="Send reminder emails to members of a class (only the class trainer)",
    )
    @api.response(HTTPStatus.OK, "Reminder process completed", remind_class_success)
    @api.response(HTTPStatus.UNPROCESSABLE_ENTITY, "Invalid class id", remind_class_invalid_id)
    @api.response(HTTPStatus.NOT_FOUND, "Class not found", remind_class_not_found)
    @api.response(HTTPStatus.FORBIDDEN, "Role not allowed", remind_class_forbidden)
    @api.response(HTTPStatus.BAD_REQUEST, "Class is in the past or has invalid date", remind_class_bad_request)
    def post(self, class_id):
        trainer_id = _get_trainer_id()
        user_resource = UserResource()
        class_resource = ClassResource()

        members, class_name, err = _prepare_reminder_context(class_id, trainer_id, class_resource)
        if err:
            return err

        assert members is not None
        assert class_name is not None

        # response_payload = _send_reminder_emails(members, class_name, user_resource)
        # return response_payload, HTTPStatus.OK
        
        active_strategies = [
            EmailNotification(),
            TelegramNotification()
        ]
        
        engine = NotificationEngine(active_strategies)
        
        total_sent = 0
        for member_id in members:
            user = user_resource.get_user(member_id)
            engine.broadcast(user, f"Your class {class_name} starts soon!")
            total_sent += 1

        return {MSG: "Reminders processed", "count": total_sent}, HTTPStatus.OK
