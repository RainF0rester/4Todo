# 4Todo

A full-stack task management application with web and mobile clients, featuring AI-powered assistance, Pomodoro timer, and real-time updates.

## Features

- **User authentication** — JWT-based registration and login
- **Task management** — Create, read, update, delete tasks with pinning, due dates, and soft deletion
- **Pomodoro timer** — Built-in focus timer with session tracking
- **AI assistant** — Chat-based AI assistant powered by Claude (Anthropic)
- **Dashboard & analytics** — Task statistics with ECharts visualizations
- **Real-time updates** — WebSocket support via Socket.IO
- **Export** — Export tasks to Excel (xlsx)
- **Mobile app** — Cross-platform Flutter app (iOS & Android)

## Tech Stack

| Layer      | Technology                                          |
| ---------- | --------------------------------------------------- |
| Frontend   | Vue 3 + Ant Design Vue + Vite + ECharts             |
| Backend    | Python + APIFlask + SQLAlchemy + Redis + Socket.IO  |
| AI         | Anthropic Claude API                                |
| Database   | SQLite                                              |
| Mobile     | Flutter (iOS & Android)                             |
| Deployment | Docker + Nginx + Gunicorn + Supervisor              |
| CI/CD      | GitHub Actions + GitLab CI/CD                       |

## Prerequisites

- **Python 3.10+** (backend)
- **Node.js LTS** (frontend)
- **Flutter SDK** (mobile)
- **Docker** (production deployment)
- **Redis** (real-time features)

## Getting Started

### Development (Docker)

```bash
docker-compose -f docker-compose.dev.yml up
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Frontend only

```bash
cd frontend
npm install
npm run dev
```

### Backend only

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
flask run
```

### Mobile

```bash
cd mobile
flutter pub get
flutter run
```

## Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations. Migrations run automatically on app startup via `alembic upgrade head`.

### Create a new migration

After modifying any model, generate a migration script:

```bash
# Enter the backend container
docker exec -it todo-backend bash

# Auto-generate migration based on model changes
alembic -c backend/alembic.ini revision --autogenerate -m "describe your change"
```

Review the generated file in `backend/migrations/versions/` before committing.

### Apply migrations manually

```bash
docker exec -it todo-backend bash
alembic -c backend/alembic.ini upgrade head
```

### Roll back

```bash
alembic -c backend/alembic.ini downgrade -1
```

---

## Running Tests

```bash
# From project root, with venv activated
pytest backend/tests/
```

Test coverage is tracked via `.coverage` and `coverage.xml`.

## CI Pipeline

- **GitHub Actions** (`.github/workflows/ci.yml`) — runs on every push/PR to `main`: builds frontend and deploys to Cloudflare Pages, runs backend pytest suite
- **GitLab CI/CD** (`.gitlab-ci.yml`) — mirrors pipeline for GitLab environments

## Repository Layout

```text
4todo/
├── backend/                    # Python APIFlask backend
│   ├── app.py                  # Application entry point
│   ├── config.py               # App configuration
│   ├── db.py                   # Database setup
│   ├── schema.sql              # Database schema
│   ├── requirements.txt        # Python dependencies
│   ├── requirements-dev.txt    # Dev dependencies
│   ├── modules/
│   │   ├── ai/                 # AI assistant (Claude API + WebSocket)
│   │   ├── tasks/              # Task CRUD module
│   │   ├── users/              # User auth module
│   │   └── pomodoro/           # Pomodoro timer module
│   ├── utils/
│   │   ├── auth_decorator.py   # Auth middleware
│   │   └── jwt_utils.py        # JWT utilities
│   └── tests/                  # pytest test suites
├── frontend/                   # Vue 3 web frontend
│   ├── src/
│   │   ├── api/                # API client
│   │   ├── components/         # Reusable components
│   │   ├── views/              # Page views
│   │   ├── router/             # Vue Router config
│   │   ├── stores/             # Pinia state management
│   │   └── styles/             # Global styles
│   ├── package.json
│   └── vite.config.js
├── mobile/                     # Flutter mobile app (iOS & Android)
│   ├── lib/
│   │   └── main.dart
│   ├── android/
│   ├── ios/
│   └── pubspec.yaml
├── docs/                       # Project documentation
├── data/                       # SQLite database file
├── Dockerfile.backend          # Backend Docker image
├── docker-compose.dev.yml      # Dev environment
├── docker-compose.prod.yml     # Production environment
├── nginx.conf                  # Nginx configuration
├── supervisord.conf            # Supervisor configuration
├── .github/workflows/ci.yml    # GitHub Actions CI/CD
└── .gitlab-ci.yml              # GitLab CI/CD
```

## License

[MIT](LICENSE) © 2026 yulinliu

---

## Request Flow

```text
User Browser / Mobile App
        ↓
   Nginx (port 8080)
        ↓
        ├── Static files (/, *.js, *.css)  →  Vue 3 Frontend
        │
        └── API requests (/api/*)
                ↓
           Gunicorn (port 5000)
                ↓
           APIFlask
                ↓
           SQLAlchemy → SQLite
                ↓
           Redis (sessions / real-time pub-sub)
```
