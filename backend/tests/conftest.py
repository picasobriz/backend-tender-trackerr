from datetime import timedelta
from types import SimpleNamespace
import pytest
from flask_jwt_extended import create_access_token

from app import create_app, services
from app.extensions import db
from app.models import Tender, User, now


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret-key"


@pytest.fixture
def app():
    app = create_app(TestConfig)

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
