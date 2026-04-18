# 4Todo

## How to Run the Project

Getting started is simple. Just run:

```bash
bash deploy.sh
```

Access the app at `http://localhost:8080`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + Ant Design Vue + Vite |
| Backend | Python + APIFlask |
| Database | SQLite + SQLAlchemy |
| Deployment | Docker + Nginx + Gunicorn + Supervisor |
| CI/CD | GitLab CI/CD + GitLab Runner |

---

## Project Structure

```
tasktracker/
├── app.py                      # Flask application entry point
├── config.py                   # App configuration
├── db.py                       # Database setup
├── schema.sql                  # Database schema
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Python dev dependencies
├── modules/
│   ├── tasks/                  # Task module
│   │   ├── models.py           # Task data models
│   │   ├── repo.py             # Task database operations
│   │   ├── routes.py           # Task API routes
│   │   ├── schemas.py          # Task request/response schemas
│   │   └── service.py         # Task business logic
│   └── users/                  # User module
│       ├── models.py           # User data models
│       ├── repo.py             # User database operations
│       ├── routes.py           # User API routes
│       ├── schemas.py          # User request/response schemas
│       └── service.py         # User business logic
├── utils/
│   ├── auth_decorator.py       # Auth middleware
│   └── jwt_utils.py            # JWT utilities
├── tests/
│   ├── tasks/                  # Task unit tests
│   ├── users/                  # User unit tests
│   └── utils/                  # Utility unit tests
├── frontend/                   # Vue 3 frontend
│   ├── src/
│   │   ├── api/                # API calls
│   │   ├── components/         # Reusable Vue components
│   │   ├── views/              # Page views
│   │   ├── router/             # Vue Router config
│   │   └── stores/             # State management
│   ├── package.json
│   └── vite.config.js
├── docs/                       # Project documentation
├── Dockerfile                  # For non-China environments
├── Dockerfile.prod             # For China environments (with mirror sources)
├── docker-compose.yml          # Container orchestration
├── nginx.conf                  # Nginx configuration
├── supervisord.conf            # Supervisor configuration
├── deploy.sh                   # Deployment script
└── .gitlab-ci.yml              # CI/CD pipeline config
```

---

## How It All Works Together

**Request Flow:**
```
User Browser
    ↓
Nginx (port 8080)
    ↓
    ├── Static files (/, *.js, *.css)  →  Vue 3 Frontend
    │
    └── API requests (/api/*)
            ↓
        Gunicorn (port 5000, 4 workers)
            ↓
        APIFlask
            ↓
        SQLAlchemy → SQLite
```

---

