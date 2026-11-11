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
