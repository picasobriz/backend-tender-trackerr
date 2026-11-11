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


class Tender(db.Model):
    __tablename__ = "tenders"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    budget = db.Column(db.Numeric(14, 2), nullable=False)
    description = db.Column(db.Text, nullable=False)
    deadline_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum("open", "closed", "awarded", name="tender_status"), nullable=False, default="open")
    cover_image_url = db.Column(db.String(500))
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=now)
    bids = db.relationship("Bid", backref="tender", cascade="all, delete-orphan")

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


class Tender(db.Model):
    __tablename__ = "tenders"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    budget = db.Column(db.Numeric(14, 2), nullable=False)
    description = db.Column(db.Text, nullable=False)
    deadline_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum("open", "closed", "awarded", name="tender_status"), nullable=False, default="open")
    cover_image_url = db.Column(db.String(500))
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=now)
    bids = db.relationship("Bid", backref="tender", cascade="all, delete-orphan")


class Bid(db.Model):
    __tablename__ = "bids"
    __table_args__ = (db.UniqueConstraint("tender_id", "bidder_id", name="one_bid_per_tender"),)
    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.Integer, db.ForeignKey("tenders.id"), nullable=False)
    bidder_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    proposed_amount = db.Column(db.Numeric(14, 2), nullable=False)
    proposal_text = db.Column(db.Text, nullable=False)
    document_url = db.Column(db.String(500))
    status = db.Column(db.Enum("pending", "accepted", "rejected", name="bid_status"), nullable=False, default="pending")
    submitted_at = db.Column(db.DateTime, default=now)
    bidder = db.relationship("User")
       