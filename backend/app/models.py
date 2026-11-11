from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def now():
    """Naive UTC time, so it compares cleanly with values read back from the DB."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("admin", "contractor", "auditor", name="user_role"), nullable=False, default="contractor")
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    company_logo_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)