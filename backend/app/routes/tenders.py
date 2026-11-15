from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Tender
from ..schemas import STATUSES, TenderIn, TenderOut
from ..utils import ApiError, find, load, paginate, roles_required

bp = Blueprint("tenders", __name__, url_prefix="/api/tenders")


def own(user, tender):
    if tender.created_by_id != user.id:
        raise ApiError("You can only manage tenders you created", 403)
    
@bp.get("")
@roles_required()
def list_tenders(user):
    status, category = request.args.get("status"), request.args.get("category")
    if status and status not in STATUSES:
        raise ApiError(f"status must be one of: {', '.join(STATUSES)}")
    if user.role == "auditor":
        status = "awarded"
    elif user.role == "contractor":
        status = status or "open"
    query = Tender.query.order_by(Tender.created_at.desc())
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter(Tender.category.ilike(category))
    return jsonify(paginate(query, TenderOut)) 

@bp.get("/<int:tender_id>")
@roles_required()
def get_tender(user, tender_id):
    tender = find(Tender, tender_id)
    if user.role == "auditor" and tender.status != "awarded":
        raise ApiError("Auditors can only view awarded tenders", 403)
    return jsonify(TenderOut().dump(tender))

@bp.post("")
@roles_required("admin")
def create_tender(user):
    tender = Tender(**load(TenderIn, request.get_json(silent=True)), created_by_id=user.id)
    db.session.add(tender)
    db.session.commit()
    return jsonify(TenderOut().dump(tender)), 201

@bp.patch("/<int:tender_id>")
@roles_required("admin")
def update_tender(user, tender_id):
    tender = find(Tender, tender_id)
    own(user, tender)
    for key, value in load(TenderIn, request.get_json(silent=True), partial=True).items():
        setattr(tender, key, value)
    db.session.commit()
    return jsonify(TenderOut().dump(tender))

@bp.delete("/<int:tender_id>")
@roles_required("admin")
def delete_tender(user, tender_id):
    tender = find(Tender, tender_id)
    own(user, tender)
    db.session.delete(tender)
    db.session.commit()
    return "", 204