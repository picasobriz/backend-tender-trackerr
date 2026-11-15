import os
import secrets

from dotenv import load_dotenv

load_dotenv()  # reads backend/.env, so python run.py and gunicorn see the same settings


def database_url(raw):
    """No DATABASE_URL -> local SQLite file (instant start). Fixes the 'postgres://' prefix some hosts hand out."""
    return raw.replace("postgres://", "postgresql://", 1) if raw else "sqlite:///tendertrack.db"


class Config:
    # Use cryptographically secure 32+ byte defaults if environment variables aren't provided
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # seconds
    SQLALCHEMY_DATABASE_URI = database_url(os.getenv("DATABASE_URL"))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")  # set to your frontend URL in production
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    MAIL_FROM = os.getenv("MAIL_FROM", "no-reply@tendertrack.com")
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SENDGRID_API_KEY = None
    CLOUDINARY_CLOUD_NAME = "test_cloud"
    CLOUDINARY_API_KEY = "test_key"
    CLOUDINARY_API_SECRET = "test_secret"