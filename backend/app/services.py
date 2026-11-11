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
def send_email(to, subject, body):
    """Send via SendGrid. Without an API key it logs instead, so local dev still works."""
    key = current_app.config.get("SENDGRID_API_KEY")
    if not key:
        current_app.logger.info("EMAIL to %s | %s | %s", to, subject, body)
        return False
    try:
        SendGridAPIClient(key).send(Mail(current_app.config["MAIL_FROM"], to, subject, plain_text_content=body))
        return True
    except Exception as e:  # never let a mail failure break an API request
        current_app.logger.error("SendGrid failed for %s: %s", to, e)
        return False    