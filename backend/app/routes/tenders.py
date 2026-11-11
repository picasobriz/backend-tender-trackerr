from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Tender
from ..schemas import STATUSES, TenderIn, TenderOut
from ..utils import ApiError, find, load, paginate, roles_required

bp = Blueprint("tenders", __name__, url_prefix="/api/tenders")


def own(user, tender):
    if tender.created_by_id != user.id:
        raise ApiError("You can only manage tenders you created", 403)