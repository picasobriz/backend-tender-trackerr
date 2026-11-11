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
    import cloudinary.uploader

def upload_file(file_storage, folder="documents"):
    """Upload a file to Cloudinary with extension and size checks."""
    if not file_storage or not file_storage.filename:
        raise ApiError("No file provided", 400)
    
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_TYPES:
        raise ApiError(f"File type .{ext} is not allowed. Allowed types: {', '.join(ALLOWED_TYPES)}", 400)
    
    # Check size via file pointer
    file_storage.seek(0, os.SEEK_END)
    size_bytes = file_storage.tell()
    file_storage.seek(0)
    
    if size_bytes > MAX_MB * 1024 * 1024:
        raise ApiError(f"File is too large. Max size is {MAX_MB}MB", 413)
    
    try:
        upload_result = cloudinary.uploader.upload(file_storage, folder=folder)
        return upload_result.get("secure_url")
    except Exception as e:
        raise ApiError(f"File upload failed: {str(e)}", 500)