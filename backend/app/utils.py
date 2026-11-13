from functools import wraps

from flask import request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from marshmallow import ValidationError

from .extensions import db
from .models import User


class ApiError(Exception):
    """Raise anywhere; the app turns it into {"error": message, "details": {...}}."""

    def __init__(self, message, status=400, details=None):
        super().__init__(message)
        self.message, self.status, self.details = message, status, details or {}


def load(schema, data, **options):
    """Validate `data` with a schema class -> clean dict, or ApiError(400) listing every bad field."""
    try:
        return schema(**options).load(data)
    except ValidationError as e:
        if not isinstance(data, dict):
            raise ApiError("Request body must be a JSON object")
        raise ApiError("Validation failed", 400, {field: "; ".join(msgs) for field, msgs in e.messages.items()})


def find(model, obj_id):
    obj = db.session.get(model, obj_id)
    if not obj:
        raise ApiError(f"{model.__name__} {obj_id} not found", 404)
    return obj


def roles_required(*roles):
    """Require a valid JWT (and one of `roles`, if given). Passes the current user as the first argument."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = db.session.get(User, int(get_jwt_identity()))
            if not user:
                raise ApiError("Account no longer exists", 401)
            if roles and user.role not in roles:
                raise ApiError(f"Access denied: requires {' or '.join(roles)} role", 403)
            return fn(user, *args, **kwargs)
        return wrapper
    return decorator


def paginate(query, schema):
    """Server-side pagination: ?page=1&per_page=10. `schema` is the output schema class for each item."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    if page < 1 or not 1 <= per_page <= 50:
        raise ApiError("page must be >= 1 and per_page must be between 1 and 50")
    result = query.paginate(page=page, per_page=per_page, error_out=False)
    return {"items": schema(many=True).dump(result.items), "page": result.page, "pages": result.pages, "total": result.total}