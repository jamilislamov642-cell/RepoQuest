from urllib.parse import quote

# Add `from urllib.parse import quote` to backend/app/main.py imports, then add:
#
# @app.get("/api/discover")
# def discover(q: str = "developer tools", page: int = 1):
#     query = q.strip() or "developer tools"
#     result = gh(f"https://api.github.com/search/repositories?q={quote(query)}&sort=stars&order=desc&per_page=18&page={max(1, min(page, 10))}")
#     return {"items": result.get("items", []), "total_count": result.get("total_count", 0)}
