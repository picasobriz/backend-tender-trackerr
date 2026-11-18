"""Create the first admin (admins cannot self-register)."""
import os

from app import create_app
from app.extensions import db
from app.models import User

name = os.getenv("ADMIN_NAME")
email = os.getenv("ADMIN_EMAIL", "").strip().lower()
password = os.getenv("ADMIN_PASSWORD")

if not name or not email or not password:
    raise SystemExit(
        "Set ADMIN_NAME, ADMIN_EMAIL and ADMIN_PASSWORD before running."
    )

if len(password) < 12:
    raise SystemExit("ADMIN_PASSWORD must contain at least 12 characters.")

app = create_app()

with app.app_context():
    existing = User.query.filter_by(email=email).first()

    if existing:
        if existing.role != "admin":
            raise SystemExit(
                "This email already belongs to a non-admin account. No changes made."
            )
        print("Admin account already exists. No changes made.")
    else:
        admin = User(
            name=name,
            email=email,
            role="admin",
            is_verified=True
        )
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print("Admin account created successfully.")
