import pytest

from app.extensions import db
from app.models import Tender, now
from datetime import timedelta

BID = {"proposed_amount": 40000, "proposal_text": "We can do it for less"}


@pytest.fixture
def scene(login, make_tender):
    """(admin headers, contractor headers, tender id)"""
    admin, contractor = login("admin"), login("contractor")
    return admin, contractor, make_tender(admin).json["id"]


def test_contractor_submits_bid(client, scene):
    _, contractor, tid = scene
    r = client.post(f"/api/tenders/{tid}/bids", json=BID, headers=contractor)
    assert r.status_code == 201 and r.json["status"] == "pending" and r.json["tender_title"] == "Road repair"


def test_cannot_bid_twice(client, scene):
    _, contractor, tid = scene
    client.post(f"/api/tenders/{tid}/bids", json=BID, headers=contractor)
    r = client.post(f"/api/tenders/{tid}/bids", json=BID, headers=contractor)
    assert r.status_code == 409 and "already bid" in r.json["error"]


def test_only_contractors_can_bid(client, scene):
    admin, _, tid = scene
    assert client.post(f"/api/tenders/{tid}/bids", json=BID, headers=admin).status_code == 403


def test_bid_validation(client, scene):
    _, contractor, tid = scene
    r = client.post(f"/api/tenders/{tid}/bids", json={"proposed_amount": -1}, headers=contractor)
    assert r.status_code == 400 and set(r.json["details"]) == {"proposed_amount", "proposal_text"}


def test_bid_on_missing_tender(client, scene):
    _, contractor, _ = scene
    assert client.post("/api/tenders/999/bids", json=BID, headers=contractor).status_code == 404


def test_cannot_bid_on_closed_tender(client, scene):
    admin, contractor, tid = scene
    client.patch(f"/api/tenders/{tid}", json={"status": "closed"}, headers=admin)
    r = client.post(f"/api/tenders/{tid}/bids", json=BID, headers=contractor)
    assert r.status_code == 400 and "closed" in r.json["error"]


def test_cannot_bid_after_deadline(client, scene):
    _, contractor, tid = scene
    db.session.get(Tender, tid).deadline_date = now() - timedelta(hours=1)
    db.session.commit()
    r = client.post(f"/api/tenders/{tid}/bids", json=BID, headers=contractor)
    assert r.status_code == 400 and "deadline" in r.json["error"]


def test_each_role_sees_the_right_bids(client, login, scene):
    admin, contractor, tid = scene
    client.post(f"/api/tenders/{tid}/bids", json=BID, headers=contractor)
    assert client.get("/api/bids", headers=contractor).json["total"] == 1
    assert client.get(f"/api/bids?tender_id={tid}", headers=admin).json["total"] == 1
    assert client.get("/api/bids", headers=login("contractor", "other@test.com")).json["total"] == 0
    assert client.get("/api/bids", headers=login("admin", "admin2@test.com")).json["total"] == 0


def test_auditor_cannot_list_bids(client, login):
    assert client.get("/api/bids", headers=login("auditor")).status_code == 403
