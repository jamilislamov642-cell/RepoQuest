# Production deployment

1. Deploy `backend/` with `backend/Dockerfile` to Railway, Render, Fly.io, or another HTTPS container host.
2. Deploy `frontend/` to Vercel or a Node 20 container.
3. Set `NEXT_PUBLIC_API_URL`, `FRONTEND_URL`, and `API_URL` to the production HTTPS URLs.
4. Configure GitHub OAuth callback as `https://YOUR_API_DOMAIN/api/auth/github/callback`.
5. Set `GITHUB_TOKEN` for higher GitHub API rate limits and `OPENAI_API_KEY` for stronger answers.
6. Anonymous history is stored locally; authenticated multi-device history should use a database/session layer before production launch.

Never commit `.env` files or OAuth secrets.
