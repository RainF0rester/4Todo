# Development Setup

## Prerequisites

- Python 3.x
- Node.js & npm

## Backend

The backend is built with [APIFlask](https://apiflask.com/) (Flask-based). Run the following from the **project root**:

```bash
# Install dependencies (first time only)
pip install -r backend/requirements.txt

# Start with hot reload
flask --app backend.app:create_app run --debug --port 5000
```

The server will be available at `http://localhost:5000`.

> **Note:** Always run from the project root directory, not from inside `backend/`, because imports use the `backend.*` package namespace.

## Frontend

The frontend is built with [Vue 3](https://vuejs.org/) + [Vite](https://vite.dev/). Run the following from the `frontend/` directory:

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server with hot reload
npm run dev
```

The dev server will be available at `http://localhost:5173` (default Vite port).
