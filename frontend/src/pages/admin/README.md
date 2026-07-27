# CodeMind DNA

CodeMind DNA is a final-year engineering project that is evolving into an AI-powered coding behavior and talent intelligence platform. Phase 2 adds a problem bank, coding arena experience, admin problem management, and draft auto-save while preserving the existing authentication and role-based access flow.

## Phase 2 highlights
- Student problem bank with search, filtering, and pagination
- Student coding arena with Monaco editor, language selection, sample test cases, and draft auto-save
- Admin problem management for creating and editing problems and adding sample or hidden test cases
- Backend APIs for listing, viewing, drafting, and managing coding problems
- Development seed data for multiple original problems

## Architecture overview
- Backend: FastAPI + SQLAlchemy + Alembic + Pydantic
- Frontend: React + Vite + React Router + Tailwind CSS + Monaco Editor
- Database: PostgreSQL

## Folder structure
- backend/app for API, models, schemas, services, repositories, and core config
- backend/alembic for database migrations
- frontend/src for UI pages, auth context, routes, and dashboard layouts

## PostgreSQL setup
Create a database:

```bash
createdb codemind_dna
```

## Backend setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Update the local database URL in the backend environment if needed.

## Frontend setup
```bash
cd frontend
npm install
```

## Migration commands
```bash
cd backend
alembic upgrade head
```

## Seed development problems
```bash
cd backend
.venv\Scripts\python -c "from app.scripts.seed_problems import seed_problems; seed_problems()"
```

## Run locally
Backend:
```bash
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open in browser:
- http://localhost:8000
- http://127.0.0.1:8000

Frontend:
```bash
cd frontend
npm run dev
```
Open in browser:
- http://localhost:5173

## Key APIs
- GET /api/problems
- GET /api/problems/{slug}
- GET /api/problems/{problem_id}/draft?language=python
- PUT /api/problems/{problem_id}/draft
- POST /api/admin/problems
- POST /api/admin/problems/{problem_id}/test-cases

## Accessing the new experience
- Students can visit /student/problems to browse coding problems.
- Clicking a problem opens /student/problems/:slug for the coding arena experience.
- Admins can visit /admin/problems to create and manage problems.

## Draft auto-save behavior
Drafts save automatically after you stop typing for approximately 1-2 seconds, and the latest saved draft is restored when the same problem and language are reopened.

## Current Phase 2 limitation
Code execution and hidden test evaluation are intentionally not implemented in this phase. The Run Code and Submit Code buttons surface the upcoming workflow without simulating execution results.

## Testing
```bash
cd backend
pytest -q
```
