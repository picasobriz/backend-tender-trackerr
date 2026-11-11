import os
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from ..utils import ApiError

ALLOWED_TYPES = {"pdf", "png", "jpg", "jpeg", "docx"}
MAX_MB = 10

def get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

def make_token(email: str) -> str:
    """Generate a secure timed token for email verification."""
    s = get_serializer()
    return s.dumps(email, salt="email-verify-salt")

def read_token(token: str, max_age: int = 3600) -> str:
    """Read and validate the timed token, returning the email."""
    s = get_serializer()
    try:
        email = s.loads(token, salt="email-verify-salt", max_age=max_age)
        return email
    except Exception:
        raise ApiError("Invalid or expired verification token", 400)