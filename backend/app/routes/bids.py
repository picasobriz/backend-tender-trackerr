from flask import Blueprint, jsonify, request

from .. import services
from ..extensions import db
from ..models import Bid, Tender, now
from ..schemas import BidIn, BidOut, ReviewIn
from ..utils import ApiError, find, load, paginate, roles_required

bp = Blueprint("bids", __name__, url_prefix="/api")


@bp.post("/tenders/<int:tender_id>/bids")
@roles_required("contractor")
def submit_bid(user, tender_id):
    tender = find(Tender, tender_id)
    if tender.status != "open":
        raise ApiError(f"This tender is {tender.status} and no longer accepts bids")
    if tender.deadline_date <= now():
        raise ApiError("The deadline for this tender has passed")
    if Bid.query.filter_by(tender_id=tender_id, bidder_id=user.id).first():
        raise ApiError("You have already bid on this tender", 409)
    bid = Bid(**load(BidIn, request.get_json(silent=True)), tender_id=tender_id, bidder_id=user.id)
    db.session.add(bid)
    db.session.commit()
    return jsonify(BidOut().dump(bid)), 201


@bp.get("/bids")
@roles_required("contractor", "admin")
def list_bids(user):
    """Contractors see their own bids; admins see proposals received on their tenders."""
    query = Bid.query.join(Tender).order_by(Bid.submitted_at.desc())
    query = query.filter(Bid.bidder_id == user.id) if user.role == "contractor" else query.filter(Tender.created_by_id == user.id)
    if request.args.get("tender_id", type=int):
        query = query.filter(Bid.tender_id == request.args.get("tender_id", type=int))
    return jsonify(paginate(query, BidOut))
