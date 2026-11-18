import hmac
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from .. import services
from ..extensions import db
from ..models import User
from ..schemas import (
    LoginIn,
    RegisterIn,
    UserOut,
    VerifyIn,
    ForgotPasswordIn,
    ResetPasswordIn,
)
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
@bp.post("/forgot-password")
def forgot_password():
    d = load(ForgotPasswordIn, request.get_json(silent=True))
    email = d["email"].lower()

    user = User.query.filter_by(email=email).first()

    if user:
        token = services.make_password_reset_token(user)

        services.send_email(
            user.email,
            "Reset your TenderTrack password",
            (
                "We received a request to reset your TenderTrack password.\n\n"
                f"Your password reset token is:\n\n{token}\n\n"
                "This token expires in 30 minutes.\n"
                "If you did not request this, ignore this email."
            ),
        )

    return jsonify(
        message="If an account exists with that email, password reset instructions will be sent."
    ), 200
@bp.post("/reset-password")
def reset_password():
    d = load(ResetPasswordIn, request.get_json(silent=True))

    payload = services.read_password_reset_token(d["token"])

    if not isinstance(payload, dict) or not isinstance(payload.get("email"), str):
        raise ApiError("Invalid or expired password reset token", 400)

    user = User.query.filter_by(email=payload["email"]).first()

    if not user:
        raise ApiError("Invalid or expired password reset token", 400)

    if not hmac.compare_digest(
        payload.get("fingerprint", ""),
        services.password_reset_fingerprint(user),
    ):
        raise ApiError("Invalid or expired password reset token", 400)

    user.set_password(d["password"])
    db.session.commit()

    return jsonify(
        message="Password successfully reset. You can now log in with your new password."
    ), 200
