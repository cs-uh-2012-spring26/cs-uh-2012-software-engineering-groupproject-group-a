from app.config import Config
from app.apis.auth import api as auth_ns
from app.db import DB

from http import HTTPStatus
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    DB.init_app(app)

    jwt = JWTManager(app)

    api = Api(
        title="Fitness Class Management and Booking System",
        version="1.0",
        description="A system that enables users to create, browse, and manage fitness classes of a particular facility, and for guests/members to book spots in them",
    )

    api.init_app(app)
    api.add_namespace(auth_ns)

    @api.errorhandler(Exception)
    def handle_input_validation_error(error):
        return {"message": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR

    return app
