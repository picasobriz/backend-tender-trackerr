
from app.schemas import (
    RegisterIn,
    LoginIn,
    VerifyIn,
    TenderIn,
    BidIn,
    ReviewIn,
)

# ----------------------------------
# TEST 1: User registration
# ----------------------------------

def test_register_valid_data():
    schema = RegisterIn()

    data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "password123",
        "role": "contractor"
    }

    result = schema.load(data)

    print("\nRegistration test passed:", result)


# ----------------------------------
# TEST 2: Invalid registration
# ----------------------------------

def test_register_invalid_email():
    schema = RegisterIn()

    data = {
        "name": "John Doe",
        "email": "invalid-email",
        "password": "password123"
    }

    try:
        schema.load(data)
        assert False, "Expected validation error"

    except Exception as error:
        print("\nInvalid email rejected:", error)


# ----------------------------------
# TEST 3: Tender validation
# ----------------------------------

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

    print("\nTender test passed:", result)


# ----------------------------------
# TEST 4: Invalid tender budget
# ----------------------------------

def test_tender_invalid_budget():
    schema = TenderIn()

    data = {
        "title": "Road Construction Tender",
        "category": "Construction",
        "budget": -1000,
        "description": "Construction of a public road",
        "deadline_date": "2030-01-31T17:00:00Z"
    }

    try:
        schema.load(data)
        assert False, "Expected validation error"

    except Exception as error:
        print("\nInvalid budget rejected:", error)


# ----------------------------------
# TEST 5: Bid validation
# ----------------------------------

def test_bid_valid_data():
    schema = BidIn()

    data = {
        "proposed_amount": 250000,
        "proposal_text": "We can complete the project",
        "document_url": "https://example.com/proposal.pdf"
    }

    result = schema.load(data)

    print("\nBid test passed:", result)


# ----------------------------------
# TEST 6: Review validation
# ----------------------------------

def test_review_valid_data():
    schema = ReviewIn()

    data = {
        "status": "accepted"
    }

    result = schema.load(data)

    print("\nReview test passed:", result)


# ----------------------------------
# RUN ALL TESTS
# ----------------------------------

if __name__ == "__main__":
    test_register_valid_data()
    test_register_invalid_email()
    test_tender_valid_data()
    test_tender_invalid_budget()
    test_bid_valid_data()
    test_review_valid_data()

    print("\nAll schema tests completed!")
