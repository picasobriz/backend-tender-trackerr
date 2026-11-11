from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from .. import services
from ..extensions import db
from ..models import User
from ..schemas import LoginIn, RegisterIn, UserOut, VerifyIn
from ..utils import ApiError, load, roles_required

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
def register():
    d = load(RegisterIn, request.get_json(silent=True))
    d["email"] = d["email"].lower()
    if User.query.filter_by(email=d["email"]).first():
        raise ApiError("This email is already registered", 409)
    user = User(name=d["name"], email=d["email"], role=d["role"])
    user.set_password(d["password"])
    db.session.add(user)
    db.session.commit()
    services.send_email(user.email, "Verify your TenderTrack account", f"Your verification token:\n\n{services.make_token(user.email)}")
    return jsonify(message="Registered. Check your email for the verification token."), 201


@bp.post("/verify")
def verify():
    d = load(VerifyIn, request.get_json(silent=True))
    user = User.query.filter_by(email=services.read_token(d["token"])).first()
    if not user:
        raise ApiError("Account not found", 404)
    user.is_verified = True
    db.session.commit()
    return jsonify(message="Account verified. You can now log in.")


@bp.post("/login")
def login():
    d = load(LoginIn, request.get_json(silent=True))
    user = User.query.filter_by(email=d["email"].lower()).first()
    if not user or not user.check_password(d["password"]):
        raise ApiError("Invalid email or password", 401)
    if not user.is_verified:
        raise ApiError("Please verify your email before logging in", 403)
    return jsonify(token=create_access_token(identity=str(user.id)), user=UserOut().dump(user))


@bp.get("/me")
@roles_required()
def me(user):
    return jsonify(UserOut().dump(user))