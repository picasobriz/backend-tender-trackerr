"""Marshmallow schemas. *In schemas validate request bodies; *Out schemas shape responses.
Output schemas are allow-lists, so sensitive columns such as password_hash can never leak."""
from datetime import timezone

from marshmallow import EXCLUDE, Schema, fields, pre_load, validates, validate as v
from marshmallow import ValidationError

from .models import now

STATUSES = ("open", "closed", "awarded")
DATE_FORMAT = "%d %b %Y, %H:%M"  # human-readable dates in responses
MSG = {"required": "is required", "null": "is required", "invalid": "is invalid"}


def text(max_len=255, required=True):
    return fields.String(required=required, error_messages=MSG, validate=v.Length(max=max_len, error=f"must be at most {max_len} characters"))


def money():
    return fields.Float(required=True, validate=v.Range(min=0, max=1e12, min_inclusive=False, max_inclusive=False, error="must be more than 0 and less than 1 trillion"),
                        error_messages={**MSG, "invalid": "must be a number", "special": "must be a number"})


class UTCDateTime(fields.DateTime):
    """ISO date/time. Timezone-aware input (e.g. '...Z' from JavaScript) is stored as naive UTC."""
    def _deserialize(self, value, attr, data, **kwargs):
        parsed = super()._deserialize(value, attr, data, **kwargs)
        return parsed.astimezone(timezone.utc).replace(tzinfo=None) if parsed.tzinfo else parsed


# ---------- input ----------
class In(Schema):
    class Meta:
        unknown = EXCLUDE  # ignore fields we do not define

    @pre_load
    def tidy(self, data, **kwargs):
        """Trim text; a blank string counts as missing."""
        if not isinstance(data, dict):
            return data
        return {k: x.strip() if isinstance(x, str) else x for k, x in data.items() if not (isinstance(x, str) and not x.strip())}


class RegisterIn(In):
    name = text(100)
    email = fields.Email(required=True, error_messages={**MSG, "invalid": "is not a valid email address"})
    password = fields.String(required=True, error_messages=MSG, validate=v.Length(min=8, max=128, error="must be 8 to 128 characters"))
    role = fields.String(load_default="contractor", validate=v.OneOf(("contractor", "auditor"), error="must be 'contractor' or 'auditor'"))  # admins come from seed.py


class LoginIn(In):
    email = text(120)
    password = text(128)


class VerifyIn(In):
    token = text(500)


class TenderIn(In):
    title = text(200)
    category = text(80)
    budget = money()
    description = text(5000)
    deadline_date = UTCDateTime(required=True, error_messages={**MSG, "invalid": "must be an ISO date, e.g. 2030-01-31T17:00", "format": "must be an ISO date, e.g. 2030-01-31T17:00"})
    cover_image_url = text(500, required=False)
    status = fields.String(validate=v.OneOf(STATUSES, error=f"must be one of: {', '.join(STATUSES)}"))  # used when updating

    @validates("deadline_date")
    def must_be_future(self, value, **kwrags):
        if value <= now():
            raise ValidationError("must be in the future")


class BidIn(In):
    proposed_amount = money()
    proposal_text = text(5000)
    document_url = text(500, required=False)


class ReviewIn(In):
    status = fields.String(required=True, error_messages=MSG, validate=v.OneOf(("accepted", "rejected"), error="must be 'accepted' or 'rejected'"))


# ==========================================
# OUTPUT SCHEMAS
# ==========================================

# TESTED OUTPUT: User information
class UserOut(Schema):
    id = fields.Integer()
    name = fields.String()
    email = fields.String()
    role = fields.String()
    is_verified = fields.Boolean()
    company_logo_url = fields.String(allow_none=True)

    class Meta:
        fields = (
            "id",
            "name",
            "email",
            "role",
            "is_verified",
            "company_logo_url",
        )


# TESTED OUTPUT: Tender information
class TenderOut(Schema):
    id = fields.Integer()
    title = fields.String()
    category = fields.String()
    budget = fields.Float()
    description = fields.String()
    status = fields.String()
    cover_image_url = fields.String(allow_none=True)

    deadline_date = fields.DateTime(format=DATE_FORMAT)
    deadline_iso = fields.DateTime(
        attribute="deadline_date",
        dump_only=True,
        data_key="deadline_iso"
    )

    created_by_id = fields.Integer()

    class Meta:
        fields = (
            "id",
            "title",
            "category",
            "budget",
            "description",
            "status",
            "cover_image_url",
            "deadline_date",
            "deadline_iso",
            "created_by_id",
        )
    class Meta:
        fields = (
            "id",
            "title",
            "category",
            "budget",
            "description",
            "status",
            "cover_image_url",
            "deadline_date",
            "deadline_iso",
            "created_by_id",
        )


# TESTED OUTPUT: Bid information
class BidOut(Schema):
    id = fields.Integer()
    tender_id = fields.Integer()
    tender_title = fields.String(attribute="tender.title")
    bidder_id = fields.Integer()
    bidder_name = fields.String(attribute="bidder.name")
    proposed_amount = fields.Float()
    proposal_text = fields.String()
    document_url = fields.String(allow_none=True)
    status = fields.String()
    submitted_at = fields.DateTime(format=DATE_FORMAT)

    class Meta:
        fields = (
            "id",
            "tender_id",
            "tender_title",
            "bidder_id",
            "bidder_name",
            "proposed_amount",
            "proposal_text",
            "document_url",
            "status",
            "submitted_at",
        )
