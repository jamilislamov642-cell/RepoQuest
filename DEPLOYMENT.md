# Production deployment

## Vercel frontend
1. Import this repository into Vercel.
2. Set the project root to `frontend`.
3. Set `NEXT_PUBLIC_API_URL` to the public HTTPS URL of the backend.
4. Deploy with `npm install` and `npm run build`.

## Render or Railway backend
- Render: use `render.yaml` or deploy `backend/Dockerfile`.
- Railway: use `railway.json` and set the service root/context as the repository root.
- Configure `/health` as the health check.
- Set `FRONTEND_URL`, `API_URL`, `GITHUB_TOKEN`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `OPENAI_API_KEY`, and `OPENAI_MODEL` as secrets.

## Persistence warning
The current SQLite history database is suitable for an MVP and requires persistent storage. Render is configured with a persistent disk. For horizontal scaling or Railway replicas, migrate `backend/app/db.py` to PostgreSQL and use a managed database.

## OAuth
GitHub callback URL:
`https://YOUR_BACKEND_DOMAIN/api/auth/github/callback`

Never commit secrets. Use HTTPS in production and change the session cookie to `secure=True` when deployed.
