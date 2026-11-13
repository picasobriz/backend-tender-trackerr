"""Create the first admin (admins cannot self-register): python seed.py"""
from app import create_app
from app.extensions import db
from app.models import User

app = create_app()
with app.app_context():
    if not User.query.filter_by(email="admin@tendertrack.com").first():
        admin = User(name="Procurement Admin", email="admin@tendertrack.com", role="admin", is_verified=True)
        admin.set_password("admin12345")
        db.session.add(admin)
        db.session.commit()
    print("Admin ready: admin@tendertrack.com / admin12345 (change this password)")
