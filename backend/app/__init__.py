import os
from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import db, jwt


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    return app