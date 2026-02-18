from flask_restx import Namespace, Resource, fields
from flask import request
from http import HTTPStatus
from app.apis import MSG
from app.apis import MSG
from app.db.users import UserResource

api = Namespace(
    "auth", description="API endpoints for authentication"
)

register_model = api.model("Register", {
    "full_name": fields.String(required=True, description="Full name", example="John Doe"),
    "username": fields.String(required=True, description="Username", example="john_doe"),
    "password": fields.String(required=True, description="Password", example="securepass123"),
    "trainer_code": fields.String(required=False, description="Trainer Code", example="TCODE123")
})

login_model = api.model("Login", {
    "username": fields.String(required=True, description="Username", example="john_doe"),
    "password": fields.String(required=True, description="Password", example="securepass123")
})

auth_success_model = api.model("AuthSuccess", {
    MSG: fields.String(example="Logged in successfully")
})

register_success_model = api.model("RegisterSuccess", {
    MSG: fields.String(example="User registered successfully")
})

auth_error_model = api.model("AuthError", {
    MSG: fields.String(example="Bad credentials")
})

@api.route("/register")
class Register(Resource):
    @api.doc(
            params={
                "full_name": "Name for user, not unique",
                "username": "Unique username per user",
                "password": "User password for registration to be hashed",
                "trainer_code": "(Optional) Trainer Code"
            }
        )
    @api.response(HTTPStatus.CREATED, "Registration successful", register_success_model)
    @api.response(HTTPStatus.BAD_REQUEST, "Invalid input or user already exists", auth_error_model)
    @api.response(
        HTTPStatus.NOT_ACCEPTABLE,
        "Invalid Request",
        api.model(
            "Register Account: Bad Request",
            {MSG: fields.String("Invalid value provided for one of the fields")},
        ),
    )

    @api.expect(register_model, validate=True)
    @api.doc(description="Register a new user account")
    def post(self):

        # collect fields and validate
        assert isinstance(request.json, dict)
        username = request.json.get("username")
        password = request.json.get("password")
        full_name = request.json.get("full_name")
        trainer_code = request.json.get("trainer_code")
        
        if not (
            isinstance(username, str)
            and len(username) > 0
            and isinstance(password, str)
            and len(password) > 0
            and isinstance(full_name, str)
            and len(full_name) > 0
            and isinstance(password, str)
            and len(password) > 0
        ):
            return {
                MSG: "Invalid value provided for one of the fields"
            }, HTTPStatus.NOT_ACCEPTABLE

        user_resource = UserResource()
        
        # check if user exists
        existing_user = user_resource.get_user(username)
        if existing_user:
            return {MSG: "Username already exists"}, HTTPStatus.BAD_REQUEST
        
        success = user_resource.create_user(
            username=username,
            password=password,
            full_name=full_name,
            trainer_code= trainer_code if trainer_code else None
        )
        
        if success:
            return {MSG: "User registered successfully"}, HTTPStatus.CREATED
        
        return {MSG: "Registration failed"}, HTTPStatus.BAD_REQUEST
