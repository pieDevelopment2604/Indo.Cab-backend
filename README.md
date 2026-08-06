# Indo.Cab B2B Rent a Car Platform

## Purpose

This is a B2B (Business-to-Business) Rent a Car Platform designed to connect vendors, drivers, and clients for car rental services. The platform handles booking management, vendor assignment, driver tracking, and billing.

## Tech Stack

- **Backend Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Caching**: Redis
- **Messaging**: MSG91 (for SMS notifications)
- **Maps**: MapMyIndia (for geocoding and route planning)
- **Deployment**: Docker & Docker Compose

Last updated: 05-08-2026
## Folder Structure

```
indocab-backend/
├── app/
│   ├── core/             # Core configurations (settings, security)
│   ├── db/               # Database setup and sessions
│   ├── models/           # SQLAlchemy database models
│   ├── schemas/          # Pydantic data schemas
│   ├── routes/           # FastAPI API routers (endpoints)
│   ├── services/         # Business logic and services
│   ├── tasks/            # Celery background tasks
│   └── main.py           # Application entrypoint
├── docker-compose.yml    # Multi-container setup
├── Dockerfile            # Application Dockerfile
├── tests/                # Unit and integration tests
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
└── .env                  # Environment variables
```