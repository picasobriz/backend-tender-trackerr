from flask import Blueprint, jsonify

from ..extensions import db

bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")
