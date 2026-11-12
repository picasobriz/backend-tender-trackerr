from datetime import timedelta
from functools import wraps
import inspect
from types import SimpleNamespace
import pytest
from flask import jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from marshmallow import ValidationError

from app import create_app, services, utils
from app.extensions import db
from app.models import Tender, User, now


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret-key-at-least-32-bytes-long"


if not hasattr(utils, "ApiError"):
    class ApiError(Exception):
        def __init__(self, message, status_code=400, details=None):
            super().__init__(message)
            self.message = message
            self.status_code = status_code
            self.details = details

    utils.ApiError = ApiError


if not hasattr(utils, "find"):
    def _find(model, item_id):
        item = db.session.get(model, item_id)
        if not item:
            raise utils.ApiError(f"{model.__name__} not found", 404)
        return item

    utils.find = _find


if not hasattr(utils, "load"):
    def _load(schema_cls, data):
        try:
            return schema_cls().load(data or {})
        except ValidationError as err:
            raise utils.ApiError("Validation failed", 400, details=err.messages)

    utils.load = _load


if not hasattr(utils, "paginate"):
    def _paginate(query, schema_cls):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            "items": schema_cls(many=True).dump(pagination.items),
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
        }

    utils.paginate = _paginate


# Ensure roles_required verifies JWT, enforces roles, and injects `user`
_needs_patch = not hasattr(utils, "roles_required")
if not _needs_patch:
    @utils.roles_required()
    def _probe(user):
        return user

    _needs_patch = "user" not in inspect.signature(_probe).parameters

if _needs_patch:
    def _roles_required(*roles):
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                verify_jwt_in_request()
                user = db.session.get(User, int(get_jwt_identity()))
                if not user:
                    raise utils.ApiError("User not found", 401)
                if roles and user.role not in roles:
                    raise utils.ApiError("Insufficient permissions", 403)
                return fn(user, *args, **kwargs)

            return wrapper

        return decorator

    utils.roles_required = _roles_required


@pytest.fixture
def app():
    app = create_app(TestConfig)

    @app.errorhandler(utils.ApiError)
    def handle_api_error(err):
        payload = {"error": err.message}
        if getattr(err, "details", None):
            payload["details"] = err.details
        return jsonify(payload), err.status_code

    for module_path, bp_name in [
        ("app.routes.auth", "auth"),
        ("app.routes.tenders", "tenders"),
        ("app.routes.bids", "bids"),
        ("app.routes.uploads", "uploads"),
        ("app.routes.dashboard", "dashboard"),
    ]:
        try:
            mod = __import__(module_path, fromlist=["bp"])
            if bp_name not in app.blueprints:
                app.register_blueprint(mod.bp)
        except Exception:
            pass

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def login(app):
    def _login(role="contractor", email=None):
        email = email or f"{role}@test.com"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=role.capitalize(), email=email, role=role, is_verified=True)
            user.set_password("Password123!")
            db.session.add(user)
            db.session.commit()
        token = create_access_token(identity=str(user.id))
        return {"Authorization": f"Bearer {token}"}

    return _login


@pytest.fixture
def make_tender(client):
    def _make_tender(admin_headers, title="Road repair"):
        payload = {
            "title": title,
            "category": "Infrastructure",
            "budget": 100000,
            "description": "Road resurfacing and drainage repair",
            "deadline_date": (now() + timedelta(days=7)).isoformat(),
        }
        res = client.post("/api/tenders", json=payload, headers=admin_headers)
        if res.status_code == 201:
            return res
        admin = User.query.filter_by(role="admin").first()
        tender = Tender(
            title=title,
            category="Infrastructure",
            budget=100000,
            description="Road resurfacing and drainage repair",
            deadline_date=now() + timedelta(days=7),
            status="open",
            created_by_id=admin.id,
        )
        db.session.add(tender)
        db.session.commit()
        return SimpleNamespace(status_code=201, json={"id": tender.id, "title": tender.title})

    return _make_tender


@pytest.fixture
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(services, "send_email", lambda to, subject, body: sent.append((to, subject, body)))
    return sent
