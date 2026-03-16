from http import HTTPStatus
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError
from jwt.exceptions import ExpiredSignatureError, DecodeError, InvalidTokenError

def create_app():
    from app.config import Config
    from app.apis.auth import api as auth_ns
    from app.apis.classes import api as classes_ns
    from app.db import DB

    app = Flask(__name__)
    app.config.from_object(Config)

    DB.init_app(app)

    jwt = JWTManager(app)

    # authorization set up and exceptions
    authorizations = {
        "Bearer": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": 'JWT Authorization header: "Bearer <token>"'
        }
    }

    api = Api(
        title="Fitness Class Management and Booking System",
        version="1.0",
        description="A system that enables users to create, browse, and manage fitness classes of a particular facility, and for guests/members to book spots in them",
        authorizations=authorizations
    )
    
    # register exceptions for jwt
    @api.errorhandler(NoAuthorizationError)
    def handle_auth_error(error):
        return {'message': 'Missing Authorization Header'}, HTTPStatus.UNAUTHORIZED
    
    @api.errorhandler(ExpiredSignatureError)
    def handle_expired_error(error):
        return {'message': 'Token has expired'}, HTTPStatus.UNAUTHORIZED
    
    @api.errorhandler(InvalidTokenError)
    def handle_invalid_token_error(error):
        return {'message': 'Invalid token'}, HTTPStatus.UNAUTHORIZED
    
    @api.errorhandler(DecodeError)
    def handle_decode_error(error):
        return {'message': 'Token is invalid'}, HTTPStatus.UNAUTHORIZED
    
    @api.errorhandler(Exception)
    def handle_general_error(error):
        return {"message": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR

    api.init_app(app)
    api.add_namespace(auth_ns)
    api.add_namespace(classes_ns)

    @api.errorhandler(Exception)
    def handle_input_validation_error(error):
        return {"message": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR

    return app
