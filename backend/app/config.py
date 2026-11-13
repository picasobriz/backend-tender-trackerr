import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # seconds
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://picaspbriz:password@localhost:5432/tender_trackerr")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    MAIL_FROM = os.getenv("MAIL_FROM", "no-reply@tendertrack.com")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
