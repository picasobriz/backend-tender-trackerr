from datetime import datetime
from decimal import Decimal

import pytest

from app.models import Tender, User
from app.schemas import BidIn, RegisterIn, TenderIn, TenderOut, UserOut
from app.utils import ApiError, load


# ---- load(): validation through schemas ----
def test_load_returns_clean_values():
    assert load(BidIn, {"proposed_amount": "5", "proposal_text": "  Offer "}) == {"proposed_amount": 5.0, "proposal_text": "Offer"}


def test_load_lists_every_problem_at_once():
    with pytest.raises(ApiError) as e:
        load(BidIn, {"proposed_amount": "abc"})
    assert e.value.status == 400
    assert e.value.details == {"proposal_text": "is required", "proposed_amount": "must be a number"}


def test_blank_string_counts_as_missing():
    with pytest.raises(ApiError) as e:
        load(BidIn, {"proposed_amount": 5, "proposal_text": "   "})
    assert e.value.details == {"proposal_text": "is required"}


def test_optional_field_may_be_left_out():
    assert "document_url" not in load(BidIn, {"proposed_amount": 5, "proposal_text": "x"})


def test_unknown_fields_are_ignored():
    assert "is_admin" not in load(BidIn, {"proposed_amount": 5, "proposal_text": "x", "is_admin": True})


@pytest.mark.parametrize("body", [None, [], "text"])
def test_load_rejects_non_object_body(body):
    with pytest.raises(ApiError, match="JSON object"):
        load(BidIn, body)


@pytest.mark.parametrize("bad", [0, -5, "abc", "nan", "inf", 1e13])
def test_money_rejects_zero_negative_text_and_huge(bad):
    with pytest.raises(ApiError) as e:
        load(BidIn, {"proposed_amount": bad, "proposal_text": "x"})
    assert "proposed_amount" in e.value.details


def test_register_defaults_role_and_checks_email_and_password():
    assert load(RegisterIn, {"name": "A", "email": "a@b.com", "password": "password1"})["role"] == "contractor"
    with pytest.raises(ApiError) as e:
        load(RegisterIn, {"name": "A", "email": "nope", "password": "short", "role": "admin"})
    assert set(e.value.details) == {"email", "password", "role"}


def test_dates_with_timezone_become_naive_utc():
    parsed = load(TenderIn, {"deadline_date": "2999-01-02T10:00:00+02:00"}, partial=True)["deadline_date"]
    assert parsed.tzinfo is None and parsed.hour == 8


def test_bad_or_past_dates_rejected():
    for value, message in [("next friday", "must be an ISO date"), ("2000-01-01T10:00", "must be in the future")]:
        with pytest.raises(ApiError) as e:
            load(TenderIn, {"deadline_date": value}, partial=True)
        assert message in e.value.details["deadline_date"]


def test_partial_update_skips_required_fields():
    assert load(TenderIn, {"title": "New"}, partial=True) == {"title": "New"}


# ---- output schemas ----
def test_user_output_never_includes_password_hash(app):
    user = User(id=1, name="A", email="a@b.com", role="admin", is_verified=True, password_hash="secret")
    out = UserOut().dump(user)
    assert out["email"] == "a@b.com" and "password_hash" not in out and "secret" not in str(out)


def test_tender_output_is_human_readable_and_json_friendly(app):
    tender = Tender(id=1, title="T", category="C", budget=Decimal("5.50"), description="d", status="open",
                    deadline_date=datetime(2030, 1, 2, 10, 0), created_by_id=1)
    out = TenderOut().dump(tender)
    assert out["budget"] == 5.5 and out["deadline_date"] == "02 Jan 2030, 10:00" and out["deadline_iso"] == "2030-01-02T10:00:00"