from flask import Blueprint, jsonify

from ..extensions import db
from ..models import Bid, Tender, now

bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")
