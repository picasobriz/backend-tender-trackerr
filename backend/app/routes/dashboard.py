from flask import Blueprint, jsonify

from ..extensions import db
from ..models import Bid, Tender, now
from ..schemas import TenderOut
from ..utils import roles_required

bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@bp.get("")
@roles_required()
def dashboard(user):
    """Each role gets its own numbers."""
    if user.role == "admin":
        mine = Tender.query.filter_by(created_by_id=user.id)
        received = Bid.query.join(Tender).filter(Tender.created_by_id == user.id)
        data = {"tenders_created": mine.count(), "open_tenders": mine.filter_by(status="open").count(),
                "proposals_received": received.count(), "pending_review": received.filter(Bid.status == "pending").count()}
    elif user.role == "contractor":
        mine = Bid.query.filter_by(bidder_id=user.id)
        upcoming = Tender.query.filter(Tender.status == "open", Tender.deadline_date > now()).order_by(Tender.deadline_date).limit(5).all()
        data = {"my_bids": mine.count(), "pending": mine.filter_by(status="pending").count(),
                "accepted": mine.filter_by(status="accepted").count(), "upcoming_deadlines": TenderOut(many=True).dump(upcoming)}
    else:
        total = db.session.query(db.func.coalesce(db.func.sum(Tender.budget), 0)).filter(Tender.status == "awarded").scalar()
        data = {"awarded_tenders": Tender.query.filter_by(status="awarded").count(), "total_awarded_value": float(total),
                "bids_on_awarded": Bid.query.join(Tender).filter(Tender.status == "awarded").count()}
    return jsonify(role=user.role, **data)
