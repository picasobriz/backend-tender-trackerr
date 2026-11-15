from .auth import bp as auth_bp
from .bids import bp as bids_bp
from .dashboard import bp as dashboard_bp
from .tenders import bp as tenders_bp
from .uploads import bp as uploads_bp

blueprints = [auth_bp, tenders_bp, bids_bp, uploads_bp, dashboard_bp]
