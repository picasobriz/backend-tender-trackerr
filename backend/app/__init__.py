import os

from flasgger import Swagger
from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from . import services
from .config import Config
from .extensions import db, jwt
from .routes import blueprints
from .utils import ApiError


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    Swagger(app, template_file=os.path.join(app.root_path, "..", "openapi.yaml"))  # docs at /apidocs

    for bp in blueprints:
        app.register_blueprint(bp)

    # --- friendly JSON errors everywhere ---
    @app.errorhandler(ApiError)
    def api_error(e):
        return jsonify(error=e.message, details=e.details), e.status

    @app.errorhandler(IntegrityError)
    def integrity_error(e):
        db.session.rollback()
        return jsonify(error="That record already exists or breaks a data rule", details={}), 409

    @app.errorhandler(HTTPException)
    def http_error(e):
        return jsonify(error=e.description, details={}), e.code

    @app.errorhandler(Exception)
    def server_error(e):
        db.session.rollback()
        app.logger.exception(e)
        return jsonify(error="Something went wrong on our side", details={}), 500

    jwt.unauthorized_loader(lambda reason: (jsonify(error="Login required", details={}), 401))
    jwt.invalid_token_loader(lambda reason: (jsonify(error="Invalid token, please log in again", details={}), 401))
    jwt.expired_token_loader(lambda header, payload: (jsonify(error="Session expired, please log in again", details={}), 401))

    @app.cli.command("send-reminders")
    def send_reminders():
        """Run daily (cron): flask send-reminders"""
        print(f"{services.send_deadline_reminders()} reminder(s) sent")

    with app.app_context():
        db.create_all()
    return app
