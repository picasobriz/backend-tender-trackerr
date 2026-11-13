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
