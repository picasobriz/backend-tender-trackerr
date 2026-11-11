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


def upload_file(file, kind):
    """Validate, resize (images) and store a file on Cloudinary; returns its secure URL."""
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_TYPES:
        raise ApiError(f"File type '.{ext}' not allowed. Use: {', '.join(sorted(ALLOWED_TYPES))}", 400)
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_MB * 1024 * 1024:
        raise ApiError(f"File is too large. Maximum size is {MAX_MB} MB", 413)
    options = {"folder": f"tendertrack/{kind}", "resource_type": "image" if ext in IMAGE_TYPES else "raw"}
    if ext in IMAGE_TYPES:
        options["transformation"] = {"width": 800, "height": 800, "crop": "limit"}
    try:
        return cloudinary.uploader.upload(file, **options)["secure_url"]
    except Exception as e:
        current_app.logger.error("Cloudinary failed: %s", e)
        raise ApiError("Upload failed, please try again later", 502)


def send_deadline_reminders(days=2):
    """Email verified contractors who have not bid on open tenders closing within days. Returns emails sent."""
    closing = Tender.query.filter(Tender.status == "open", Tender.deadline_date.between(now(), now() + timedelta(days=days))).all()
    contractors = User.query.filter_by(role="contractor", is_verified=True).all()
    sent = 0
    for tender in closing:
        already_bid = {b.bidder_id for b in tender.bids}
        for user in contractors:
            if user.id not in already_bid:
                send_email(user.email, f"Deadline approaching: {tender.title}", f"This tender closes {TenderOut().dump(tender)['deadline_date']}.")
                sent += 1
    return sent
