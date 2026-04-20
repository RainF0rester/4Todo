# Task Tracker (COMP9820)

A web-based modern task management application, designed for users to intuitively manage their to-dos, keep track of due dates, and securely organize their daily routines.

## What this project does

- **User / context**: Individuals, students, and professionals looking for a simple yet feature-rich daily task tracking tool with secure authentication capabilities.
- **Problem**: Solves the problem of forgotten tasks and poorly managed schedules by centralizing tasks with pinning, due dates, and auto-cleanup mechanisms.
- **Stories**: 
  - User Registration and Login.
  - CRUD operations for Task entries (Create, Read, Update, Delete).
  - Pinning critical tasks to the top.
  - Scheduled auto-deletion / soft deletion for expired tasks.
  - Setting and tracking Task Due Times.

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + Ant Design Vue + Vite |
| Backend | Python + APIFlask |
| Database | SQLite + SQLAlchemy |
| Deployment | Docker + Nginx + Gunicorn + Supervisor |
| CI/CD | GitLab CI/CD + GitLab Runner |

## Prerequisites

- **Python 3.10+** (For backend API operations)
- **Node.js LTS** (For frontend Vue dependencies)
- **Docker** (For running production-grade deployments through `docker-compose`)

## How to run it

Getting started is simple. Just run:

```bash
bash deploy.sh
```

## How to run tests and checks

```bash
# Ensure you are at the project root and venv is activated
pytest tests/
```
*Test coverage is accessible via the `.coverage` tooling and generated reports such as `coverage.xml`.*

## CI pipeline

Our CI pipeline executes on GitLab natively via `.gitlab-ci.yml`. On every merge request / push to `main`, it spins up a testing environment to validate code integrity and executes all `pytest` suites to ensure backward compatibility and feature safety.

## Where to find project evidence

| Artifact | Where                                                                                                                                                                                           |
|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Risk report** | [docs/RISK_REPORT.md](./docs/RISK_REPORT.md)                                                                                                                                                    |
| **Refactoring & complexity report** | [docs.COMPLEXITY_REPORT.md](./docs/COMPLEXITY_REPORT.md)                                                                                                                                        |
| **Issue board** | [GitLab Issue Board](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/boards)                                                                                |
| **Team contract** | [docs/team-contract.md](./docs/team-contract.md)                                                                                                                                                |
| **Meeting notes** | [GitLab Wiki](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/wikis/home)                                                                                   |
| **Sprint 3 group retrospective** | [Sp3 Retrospective](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/wikis/home/Sp3-Retrospective) |

## Repository layout

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

## Team & course

- **Course**: COMP9820 — 26T1
- **Group**: T09A-B
