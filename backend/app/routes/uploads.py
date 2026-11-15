from flask import Blueprint, jsonify, request

from .. import services
from ..extensions import db
from ..utils import ApiError, roles_required

bp = Blueprint("uploads", __name__, url_prefix="/api/uploads")


@bp.post("")
@roles_required()
def upload(user):
    """Multipart form: file=<file>, kind=logo|cover|bid. Returns the Cloudinary URL."""
    file = request.files.get("file")
    kind = request.form.get("kind", "")

    if not file or not file.filename:
        raise ApiError("No file received. Send it as multipart form field 'file'", 400)
    if kind not in ("logo", "cover", "bid"):
        raise ApiError("kind must be one of: logo, cover, bid", 400)

    url = services.upload_file(file, kind)

    if kind == "logo":
        try:
            user.company_logo_url = url
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ApiError("Failed to save logo URL to profile", 500) from e

    return jsonify(url=url), 201
