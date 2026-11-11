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

