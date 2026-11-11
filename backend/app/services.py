"""Outside-world helpers: verification tokens, SendGrid email, Cloudinary uploads, deadline reminders."""
from datetime import timedelta

import cloudinary.uploader
from flask import current_app
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .models import Tender, User, now
from .schemas import TenderOut
from .utils import ApiError

IMAGE_TYPES = {"png", "jpg", "jpeg", "webp"}
ALLOWED_TYPES = IMAGE_TYPES | {"pdf", "doc", "docx"}
MAX_MB = 5


def make_token(email):
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"]).dumps(email, salt="verify")


def read_token(token, max_age=86400):
    try:
        return URLSafeTimedSerializer(current_app.config["SECRET_KEY"]).loads(token, salt="verify", max_age=max_age)
    except BadSignature:  # SignatureExpired is a subclass
        raise ApiError("Invalid or expired verification token")