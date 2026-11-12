from flask import Blueprint, jsonify, request

from .. import services
from ..extensions import db
from ..utils import ApiError, roles_required

bp = Blueprint("uploads", __name__, url_prefix="/api/uploads")
