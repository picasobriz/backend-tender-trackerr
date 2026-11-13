from flask import Blueprint, jsonify, request

from .. import services
from ..extensions import db
from ..utils import ApiError, roles_required

bp = Blueprint("uploads", __name__, url_prefix="/api/uploads")


@bp.post("")
@roles_required()
def upload(user):
    """multipart form: file=<file>, kind=logo|cover|bid. Returns the Cloudinary URL to put in your next request."""
    file, kind = request.files.get("file"), request.form.get("kind", "")
    if not file or not file.filename:
        raise ApiError("No file received. Send it as multipart form field 'file'")
    if kind not in ("logo", "cover", "bid"):
        raise ApiError("kind must be one of: logo, cover, bid")
    url = services.upload_file(file, kind)
    if kind == "logo":
        user.company_logo_url = url
        db.session.commit()
    return jsonify(url=url), 201
