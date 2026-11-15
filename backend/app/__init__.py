from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import db, jwt
from .utils import ApiError


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    @app.errorhandler(ApiError)
    def handle_api_error(err):
        payload = {"error": err.message}
        if getattr(err, "details", None):
            payload["details"] = err.details
        return jsonify(payload), err.status_code

    @jwt.unauthorized_loader
    def handle_missing_token(_reason):
        return jsonify(error="Login required"), 401

    @jwt.invalid_token_loader
    def handle_invalid_token(reason):
        return jsonify(error=f"Invalid token: {reason}"), 401

    @jwt.expired_token_loader
    def handle_expired_token(_jwt_header, _jwt_payload):
        return jsonify(error="Token has expired"), 401

    from .routes.auth import bp as auth_bp
    from .routes.bids import bp as bids_bp
    from .routes.tenders import bp as tenders_bp
    from .routes.uploads import bp as uploads_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tenders_bp)
    app.register_blueprint(bids_bp)
    app.register_blueprint(uploads_bp)

    return app
