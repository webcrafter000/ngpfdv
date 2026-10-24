# Wind Forecast Decision Support Portal

A full-stack web application for UK energy utilities to compare day-ahead wind generation forecasts against actual outturns for January 2026.

## Files and Directories

- `backend/app/` — FastAPI application root (`main.py`, `db.py`, `models.py`, `config.py`)
- `backend/app/routers/` — API route handlers (`forecast.py`, `actuals.py`, `error.py`)
- `backend/app/services/` — Business logic (`latest_asof.py`, `actuals.py`, `error_calc.py`)
- `backend/app/ingest/` — Database schema and Elexon data ingest scripts (`schema.sql`, `fetch_fuelhh.py`, `fetch_windfor.py`)
- `backend/requirements.txt` — Python dependencies
- `backend/Dockerfile` — Container build configuration for FastAPI backend
- `frontend/src/` — React application source code (`App.tsx`, `api.ts`, charts, KPI components)
- `frontend/src/screens/` — UI view screens (`ForecastView.tsx`, `AccuracyView.tsx`)
- `frontend/package.json` — Frontend project dependencies and scripts
- `frontend/vite.config.ts` — Vite build and dev server configuration
- `frontend/Dockerfile` — Container build configuration for React/Vite frontend
- `docker-compose.yml` — Multi-container orchestration (PostgreSQL database, backend, frontend)
- `README.md` — Project documentation and setup instructions

## How to Start the Application

Exact commands in order:
1. `docker compose up -d --build`
2. Apply schema: `docker compose exec -T db psql -U postgres -d postgres < backend/app/ingest/schema.sql`
3. `docker compose exec backend python -m app.ingest.fetch_fuelhh`
4. `docker compose exec backend python -m app.ingest.fetch_windfor`
5. Open http://localhost:5173

See `.env.example` for environment variable configuration options.

## Live Deployment

- **Frontend (Vercel):** https://ngpfdv.vercel.app
- **Backend (Render):** https://ngpfdv.onrender.com
- **Database:** Render Postgres (managed)

Note: Backend was deployed on Render rather than Heroku because Heroku 
discontinued its free tier and entered sustaining-engineering mode in 
2026. Render provides equivalent Docker-based deployment and a managed 
Postgres database, satisfying the  deployment requirement.

## AI-Assisted Development Disclosure

This project was developed with the assistance of AI tools (Antigravity AI / Cursor). AI was used for boilerplate scaffolding, including FastAPI routers, React components, Dockerfiles, and `docker-compose.yml`. The core domain logic—including the latest-as-of SQL query with distinct-on semantics, gate-closure timezone logic, hourly actuals error calculation, and Elexon endpoint selection—was authored and verified by the developer. Every file change was verified directly on disk (`dir`/`ls`) to ensure changes were accurately committed.
