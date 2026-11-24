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