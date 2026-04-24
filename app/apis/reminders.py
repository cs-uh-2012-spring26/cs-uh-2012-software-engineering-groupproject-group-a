from http import HTTPStatus

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from app.apis import MEMBER, MSG, TRAINER, require_roles
from app.db.users import UserResource

api = Namespace("reminders", description="API endpoints for reminder preferences")

ALLOWED_NOTIFICATION_METHODS = {"email", "telegram"}

configure_model = api.model(
    "ConfigureReminderPreferences",
    {
        "preferred_notification_methods": fields.List(
            fields.String,
            required=True,
            description="Notification methods to receive reminders through",
            example=["email", "telegram"],
        )
    },
)

configure_success_model = api.model(
    "ConfigureReminderPreferencesSuccess",
    {
        MSG: fields.String(example="Reminder preferences updated successfully"),
        "preferred_notification_methods": fields.List(
            fields.String, example=["email", "telegram"]
        ),
    },
)

configure_error_model = api.model(
    "ConfigureReminderPreferencesError",
    {MSG: fields.String(example="preferred_notification_methods must be a non-empty list")},
)


def _normalize_notification_methods(raw_methods):
    if not isinstance(raw_methods, list) or len(raw_methods) == 0:
        return None

    normalized = []
    seen = set()

    for method in raw_methods:
        if not isinstance(method, str) or len(method.strip()) == 0:
            return None
        normalized_method = method.strip().lower()
        if normalized_method not in ALLOWED_NOTIFICATION_METHODS:
            return None
        if normalized_method in seen:
            continue
        normalized.append(normalized_method)
        seen.add(normalized_method)

    return normalized if len(normalized) > 0 else None


@api.route("/configure")
class ConfigureReminders(Resource):
    @jwt_required()
    @require_roles(MEMBER, TRAINER)
    @api.doc(
        security="Bearer",
        description="Configure preferred notification methods for the authenticated user",
    )
    @api.expect(configure_model, validate=True)
    @api.response(HTTPStatus.OK, "Preferences updated", configure_success_model)
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Invalid input", configure_error_model)
    @api.response(HTTPStatus.NOT_FOUND, "User not found", configure_error_model)
    def post(self):
        assert isinstance(request.json, dict)
        raw_methods = request.json.get("preferred_notification_methods")
        preferred_methods = _normalize_notification_methods(raw_methods)
        if preferred_methods is None:
            return {
                MSG: "preferred_notification_methods must be a non-empty list of supported methods: email, telegram"
            }, HTTPStatus.NOT_ACCEPTABLE

        username = get_jwt_identity()
        user_resource = UserResource()
        updated = user_resource.set_preferred_notification_methods(username, preferred_methods)
        if not updated:
            return {MSG: "User not found"}, HTTPStatus.NOT_FOUND

        return {
            MSG: "Reminder preferences updated successfully",
            "preferred_notification_methods": preferred_methods,
        }, HTTPStatus.OK
