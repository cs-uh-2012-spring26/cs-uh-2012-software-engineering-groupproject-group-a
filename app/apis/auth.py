from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import create_access_token
import datetime
from http import HTTPStatus
from app.apis import MSG, are_non_empty_strings
from app.db.users import UserResource
from app.services.telegram_service import TelegramService

api = Namespace(
    "auth", description="API endpoints for authentication"
)

# general input models
register_model = api.model("Register", {
    "full_name": fields.String(required=True, description="Full name", example="John Doe"),
    "username": fields.String(required=True, description="Username", example="john_doe"),
    "email": fields.String(required=True, description="Email", example="john_doe@example.com"),
    "password": fields.String(required=True, description="Password", example="securepass123"),
    "trainer_code": fields.String(required=False, description="Trainer Code", example="TCODE123")
})

login_model = api.model("Login", {
    "username": fields.String(required=True, description="Username", example="john_doe"),
    "password": fields.String(required=True, description="Password", example="securepass123")
})

# success or error models
login_success_model = api.model("LoginSuccess", {
    MSG: fields.String(example="Logged in successfully"),
    "access_token": fields.String(example="hjX02ksdkKkjqD...")
})

register_success_model = api.model("RegisterSuccess", {
    MSG: fields.String(example="User registered successfully")
})

login_error_model = api.model("LoginError", {
    MSG: fields.String(example="Bad credentials")
})

# register endpoint
@api.route("/register")
class Register(Resource):
    @api.doc(
            params={
                "full_name": "Name for user, not unique",
                "username": "Unique username per user",
                "email": "Unique email for user account",
                "password": "User password for registration to be hashed",
                "trainer_code": "(Optional) Trainer Code"
            },
            description="Register a new user account"
        )
    @api.response(HTTPStatus.CREATED, "Registration successful", register_success_model)
    @api.response(HTTPStatus.BAD_REQUEST, "Invalid input or user already exists", login_error_model)
    @api.response(
        HTTPStatus.NOT_ACCEPTABLE,
        "Invalid Request",
        api.model(
            "Register Account: Bad Request",
            {MSG: fields.String("Invalid value provided for one of the fields")},
        ),
    )

    @api.expect(register_model, validate=True)
    def post(self):

        # collect fields and validate
        assert isinstance(request.json, dict)
        username = request.json.get("username")
        email = request.json.get("email")
        password = request.json.get("password")
        full_name = request.json.get("full_name")
        trainer_code = request.json.get("trainer_code")
        
        if not are_non_empty_strings(username, email, password, full_name):
            return {
                MSG: "Invalid value provided for one of the fields"
            }, HTTPStatus.NOT_ACCEPTABLE

        user_resource = UserResource()
        
        # check if user exists
        existing_user = user_resource.get_user(username)
        if existing_user:
            return {MSG: "Username already exists"}, HTTPStatus.BAD_REQUEST

        existing_email = user_resource.get_user_by_email(email)
        if existing_email:
            return {MSG: "Email already exists"}, HTTPStatus.BAD_REQUEST
        
        registered_user, telegram_link = user_resource.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            trainer_code= trainer_code if trainer_code else None
        )

        if registered_user:
            return {
                MSG: "User registered successfully",
                "telegram_connect_link": telegram_link
                    }, HTTPStatus.CREATED
        
        return {MSG: "Registration failed"}, HTTPStatus.BAD_REQUEST

# login endpoint
@api.route("/login")
class Login(Resource):
    @api.doc(
            params={
                "username": "Username for existing account",
                "password": "Password for the associated username"
            },
            description="Log into an exisiting account with username and password"
        )
    @api.response(HTTPStatus.OK, "Login successful", login_success_model)
    @api.response(HTTPStatus.UNAUTHORIZED, "Invalid credentials", login_error_model)
    @api.response(
        HTTPStatus.NOT_ACCEPTABLE,
        "Invalid Request",
        api.model(
            "Login: Bad Request",
            {MSG: fields.String("Invalid value provided for one of the fields")},
        ),
    )

    @api.expect(login_model, validate=True)
    def post(self):

        # collect fields and validate
        assert isinstance(request.json, dict)
        username = request.json.get("username")
        password = request.json.get("password")

        if not are_non_empty_strings(username, password):
            return {
                MSG: "Invalid value provided for one of the fields"
            }, HTTPStatus.NOT_ACCEPTABLE

        user_resource = UserResource()
        telegram_service = TelegramService()

        if user_resource.check_password(username, password):

            # get role for token
            user = user_resource.get_user(username)
            assert isinstance(user, dict)

            telegram_token = user_resource.get_user_telegram_token(username)
            print(telegram_token)
            if telegram_token:
                chat_id = telegram_service.get_user_chat_id(telegram_token)
                print(chat_id)
                if chat_id:
                    user_resource.append_telegram_chat_id(username, chat_id)
                    print("appended?")

            access_token = create_access_token(
                identity=username,
                additional_claims={
                    "role": user.get("role", "member"),  # Add role to token
                    "full_name": user.get("full_name")   # Can add other data too
                },
                expires_delta=datetime.timedelta(hours=24)
            )
            return {
                MSG: "Logged in successfully",
                "access_token": access_token
            }, HTTPStatus.OK
        
        return {MSG: "Bad credentials"}, HTTPStatus.UNAUTHORIZED
