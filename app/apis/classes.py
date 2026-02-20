from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from http import HTTPStatus
from app.apis import MSG
from app.db.users import UserResource
from app.db.classes import ClassResource

api = Namespace(
    "classes", description="API endpoints for class viewing and creation"
)

# input model for creating a class
create_class_model = api.model("CreateClass", {
    "class_name": fields.String(required=True, description="Class name/title", example="Morning Yoga"),
    "start_date": fields.String(required=True, description="Start datetime (ISO)", example="2026-02-20T09:00:00Z"),
    "end_date": fields.String(required=True, description="End datetime (ISO)", example="2026-02-20T10:00:00Z"),
    "location": fields.String(required=True, description="Location of class", example="Studio A"),
    "capacity": fields.Integer(required=True, description="Maximum capacity", example=20)
})

create_class_success = api.model("CreateClassSuccess", {
    MSG: fields.String(example="Class created successfully"),
    "class_id": fields.String(example="605c3c2f9f1b2c3d4e5f6a7b")
})

create_class_error = api.model("CreateClassError", {
    MSG: fields.String(example="Invalid value provided for one of the fields")
})

create_class_forbidden = api.model("CreateClassForbidden", {
    MSG: fields.String(example="Only trainers are allowed to create classes")
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

book_class_forbidden = api.model("BookClassForbidden", {
    MSG: fields.String(example="Only trainers and members allowed")
})

book_class_bad_request = api.model("BookClassBadRequest", {
    MSG: fields.String(example="Failed to book class")
})

@api.route("/create-class")

class CreateClass(Resource):
    @jwt_required()
    @api.doc(security='Bearer', params={
        "class_name": "Name/title of the class",
        "start_date": "Start datetime for the class",
        "end_date": "End datetime for the class",
        "location": "Location for the class",
        "capacity": "Maximum number of participants"
    }, description="Create a new class (trainers only)")
    @api.response(HTTPStatus.CREATED, "Class created", create_class_success)
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Invalid input", create_class_error)
    @api.response(HTTPStatus.FORBIDDEN, "Only trainers allowed", create_class_forbidden)
    @api.response(HTTPStatus.BAD_REQUEST, "Failed to create class", create_class_bad_request)
    @api.expect(create_class_model, validate=True)
    
    def post(self):
        current_user = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get("role")

        if user_role != "trainer":
            return {MSG: "Only trainers allowed"}, HTTPStatus.FORBIDDEN

        assert isinstance(request.json, dict)

        class_name = request.json.get("class_name")
        start_date = request.json.get("start_date")
        end_date = request.json.get("end_date")
        location = request.json.get("location")
        capacity = request.json.get("capacity")

        if not (
            isinstance(class_name, str) and len(class_name) > 0
            and isinstance(start_date, str) and len(start_date) > 0
            and isinstance(end_date, str) and len(end_date) > 0
            and isinstance(location, str) and len(location) > 0
            and isinstance(capacity, int) and capacity > 0
        ):
            return {MSG: "Invalid value provided for one of the fields"}, HTTPStatus.NOT_ACCEPTABLE

        # get trainer id from user record if available
        user_resource = UserResource()
        user = user_resource.get_user(current_user)
        trainer_id = user.get("_id") if isinstance(user, dict) and user.get("_id") else current_user
        assert isinstance(trainer_id, str)
        
        class_resource = ClassResource()
        created = class_resource.create_class(
            class_name=class_name,
            start_date=start_date,
            end_date=end_date,
            location=location,
            capacity=capacity,
            trainer_id=trainer_id,
        )

        if created:
            return {MSG: "Class created successfully", "class_id": created.get("_id")}, HTTPStatus.CREATED

        return {MSG: "Failed to create class"}, HTTPStatus.BAD_REQUEST

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
    @api.response(HTTPStatus.FORBIDDEN, "Role not allowed", book_class_forbidden)
    @api.response(HTTPStatus.BAD_REQUEST, "Booking failed", book_class_bad_request)
    def post(self, class_id):
        current_user = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get("role")
        
        # autherize
        if user_role not in {"trainer", "member"}:
            return {MSG: "Only trainers and members allowed"}, HTTPStatus.FORBIDDEN

        # get user
        user_resource = UserResource()
        user = user_resource.get_user(current_user)
        if not isinstance(user, dict) or not user.get("_id"):
            return {MSG: "User not found"}, HTTPStatus.NOT_FOUND


        user_id = user.get("_id")

        class_resource = ClassResource()
        # save username in member_list, but use user_id for trainer ownership check
        booking_status = class_resource.book_class(current_user, class_id, user_id)

        if booking_status == "booked":
            return {MSG: "Class booked successfully"}, HTTPStatus.OK
        if booking_status == "invalid_class_id":
            return {MSG: "Invalid class id"}, HTTPStatus.UNPROCESSABLE_ENTITY
        if booking_status == "class_not_found":
            return {MSG: "Class not found"}, HTTPStatus.NOT_FOUND
        if booking_status == "trainer_cannot_book":
            return {MSG: "Trainer cannot book their own class"}, HTTPStatus.FORBIDDEN
        if booking_status == "already_booked":
            return {MSG: "User already booked this class"}, HTTPStatus.CONFLICT

        return {MSG: "Failed to book class"}, HTTPStatus.BAD_REQUEST

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

@api.route("/<string:class_id>/members") # accessible by going to /classid/members
class ClassMembers(Resource):
    @jwt_required() # requires bearer token on swagger to view this (not available to non-trainers)
    @api.doc(
        security="Bearer", # need jwt token
        params={"class_id": "Class ID (Mongo ObjectId string)"},
        description="View member list of a class (trainers only)" # human readable descrip in swagger
    )
    @api.response(HTTPStatus.OK, "Member list", view_members_success) # types of possible responses
    @api.response(HTTPStatus.NOT_FOUND, "Class not found", view_members_not_found) # calls appropriate response defined in this file
    @api.response(HTTPStatus.UNPROCESSABLE_ENTITY, "Invalid class id", view_members_invalid_id)
    @api.response(HTTPStatus.FORBIDDEN, "Role not allowed", view_members_forbidden)
    def get(self, class_id):
        claims = get_jwt()
        user_role = claims.get("role") # extract user role

        if user_role not in {"trainer"}: # only for trainers
            return {MSG: "Only trainers allowed"}, HTTPStatus.FORBIDDEN # throw appropriate http response

        # get trainer's user ID to verify ownership of the class
        current_user = get_jwt_identity()
        user_resource = UserResource()
        user = user_resource.get_user(current_user)
        trainer_id = user.get("_id") if isinstance(user, dict) and user.get("_id") else None

        class_resource = ClassResource()
        result = class_resource.get_class_members(class_id, trainer_id) # get class members for this class

        if result == "invalid_class_id": # handling possible responses of the get_class_members method
            return {MSG: "Invalid class id"}, HTTPStatus.UNPROCESSABLE_ENTITY
        if result == "class_not_found":
            return {MSG: "Class not found"}, HTTPStatus.NOT_FOUND
        if result == "not_your_class":
            return {MSG: "Only the trainer of this class can view its members"}, HTTPStatus.FORBIDDEN

        return {"members": result}, HTTPStatus.OK # otherwise return result, all went well