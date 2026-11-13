from datetime import timedelta
from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage

from app import services
from app.extensions import db
from app.models import Bid, Tender, User, now
from app.utils import ApiError


# ---- verification tokens ----
def test_token_roundtrip(app):
    assert services.read_token(services.make_token("a@b.com")) == "a@b.com"


def test_tampered_token_is_rejected(app):
    with pytest.raises(ApiError, match="Invalid or expired"):
        services.read_token(services.make_token("a@b.com") + "x")


def test_expired_token_is_rejected(app):
    with pytest.raises(ApiError, match="Invalid or expired"):
        services.read_token(services.make_token("a@b.com"), max_age=-1)


# ---- SendGrid ----
class FakeSendGrid:
    sent, fail = [], False

    def __init__(self, key):
        pass

    def send(self, mail):
        if self.fail:
            raise RuntimeError("boom")
        self.sent.append(mail)


def test_email_without_api_key_is_only_logged(app):
    app.config["SENDGRID_API_KEY"] = None
    assert services.send_email("a@b.com", "Hi", "Body") is False


def test_email_sent_through_sendgrid(app, monkeypatch):
    app.config["SENDGRID_API_KEY"] = "key"
    FakeSendGrid.sent, FakeSendGrid.fail = [], False
    monkeypatch.setattr(services, "SendGridAPIClient", FakeSendGrid)
    assert services.send_email("a@b.com", "Hi", "Body") is True
    assert len(FakeSendGrid.sent) == 1


def test_email_failure_never_raises(app, monkeypatch):
    app.config["SENDGRID_API_KEY"] = "key"
    FakeSendGrid.fail = True
    monkeypatch.setattr(services, "SendGridAPIClient", FakeSendGrid)
    assert services.send_email("a@b.com", "Hi", "Body") is False


# ---- Cloudinary ----
def file(name, data=b"x"):
    return FileStorage(BytesIO(data), filename=name)


@pytest.fixture
def cloud(monkeypatch):
    calls = {}
    def fake_upload(f, **options):
        calls.update(options)
        return {"secure_url": "https://cdn.test/file"}
    monkeypatch.setattr(services.cloudinary.uploader, "upload", fake_upload)
    return calls


def test_images_are_resized_before_storing(cloud):
    assert services.upload_file(file("logo.PNG"), "logo") == "https://cdn.test/file"
    assert cloud["transformation"]["width"] == 800 and cloud["resource_type"] == "image"


def test_documents_are_stored_raw_without_resize(cloud):
    services.upload_file(file("bid.pdf"), "bid")
    assert cloud["resource_type"] == "raw" and "transformation" not in cloud


@pytest.mark.parametrize("name", ["virus.exe", "noextension"])
def test_disallowed_file_types_rejected(cloud, name):
    with pytest.raises(ApiError, match="not allowed") as e:
        services.upload_file(file(name), "bid")
    assert e.value.status == 400


def test_oversized_file_rejected(cloud, monkeypatch):
    monkeypatch.setattr(services, "MAX_MB", 0)
    with pytest.raises(ApiError, match="too large") as e:
        services.upload_file(file("big.pdf"), "bid")
    assert e.value.status == 413


def test_cloudinary_outage_gives_friendly_error(monkeypatch):
    def broken(f, **o):
        raise RuntimeError("down")
    monkeypatch.setattr(services.cloudinary.uploader, "upload", broken)
    with pytest.raises(ApiError, match="try again later") as e:
        services.upload_file(file("a.png"), "logo")
    assert e.value.status == 502


# ---- deadline reminders ----
def add_user(email, role):
    user = User(name=role, email=email, role=role, is_verified=True, password_hash="x")
    db.session.add(user)
    db.session.commit()
    return user


def add_tender(admin, days):
    tender = Tender(title="T", category="C", budget=1, description="d", deadline_date=now() + timedelta(days=days), created_by_id=admin.id)
    db.session.add(tender)
    db.session.commit()
    return tender


def test_reminders_go_to_contractors_who_have_not_bid(app, outbox):
    admin, contractor = add_user("a@t.com", "admin"), add_user("c@t.com", "contractor")
    add_tender(admin, days=1)
    assert services.send_deadline_reminders() == 1
    assert outbox[0][0] == "c@t.com"


def test_no_reminder_if_already_bid_or_deadline_far(app, outbox):
    admin, contractor = add_user("a@t.com", "admin"), add_user("c@t.com", "contractor")
    soon, far = add_tender(admin, days=1), add_tender(admin, days=30)
    db.session.add(Bid(tender_id=soon.id, bidder_id=contractor.id, proposed_amount=1, proposal_text="x"))
    db.session.commit()
    assert services.send_deadline_reminders() == 0
    assert outbox == []