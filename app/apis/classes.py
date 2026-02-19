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