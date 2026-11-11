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
def send_email(to: str, subject: str, body: str):
    """Send email via SendGrid or fallback to logging if not configured."""
    api_key = current_app.config.get("SENDGRID_API_KEY")
    if not api_key:
        print(f"Mock Email to {to}: {subject}\n{body}")
        return False
    
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    
    message = Mail(
        from_email=current_app.config.get("MAIL_FROM", "noreply@tendertrack.com"),
        to_emails=to,
        subject=subject,
        plain_text_content=body
    )
    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        return True
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False    