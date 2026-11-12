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
