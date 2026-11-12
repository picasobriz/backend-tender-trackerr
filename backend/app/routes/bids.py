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
