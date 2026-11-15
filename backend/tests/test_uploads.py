import io
import pytest
from app import services
from app.models import User


@pytest.fixture
def fake_storage(monkeypatch):
    calls = []

    def _upload(file, kind):
        calls.append((file.filename, kind))
        return f"https://cdn.example.com/{kind}/{file.filename}"

    monkeypatch.setattr(services, "upload_file", _upload, raising=False)
    return calls


def test_upload_requires_auth(client):
    data = {"file": (io.BytesIO(b"hello"), "doc.pdf"), "kind": "bid"}
    assert client.post("/api/uploads", data=data, content_type="multipart/form-data").status_code == 401


def test_upload_missing_or_empty_file(client, login):
    headers = login("contractor")
    r1 = client.post("/api/uploads", data={"kind": "bid"}, headers=headers, content_type="multipart/form-data")
    assert r1.status_code == 400 and "No file received" in r1.json["error"]

    r2 = client.post(
        "/api/uploads",
        data={"file": (io.BytesIO(b""), ""), "kind": "bid"},
        headers=headers,
        content_type="multipart/form-data",
    )
    assert r2.status_code == 400 and "No file received" in r2.json["error"]


def test_upload_invalid_kind(client, login):
    headers = login("contractor")
    data = {"file": (io.BytesIO(b"pdf"), "proposal.pdf"), "kind": "avatar"}
    r = client.post("/api/uploads", data=data, headers=headers, content_type="multipart/form-data")
    assert r.status_code == 400 and "kind must be one of" in r.json["error"]


def test_upload_bid_and_cover_documents(client, login, fake_storage):
    headers = login("contractor")
    for kind, fname in [("bid", "proposal.pdf"), ("cover", "banner.png")]:
        data = {"file": (io.BytesIO(b"binary-data"), fname), "kind": kind}
        r = client.post("/api/uploads", data=data, headers=headers, content_type="multipart/form-data")
        assert r.status_code == 201
        assert r.json == {"url": f"https://cdn.example.com/{kind}/{fname}"}

    assert fake_storage == [("proposal.pdf", "bid"), ("banner.png", "cover")]


def test_upload_logo_updates_user_profile(client, login, fake_storage):
    headers = login("contractor", "logo@test.com")
    data = {"file": (io.BytesIO(b"png-bytes"), "logo.png"), "kind": "logo"}
    r = client.post("/api/uploads", data=data, headers=headers, content_type="multipart/form-data")
    assert r.status_code == 201
    assert r.json["url"] == "https://cdn.example.com/logo/logo.png"

    user = User.query.filter_by(email="logo@test.com").first()
    assert user.company_logo_url == "https://cdn.example.com/logo/logo.png"
