from functools import wraps
from flask import request
from marshmallow import ValidationError
from .extensions import db

class ApiError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def find(model, item_id):
    item = db.session.get(model, item_id)
    if not item:
        raise ApiError(f"{model.__name__} not found", 404)
    return item

def load(schema_cls, data):
    try:
        return schema_cls().load(data or {})
    except ValidationError as err:
        raise ApiError(str(err.messages), 400)

def paginate(query, schema_cls):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": schema_cls(many=True).dump(pagination.items),
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    }

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator
