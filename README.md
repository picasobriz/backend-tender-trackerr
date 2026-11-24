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