from datetime import datetime, timedelta, timezone

import pytest

from app.models import now


def test_admin_creates_tender(login, make_tender):
    r = make_tender(login("admin"))
    assert r.status_code == 201 and r.json["status"] == "open"
    assert r.json["deadline_date"]  # human-readable string


def test_javascript_style_utc_deadline_is_accepted(login, make_tender):
    deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    assert make_tender(login("admin"), deadline_date=deadline).status_code == 201


def test_creating_requires_login(client):
    assert client.post("/api/tenders", json={}).status_code == 401


def test_contractor_cannot_create(login, make_tender):
    r = make_tender(login("contractor"))
    assert r.status_code == 403 and "requires admin" in r.json["error"]


def test_create_reports_every_missing_field(client, login):
    r = client.post("/api/tenders", json={}, headers=login("admin"))
    assert r.status_code == 400
    assert set(r.json["details"]) == {"title", "category", "budget", "description", "deadline_date"}


def test_past_deadline_rejected(login, make_tender):
    r = make_tender(login("admin"), deadline_date=(now() - timedelta(days=1)).isoformat())
    assert r.status_code == 400 and r.json["details"]["deadline_date"] == "must be in the future"


@pytest.mark.parametrize("field,value", [("budget", -5), ("budget", "lots"), ("deadline_date", "tomorrow")])
def test_invalid_values_rejected(login, make_tender, field, value):
    r = make_tender(login("admin"), **{field: value})
    assert r.status_code == 400 and field in r.json["details"]


def test_pagination(client, login, make_tender):
    admin = login("admin")
    for i in range(3):
        make_tender(admin, title=f"Tender {i}")
    page1 = client.get("/api/tenders?per_page=2", headers=admin).json
    page2 = client.get("/api/tenders?per_page=2&page=2", headers=admin).json
    assert (len(page1["items"]), page1["pages"], page1["total"], len(page2["items"])) == (2, 2, 3, 1)


@pytest.mark.parametrize("query", ["page=0", "per_page=999", "status=banana"])
def test_bad_list_params_rejected(client, login, query):
    r = client.get(f"/api/tenders?{query}", headers=login("admin"))
    assert r.status_code == 400 and r.json["error"]


def test_category_filter(client, login, make_tender):
    admin = login("admin")
    make_tender(admin, category="IT")
    make_tender(admin, category="Construction")
    assert client.get("/api/tenders?category=it", headers=admin).json["total"] == 1


def test_contractor_sees_open_tenders_by_default(client, login, make_tender):
    admin = login("admin")
    make_tender(admin)
    closed = make_tender(admin, title="Old").json["id"]
    client.patch(f"/api/tenders/{closed}", json={"status": "closed"}, headers=admin)
    assert client.get("/api/tenders", headers=login("contractor")).json["total"] == 1


def test_auditor_only_sees_awarded(client, login, make_tender):
    admin, auditor = login("admin"), login("auditor")
    open_id = make_tender(admin).json["id"]
    awarded_id = make_tender(admin, title="Done").json["id"]
    client.patch(f"/api/tenders/{awarded_id}", json={"status": "awarded"}, headers=admin)
    assert [t["id"] for t in client.get("/api/tenders", headers=auditor).json["items"]] == [awarded_id]
    assert client.get(f"/api/tenders/{open_id}", headers=auditor).status_code == 403
    assert client.get(f"/api/tenders/{awarded_id}", headers=auditor).status_code == 200


def test_missing_tender_is_404(client, login):
    r = client.get("/api/tenders/999", headers=login("admin"))
    assert r.status_code == 404 and r.json["error"] == "Tender 999 not found"


def test_admin_updates_own_tender(client, login, make_tender):
    admin = login("admin")
    tid = make_tender(admin).json["id"]
    r = client.patch(f"/api/tenders/{tid}", json={"title": "New title", "budget": 1}, headers=admin)
    assert r.status_code == 200 and r.json["title"] == "New title" and r.json["budget"] == 1


def test_invalid_status_rejected(client, login, make_tender):
    admin = login("admin")
    tid = make_tender(admin).json["id"]
    r = client.patch(f"/api/tenders/{tid}", json={"status": "banana"}, headers=admin)
    assert r.status_code == 400 and "status" in r.json["details"]


def test_other_admin_cannot_edit_or_delete(client, login, make_tender):
    owner, other = login("admin"), login("admin", "other@test.com")
    tid = make_tender(owner).json["id"]
    assert client.patch(f"/api/tenders/{tid}", json={"title": "Hacked"}, headers=other).status_code == 403
    r = client.delete(f"/api/tenders/{tid}", headers=other)
    assert r.status_code == 403 and "you created" in r.json["error"]


def test_delete_then_gone(client, login, make_tender):
    admin = login("admin")
    tid = make_tender(admin).json["id"]
    assert client.delete(f"/api/tenders/{tid}", headers=admin).status_code == 204
    assert client.get(f"/api/tenders/{tid}", headers=admin).status_code == 404