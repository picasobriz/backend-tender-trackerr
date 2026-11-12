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

