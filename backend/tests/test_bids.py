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
