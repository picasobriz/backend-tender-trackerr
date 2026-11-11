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
    pass
