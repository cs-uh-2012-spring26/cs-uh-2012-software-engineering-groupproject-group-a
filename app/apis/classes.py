from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from http import HTTPStatus
from app.apis import MSG
from app.apis import MSG
from app.db.users import UserResource

api = Namespace(
    "classes", description="API endpoints for class viewing and creation"
)

# test for authentication JWT token
@api.route("/test-member")
class TestMember(Resource):
    @jwt_required()
    @api.doc(security='Bearer')

    def get(self):
        current_user = get_jwt_identity()

        claims = get_jwt()
        user_role = claims.get("role")

        # both trainer and member can access but not guest
        if user_role != "member" and user_role != "trainer":
            print(user_role)
            return {MSG: "Only members and trainers allowed"}, HTTPStatus.FORBIDDEN
        
        return {
            MSG: f"Hello, {current_user} ({user_role})."
        }, HTTPStatus.OK

@api.route("/test-trainer")
class TestTrainer(Resource):
    @jwt_required()
    @api.doc(security='Bearer')
    def get(self):
        current_user = get_jwt_identity()

        claims = get_jwt()
        user_role = claims.get("role")

        # both trainer and member can access but not guest
        if user_role != "trainer":
            return {MSG: "Only trainers allowed"}, HTTPStatus.FORBIDDEN
        
        return {
            MSG: f"Hello, {current_user} ({user_role})."
        }, HTTPStatus.OK
