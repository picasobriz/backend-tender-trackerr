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

  ## How the Backend Starts

The application follows an application factory pattern. This means that the Flask application is created and configured through a function instead of being configured entirely in one global file.

The startup process follows this order:

1. **The application starts**
   - Production starts the backend through Gunicorn.
   - Gunicorn loads `run.py`.
   - `run.py` imports `create_app()` from the application package.

2. **The application factory runs**
   - `create_app()` creates a Flask application instance.
   - The application loads its configuration from `config.py`.

3. **Extensions are initialized**
   - SQLAlchemy connects the application to the configured database.
   - Flask-Migrate initializes migration support.
   - Flask-JWT-Extended initializes token authentication.
   - Flask-CORS configures cross-origin communication.

4. **External services are configured**
   - Cloudinary receives its configuration.
   - Flasgger loads the OpenAPI specification for Swagger documentation.

5. **Blueprints are registered**
   - The application imports the five Blueprints from `routes/__init__.py`.
   - Each Blueprint registers its routes with Flask.

6. **Error handling is registered**
   - Application-specific errors are converted into JSON responses.
   - Database integrity errors are handled.
   - HTTP errors are returned in a consistent format.
   - Unexpected errors are logged and returned as HTTP 500 responses.

7. **Database tables are initialized**
   - The application enters its application context.
   - `db.create_all()` creates missing database tables.
   - Existing tables are not recreated or cleared.

8. **The application becomes available**
   - The Flask application instance is returned.
   - Gunicorn serves incoming HTTP requests.

This process ensures that the application's required components are initialized before it handles requests.

## The Five Flask Blueprints

TenderTrack uses five Flask Blueprints to separate its backend functionality into independent modules. Each Blueprint handles a specific area of the system.

### 1. Authentication Blueprint

File: `app/routes/auth.py`

URL prefix: `/api/auth`

The Authentication Blueprint manages user registration, login and account security.

Its responsibilities include:

- Registering contractors and auditors.
- Checking whether an email address is already registered.
- Hashing passwords before storing them.
- Sending email verification tokens.
- Verifying user accounts.
- Authenticating users during login.
- Generating JWT access tokens.
- Returning the authenticated user's profile.
- Requesting password resets.
- Validating password reset tokens.
- Updating user passwords.

Administrators are not allowed to register through the public registration endpoint. Their accounts are created using the administrative seeding script.

Available endpoints:

- `POST /api/auth/register`
- `POST /api/auth/verify`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/forgot-password`
- `POST /api/auth/reset-password`

### 2. Tenders Blueprint

File: `app/routes/tenders.py`

URL prefix: `/api/tenders`

The Tenders Blueprint manages tender creation, retrieval, updating and deletion.

Its responsibilities include:

- Creating new tenders.
- Retrieving available tenders.
- Retrieving individual tender information.
- Filtering tenders by status and category.
- Applying pagination to tender results.
- Updating existing tenders.
- Deleting tenders.
- Ensuring that only administrators can manage tenders they created.

Important business rules:

- Only administrators can create tenders.
- Only the administrator who created a tender can update or delete it.
- Contractors see open tenders by default.
- Auditors can only view awarded tenders.
- Administrators can view tenders across the system.

Available endpoints:

- `GET /api/tenders`
- `POST /api/tenders`
- `GET /api/tenders/{tender_id}`
- `PATCH /api/tenders/{tender_id}`
- `DELETE /api/tenders/{tender_id}`

### 3. Bids Blueprint

File: `app/routes/bids.py`

URL prefix: `/api`

The Bids Blueprint handles contractor proposals and administrator bid reviews.

Its responsibilities include:

- Allowing contractors to submit bids for tenders.
- Checking whether a tender is still open.
- Checking whether the tender deadline has passed.
- Preventing a contractor from submitting multiple bids for the same tender.
- Retrieving bids submitted by contractors.
- Allowing administrators to view proposals received on their own tenders.
- Allowing administrators to accept or reject bids.
- Updating tender status when a bid is accepted.
- Sending email notifications after a bid is reviewed.

Important business rules:

- Only contractors can submit bids.
- A bid can only be submitted while the tender is open.
- The deadline must not have passed.
- A contractor can only submit one bid per tender.
- Only the administrator who owns the tender can review its bids.
- Accepting a bid changes its tender status to awarded.
- An already awarded tender cannot be awarded again.

Available endpoints:

- `POST /api/tenders/{tender_id}/bids`
- `GET /api/bids`
- `PATCH /api/bids/{bid_id}`

### 4. Dashboard Blueprint

File: `app/routes/dashboard.py`

URL prefix: `/api/dashboard`

The Dashboard Blueprint provides information and statistics based on the authenticated user's role.

Its responsibilities include:

- Retrieving administrator statistics.
- Retrieving contractor bidding statistics.
- Retrieving auditor statistics.
- Displaying upcoming tender deadlines for contractors.

The information returned depends on the user's role.

Administrators receive:

- Number of tenders created.
- Number of open tenders.
- Number of proposals received.
- Number of bids awaiting review.

Contractors receive:

- Total bids submitted.
- Pending bids.
- Accepted bids.
- Upcoming open tender deadlines.

Auditors receive:

- Number of awarded tenders.
- Total value of awarded tenders.
- Number of bids associated with awarded tenders.

Available endpoint:

- `GET /api/dashboard`

## Database Design

TenderTrack uses SQLAlchemy models to represent its relational database structure.

The main database tables are:

### Users

The `users` table stores information about registered users.

Important fields:

- `id` - Unique user identifier.
- `name` - User's name.
- `email` - Unique email address.
- `password_hash` - Securely hashed password.
- `role` - Admin, contractor or auditor.
- `is_verified` - Indicates whether the account has been verified.
- `company_logo_url` - Stores the company logo URL.
- `created_at` - Account creation timestamp.

Passwords are never stored as plain text. The application uses Werkzeug's password hashing functions to generate and verify password hashes.

### Tenders

The `tenders` table stores tender information created by administrators.

Important fields:

- `id` - Unique tender identifier.
- `title` - Tender title.
- `category` - Tender category.
- `budget` - Available tender budget.
- `description` - Tender description.
- `deadline_date` - Tender closing date and time.
- `status` - Open, closed or awarded.
- `cover_image_url` - Optional tender cover image.
- `created_by_id` - References the administrator who created the tender.
- `created_at` - Tender creation timestamp.

Each tender belongs to one user through `created_by_id`.

A tender can also have multiple associated bids.

### Bids

The `bids` table stores contractor proposals submitted against tenders.

Important fields:

- `id` - Unique bid identifier.
- `tender_id` - References the tender being bid on.
- `bidder_id` -References the contractor submitting the bid.
- `proposed_amount` - Amount proposed by the contractor.
- `proposal_text` - Description of the contractor's proposal.
- `document_url` - Optional supporting document URL.
- `status` - Pending, accepted or rejected.
- `submitted_at` - Bid submission timestamp.

A unique database constraint on `tender_id` and `bidder_id` prevents the same contractor from submitting more than one bid for a particular tender.

### Database Relationships

- One user can create multiple tenders.
- One tender belongs to the administrator who created it.
- One tender can receive multiple bids.
- One contractor can submit multiple bids across different tenders.
- Each bid belongs to one contractor and one tender.
- Deleting a tender also

