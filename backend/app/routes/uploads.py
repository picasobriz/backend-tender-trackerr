from flask import Blueprint, jsonify, request

from .. import services
from ..extensions import db
from ..utils import ApiError, roles_required

bp = Blueprint("uploads", __name__, url_prefix="/api/uploads")


@bp.post("")
@roles_required()
def upload(user):
    """multipart form: file=<file>, kind=logo|cover|bid. Returns the Cloudinary URL to put in your next request."""
    pass
