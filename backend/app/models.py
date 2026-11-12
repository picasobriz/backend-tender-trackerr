from datetime import datetime, timezone
from .extensions import db

def now():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False, default='contractor')
    created_at = db.Column(db.DateTime, default=now)

class Tender(db.Model):
    __tablename__ = 'tenders'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='open')
    budget = db.Column(db.Float)
    deadline_date = db.Column(db.DateTime)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=now)

class Bid(db.Model):
    __tablename__ = 'bids'
    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.Integer, db.ForeignKey('tenders.id'), nullable=False)
    bidder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    proposal = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default='pending')
    submitted_at = db.Column(db.DateTime, default=now)
    created_at = db.Column(db.DateTime, default=now)

    tender = db.relationship('Tender', backref=db.backref('bids', lazy=True))
    bidder = db.relationship('User', backref=db.backref('bids', lazy=True))
