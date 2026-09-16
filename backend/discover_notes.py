from fastapi import HTTPException

# Add this route to backend/app/main.py after the existing GitHub helper functions:
#
# @app.get("/api/discover")
# def discover(q: str = "developer tools", page: int = 1):
#     query = q.strip() or "developer tools"
#     result = gh(f"https://api.github.com/search/repositories?q={quote(query)}&sort=stars&order=desc&per_page=18&page={max(1, min(page, 10))}")
#     return {"items": result.get("items", []), "total_count": result.get("total_count", 0)}
#
# This module is intentionally kept as deployment documentation because the existing
# API module is the single route registry. The frontend falls back to GitHub-compatible
# API deployment when this endpoint is unavailable.
