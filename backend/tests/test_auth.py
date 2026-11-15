from datetime import timedelta

import pytest
from flask_jwt_extended import create_access_token


def register(client, **overrides):
    body = {"name": "Ann", "email": "ann@test.com", "password": "password123", **overrides}
    return client.post("/api/auth/register", json=body)


def test_register_sends_verification_email(client, outbox):
    assert register(client).status_code == 201
    assert outbox[0][0] == "ann@test.com" and "verification token" in outbox[0][2]


def test_register_duplicate_email(client, outbox):
    register(client)
    r = register(client, email="ANN@test.com")
    assert r.status_code == 409 and "already registered" in r.json["error"]


@pytest.mark.parametrize("overrides,field", [({"email": "nope"}, "email"), ({"password": "short"}, "password"), ({"name": ""}, "name")])
def test_register_rejects_bad_input(client, outbox, overrides, field):
    r = register(client, **overrides)
    assert r.status_code == 400 and field in r.json["details"]


def test_nobody_can_self_register_as_admin(client, outbox):
    r = register(client, role="admin")
    assert r.status_code == 400 and "contractor" in r.json["details"]["role"]


def test_register_without_json_body(client):
    r = client.post("/api/auth/register", data="hello")
    assert r.status_code == 400 and "JSON object" in r.json["error"]


def test_full_two_step_flow(client, outbox):
    register(client)
    creds = {"email": "ann@test.com", "password": "password123"}
    blocked = client.post("/api/auth/login", json=creds)
    assert blocked.status_code == 403 and "verify" in blocked.json["error"]

    token = outbox[0][2].split()[-1]
    assert client.post("/api/auth/verify", json={"token": token}).status_code == 200

    ok = client.post("/api/auth/login", json=creds)
    assert ok.status_code == 200 and ok.json["user"]["is_verified"] is True and ok.json["token"]


def test_verify_rejects_garbage_token(client):
    r = client.post("/api/auth/verify", json={"token": "garbage"})
    assert r.status_code == 400 and "Invalid or expired" in r.json["error"]


def test_verify_requires_token(client):
    assert "token" in client.post("/api/auth/verify", json={}).json["details"]


def test_login_errors_do_not_reveal_which_part_was_wrong(client, login):
    login("contractor")
    wrong_pw = client.post("/api/auth/login", json={"email": "contractor@test.com", "password": "nope-nope"})
    no_user = client.post("/api/auth/login", json={"email": "who@test.com", "password": "password123"})
    assert wrong_pw.status_code == no_user.status_code == 401
    assert wrong_pw.json["error"] == no_user.json["error"] == "Invalid email or password"


def test_me_returns_current_user(client, login):
    r = client.get("/api/auth/me", headers=login("auditor"))
    assert r.status_code == 200 and r.json["role"] == "auditor" and "password_hash" not in r.json


def test_me_requires_login(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401 and r.json["error"] == "Login required"


def test_garbage_token_rejected(client):
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer abc"})
    assert r.status_code == 401 and "Invalid token" in r.json["error"]


def test_expired_token_rejected(app, client):
    token = create_access_token(identity="1", expires_delta=timedelta(seconds=-1))
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401 and "expired" in r.json["error"]


def test_token_for_deleted_account_rejected(app, client):
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {create_access_token(identity='999')}"})
    assert r.status_code == 401 and "no longer exists" in r.json["error"]