# RepoQuest

RepoQuest turns any GitHub repository into a guided contribution adventure.

## What it does
- Analyze a public GitHub repository
- Detect likely architecture and entry points
- Generate a beginner-friendly contribution path
- Show quest ideas for contributors
- Provide a simple Q&A mode for understanding the repo

## Tech stack
- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- GitHub API: public repo metadata and file tree analysis

## Run locally

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs

## Example repo
https://github.com/vercel/next.js
