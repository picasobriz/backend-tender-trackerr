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
