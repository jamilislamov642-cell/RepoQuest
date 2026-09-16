# RepoQuest

RepoQuest turns any GitHub repository into a guided contribution adventure.

## What it does
- Analyze a public GitHub repo in seconds
- Detect architecture, key modules, and likely entry points
- Generate a contributor-ready quest board
- Highlight priority files and low-risk onboarding paths
- Answer repo questions in plain English

## Why it stands out
Most developers don’t need another generic repo analyzer. They need a way to understand a codebase quickly and confidently contribute.

RepoQuest turns repo exploration into a guided, approachable workflow.

## Tech stack
- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- GitHub API: repo metadata, tree, and file insights
- Architecture: lightweight rule-based analysis + optional OpenAI API integration

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
```text
https://github.com/vercel/next.js
```

## Demo vision
Users paste a repo URL and instantly see:
- architecture overview
- likely entry points
- contributor-friendly tasks
- repo-specific Q&A

## Future enhancements
- repo graph visualization
- markdown report export
- GitHub App integration
- PR analysis and change summaries
- repository comparison mode
- shareable public repo pages

## License
MIT
