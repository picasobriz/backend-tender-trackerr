# TenderTrack Backend

TenderTrack is a tender management and bidding system built with Python and Flask. It provides a REST API that allows administrators to publish and manage tenders, contractors to browse available opportunities and submit bids, and auditors to access awarded tender information.

The backend handles the application's main business operations, authentication, authorization, database communication, file uploads, email notifications and validation. It communicates with the frontend through HTTP requests and JSON responses.

*Live API:* https://backend-tender-trackerr.onrender.com

*API Documentation:* https://backend-tender-trackerr.onrender.com/apidocs/

*GitHub Repository:* https://github.com/picasobriz/backend-tender-trackerr

---

## Project Overview

TenderTrack is designed around three main user roles:

- **Admin**
  - Creates and publishes tenders.
  - Views and manages tenders they have created.
  - Receives bids submitted by contractors.
  - Reviews submitted bids.
  - Accepts or rejects contractor proposals.
  - Views dashboard statistics relating to their tenders.

- **Contractor**
  - Creates an account and verifies their email.
  - Logs into the system.
  - Views available tenders.
  - Submits proposals for open tenders.
  - Uploads supporting bid documents.
  - Tracks submitted bids and their statuses.
  - Views upcoming tender deadlines on their dashboard.

- **Auditor**
  - Logs into the system.
  - Views awarded tenders.
  - Accesses information about awarded projects.
  - Views statistics relating to awarded tenders and their values.

  The backend enforces these roles to ensure that users can only perform operations permitted by their account type.

## Technologies and Dependencies

The project uses the following technologies:

- **Python**: Main programming language used to develop the backend.
- **Flask**: Web framework responsible for handling HTTP requests and API routes.
- **Flask Blueprints**: Organize the API into separate functional modules.
- **Flask-SQLAlchemy**: Handles database communication through Python models and queries.
- **PostgreSQL**: Production relational database hosted on Neon.
- **SQLite**: Default local database when no database URL is configured.
- **Flask-JWT-Extended**: Handles JWT authentication and protected routes.
- **Marshmallow**: Validates incoming request data and structures outgoing responses.
- **Flask-Migrate and Alembic**: Provide database migration support.
- **Flask-CORS**: Allows the frontend to communicate with the backend from a different origin.
- **Flasgger and OpenAPI**: Provide interactive Swagger API documentation.
- **Werkzeug Security**: Handles secure password hashing and password verification.
- **Resend**: Handles email delivery for verification, password resets and notifications.
- **Cloudinary**: Stores uploaded images and documents.
- **Gunicorn**: Runs the Flask application in the production environment.
- **Pytest**: Used to test the backend functionality.

## Project Structure

The repository separates the backend application from the repository's root configuration files.

```text
backend-tender-trackerr/
|
|-- .env.example
|-- .gitignore
|-- Pipfile
|-- Pipfile.lock
|-- README.md
|
`-- backend/
    |
    |-- app/
    |   |-- __init__.py
    |   |-- config.py
    |   |-- extensions.py
    |   |-- models.py
    |   |-- schemas.py
    |   |-- services.py
    |   |-- utils.py
    |   |
    |   `-- routes/
    |       |-- __init__.py
    |       |-- auth.py
    |       |-- bids.py
    |       |-- dashboard.py
    |       |-- tenders.py
    |       `-- uploads.py
    |
    |-- tests/
    |   |-- conftest.py
    |   |-- test_app.py
    |   |-- test_auth.py
    |   |-- test_bids.py
    |   |-- test_dashboard.py
    |   |-- test_services.py
    |   |-- test_tenders.py
    |   |-- test_uploads.py
    |   `-- test_utils.py
    |
    |-- .env.example
    |-- db_diagram.png
    |-- openapi.yaml
    |-- pytest.ini
    |-- requirements.txt
    |-- run.py
    |-- seed.py
    `-- test_schemas.py
```

### Main Application Files

- `run.py`
  - Entry point used to start the Flask application.
  - Imports `create_app()` and creates the Flask application instance.
  - Gunicorn uses the application instance named `app` when starting the deployed service.

- `app/__init__.py`
  - Contains the application factory called `create_app()`.
  - Creates and configures the Flask application.
  - Initializes the database, JWT manager, migrations and CORS.
  - Configures Cloudinary and Swagger.
  - Registers all five Blueprints.
  - Defines centralized error handlers.
  - Creates database tables when the application starts.

- `config.py`
  - Loads environment variables.
  - Configures application security keys.
  - Configures the database connection.
  - Sets JWT expiration.
  - Configures email and Cloudinary settings.
  - Provides a separate configuration for testing.

- `extensions.py`
  - Creates reusable Flask extensions.
  - Defines the SQLAlchemy database instance and JWT manager.

- `models.py`
  - Defines the database tables and their relationships.
  - Contains the User, Tender and Bid models.
  - Provides password hashing and password verification methods.

- `schemas.py`
  - Validates incoming data before it reaches the database.
  - Checks required fields, data types, string lengths, dates, amounts and allowed values.
  - Controls the structure of API responses.
  - Prevents sensitive information such as password hashes from appearing in normal user responses.

- `utils.py`
  - Contains reusable application functions.
  - Handles request validation, record retrieval, pagination, API errors and role-based authorization.

- `services.py`
  - Contains operations that interact with external services.
  - Handles email verification tokens, password reset tokens, Resend email delivery, Cloudinary uploads and tender deadline reminders.