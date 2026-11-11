
from datetime import datetime
from types import SimpleNamespace

import pytest
from marshmallow import ValidationError

from app.schemas import (
    RegisterIn,
    LoginIn,
    VerifyIn,
    TenderIn,
    BidIn,
    ReviewIn,
    UserOut,
    TenderOut,
    BidOut,
)


# ==========================================
# INPUT SCHEMA TESTS
# ==========================================

# TEST 1: Valid user registration

def test_register_valid_data():
    schema = RegisterIn()

    data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "password123",
        "role": "contractor"
    }

    result = schema.load(data)

    assert result["name"] == "John Doe"
    assert result["email"] == "john@example.com"
    assert result["role"] == "contractor"


# TEST 2: Invalid registration email

def test_register_invalid_email():
    schema = RegisterIn()

    data = {
        "name": "John Doe",
        "email": "invalid-email",
        "password": "password123"
    }

    with pytest.raises(ValidationError):
        schema.load(data)


# TEST 3: Valid tender creation

def test_tender_valid_data():
    schema = TenderIn()

    data = {
        "title": "Road Construction Tender",
        "category": "Construction",
        "budget": 500000,
        "description": "Construction of a public road",
        "deadline_date": "2030-01-31T17:00:00Z",
        "status": "open"
    }

    result = schema.load(data)

    assert result["title"] == "Road Construction Tender"
    assert result["budget"] == 500000.0
    assert result["status"] == "open"


# TEST 4: Invalid tender budget

def test_tender_invalid_budget():
    schema = TenderIn()

    data = {
        "title": "Road Construction Tender",
        "category": "Construction",
        "budget": -1000,
        "description": "Construction of a public road",
        "deadline_date": "2030-01-31T17:00:00Z"
    }

    with pytest.raises(ValidationError):
        schema.load(data)


# TEST 5: Valid bid submission

def test_bid_valid_data():
    schema = BidIn()

    data = {
        "proposed_amount": 250000,
        "proposal_text": "We can complete the project",
        "document_url": "https://example.com/proposal.pdf"
    }

    result = schema.load(data)

    assert result["proposed_amount"] == 250000.0
    assert result["proposal_text"] == "We can complete the project"


# TEST 6: Valid bid review

def test_review_valid_data():
    schema = ReviewIn()

    data = {
        "status": "accepted"
    }

    result = schema.load(data)

    assert result["status"] == "accepted"


# ==========================================
# OUTPUT SCHEMA TESTS
# ==========================================

# TEST 7: User output serialization

def test_user_output():
    user = SimpleNamespace(
        id=1,
        name="John Doe",
        email="john@example.com",
        role="contractor",
        is_verified=True,
        company_logo_url="https://example.com/logo.png",
        password_hash="secret_hash"
    )

    result = UserOut().dump(user)

    assert result["id"] == 1
    assert result["name"] == "John Doe"
    assert result["email"] == "john@example.com"
    assert result["role"] == "contractor"
    assert result["is_verified"] is True
    assert result["company_logo_url"] == "https://example.com/logo.png"

    # Never expose sensitive password information
    assert "password_hash" not in result


# TEST 8: Tender output serialization

def test_tender_output():
    tender = SimpleNamespace(
        id=1,
        title="Road Construction Tender",
        category="Construction",
        budget=500000.0,
        description="Construction of a public road",
        status="open",
        cover_image_url="https://example.com/road.png",
        deadline_date=datetime(2030, 1, 31, 17, 0),
        created_by_id=2
    )

    result = TenderOut().dump(tender)

    assert result["id"] == 1
    assert result["title"] == "Road Construction Tender"
    assert result["category"] == "Construction"
    assert result["budget"] == 500000.0
    assert result["description"] == "Construction of a public road"
    assert result["status"] == "open"
    assert result["cover_image_url"] == "https://example.com/road.png"
    assert result["created_by_id"] == 2

    assert isinstance(result["deadline_date"], str)
    assert isinstance(result["deadline_iso"], str)


# TEST 9: Bid output serialization

def test_bid_output():
    bid = SimpleNamespace(
        id=1,
        tender_id=10,
        bidder_id=5,
        proposed_amount=250000.0,
        proposal_text="We can complete the project",
        document_url="https://example.com/proposal.pdf",
        status="pending",
        submitted_at=datetime(2030, 1, 15, 10, 30),
        tender=SimpleNamespace(
            title="Road Construction Tender"
        ),
        bidder=SimpleNamespace(
            name="John Doe"
        )
    )

    result = BidOut().dump(bid)

    assert result["id"] == 1
    assert result["tender_id"] == 10
    assert result["tender_title"] == "Road Construction Tender"
    assert result["bidder_id"] == 5
    assert result["bidder_name"] == "John Doe"
    assert result["proposed_amount"] == 250000.0
    assert result["proposal_text"] == "We can complete the project"
    assert result["document_url"] == "https://example.com/proposal.pdf"
    assert result["status"] == "pending"

    assert isinstance(result["submitted_at"], str)
