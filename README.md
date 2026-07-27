# CodeMind DNA

This repository contains the CodeMind DNA project (frontend + backend).

## Local development

Backend (Python/FastAPI)

- Create a virtual environment and install dependencies:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

- Run the backend:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (Vite/React)

```bash
cd frontend
npm ci
npm run dev
```

Open the app at `http://localhost:5173`.

## CI / Deploy (Render)

This repo includes GitHub Actions workflows to build and deploy the frontend and backend to Render.

Secrets required (add to GitHub repo Settings → Secrets):

- `RENDER_API_KEY` — Render API key with deploy permissions
- `RENDER_SERVICE_ID_FRONTEND` — Render service ID for the frontend static site
- `RENDER_SERVICE_ID_BACKEND` — Render service ID for the backend (Docker or web service)

Workflow triggers: pushes to `main` will build relevant packages and trigger Render deployments.

## Pushing changes

If you want me to push these changes, either give push access from this environment or run these commands locally:

```bash
git init
git add .
git commit -m "chore: add CI and deploy workflows"
git branch -M main
git remote add origin https://github.com/RaghuJ2411/Code-mind-dna.git
git push -u origin main
```

## Next steps I can take

- Create and commit GitHub Actions workflows (frontend + backend) for Render deploy.
- Create additional CI steps (tests, linters) on demand.
- Optionally push commits to your GitHub repo if you confirm I should.