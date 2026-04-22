from functools import wraps
from http import HTTPStatus

from flask_jwt_extended import get_jwt

MSG = "message"
TRAINER = "trainer"
MEMBER = "member"

FORBIDDEN_ROLE_MESSAGE = "Current role is not allowed to access this resource"


def require_roles(*allowed_roles: str):
	if len(allowed_roles) == 0:
		raise ValueError("At least one role must be provided")

	allowed_set = set(allowed_roles)

	def decorator(fn):
		@wraps(fn)
		def wrapper(*args, **kwargs):
			claims = get_jwt()
			user_role = claims.get("role")
			if user_role not in allowed_set:
				return {MSG: FORBIDDEN_ROLE_MESSAGE}, HTTPStatus.FORBIDDEN
			return fn(*args, **kwargs)

		return wrapper

	return decorator