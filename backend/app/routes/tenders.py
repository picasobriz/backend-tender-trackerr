from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Tender
from ..schemas import STATUSES, TenderIn, TenderOut
from ..utils import ApiError, find, load, paginate, roles_required

bp = Blueprint("tenders", __name__, url_prefix="/api/tenders")


