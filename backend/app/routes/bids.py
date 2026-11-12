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
