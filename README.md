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

- **Language / runtime**: Python 3.x (Backend), Node.js (Frontend)
- **Framework / libraries**: APIFlask (Backend RESTful API), Vue 3 + Vite + Vue Router (Frontend)
- **Persistence**: SQLite (`taskmaster.db`) interacted via SQLAlchemy 2.0 ORM.
- **Containerization**: Docker & Docker Compose (for production deployments).

## Prerequisites

- **Python 3.10+** (For backend API operations)
- **Node.js LTS** (For frontend Vue dependencies)
- **Docker** (Optional, for running production-grade deployments through `docker-compose`)

## How to run locally

### Backend (APIFlask)
```bash
# Navigate to the project root
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
*Note: The backend will run on `http://127.0.0.1:5000` by default. Database configurations are managed automatically via `config.py`.*

### Frontend (Vue 3)
```bash
cd frontend
npm install
npm run dev
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

| Artifact | Where |
|----------|--------|
| **Risk report** | [docs/RISK_REPORT.md](./docs/RISK_REPORT.md) |
| **Refactoring & complexity report** | *(To be added / Please link file here)* |
| **Issue board** | [GitLab Issue Board](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/boards) |
| **Team contract** | [docs/team-contract.md](./docs/team-contract.md) |
| **Meeting notes** | [GitLab Wiki](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/wikis/home) |
| **Sprint 3 group retrospective** | *(To be added / Please link file here)* |

## Repository layout

- `modules/` - Domain-driven backend structure separated by domains (`tasks`, `users`). Contains routes, services, schemas, and models.
- `frontend/` - Independent Vue 3 + Vite SPA frontend code.
- `docs/` - Contains our Risk Reports and other engineering documentations.
- `tests/` - Comprehensive Pytest suites for testing backend functionality.
- `Dockerfile` / `docker-compose.yml` - Container environments for straightforward deployment.

## Team & course

- **Course**: COMP9820 — 26T1
- **Group**: T09A-B
