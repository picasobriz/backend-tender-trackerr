BID = {"proposed_amount": 100, "proposal_text": "Offer"}

def test_dashboard_requires_login(client):
    assert client.get("api/dashboard").status_code == 401

def test_admin_dashboard(client, login, make_tender):
    admin = login("admin")
    tid = make_tender(admin).json["id"]

    client.post(
        f"/api/tenders/{tid}/bids",
        json=BID,
        headers=login("contractor")
    )

    d = client.get("/api/dashboard", headers=admin).json

    assert (
        d["role"],
        d["tenders_created"],
        d["open_tenders"],
        d["proposals_received"],
        d["pending_review"]
    ) == ("admin", 1, 1, 1, 1)

def test_contractor_dashboard(client, login, make_tender):
    contractor = login("contractor")
    tid = make_tender(login("admin")).json["id"]

    client.post(
        f"/api/tenders/{tid}/bids",
        json=BID,
        headers=contractor
    )

    d = client.get("/api/dashboard", headers=contractor).json

    assert (d["my_bids"], d["pending"], d["accepted"]) == (1, 1, 0)
    assert d["upcoming_deadlines"][0]["id"] == tid

def test_auditor_dashboard_counts_awarded_only(client, login, make_tender):
    admin = login("admin")
    tid = make_tender(admin, budget=2500).json["id"]

    make_tender(admin)  # stays open, must not be counted

    client.patch(
        f"/api/tenders/{tid}",
        json={"status": "awarded"},
        headers=admin
    )

    d = client.get("/api/dashboard", headers=login("auditor")).json

    assert (d["awarded_tenders"], d["total_awarded_value"]) == (1, 2500)
