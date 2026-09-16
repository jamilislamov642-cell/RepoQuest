from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from urllib.parse import urlencode
from typing import Any
import httpx
import os
import re

from .db import (
    create_session_for_user,
    get_user_from_session,
    get_user_history,
    save_repo_history,
    upsert_user,
)

app = FastAPI(title="RepoQuest API", version="0.3.0")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


class RepoRequest(BaseModel):
    repo_url: str


class ChatRequest(BaseModel):
    repo_url: str
    question: str


class HistoryRequest(BaseModel):
    repo_url: str
    repo_name: str


class GitHubSessionRequest(BaseModel):
    repo_url: str


def parts(value: str):
    match = re.search(r"github\.com[:/]+([^/]+)/([^/#?]+)", value.strip().rstrip("/"))
    if not match:
        raise ValueError("Use a valid GitHub URL: https://github.com/owner/repo")
    return match.group(1), match.group(2).removesuffix(".git")


def gh(url: str) -> Any:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "RepoQuest"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = httpx.get(url, headers=headers, timeout=25)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"GitHub request failed ({response.status_code})")
    return response.json()


def analyze_url(url: str):
    owner, repo = parts(url)
    meta = gh(f"https://api.github.com/repos/{owner}/{repo}")
    branch = meta.get("default_branch", "main")
    tree = gh(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1")
    paths = [x["path"] for x in tree.get("tree", []) if x.get("type") == "blob" and x.get("path")]

    groups = {"entry_points": [], "core_files": [], "config_files": [], "docs_files": [], "tests_files": []}
    for path in paths:
        p = path.lower()
        if p.endswith((".md", ".rst", ".txt")):
            groups["docs_files"].append(path)
        elif any(x in p for x in ("test", "spec")) and p.endswith((".js", ".ts", ".tsx", ".py", ".go", ".rs")):
            groups["tests_files"].append(path)
        elif p.endswith((".json", ".yaml", ".yml", ".toml", ".ini", ".env", ".config")):
            groups["config_files"].append(path)
        elif any(x in p for x in ("main.", "index.", "app.", "server.", "router.", "bootstrap.", "entry.")):
            groups["entry_points"].append(path)
        elif any(x in p for x in ("src/", "app/", "lib/", "server/", "api/", "routes/", "core/", "cmd/")):
            groups["core_files"].append(path)

    groups = {k: sorted(set(v))[:12] for k, v in groups.items()}
    priority = list(dict.fromkeys(sum([groups[k][:3] for k in ("entry_points", "core_files", "docs_files", "tests_files", "config_files")], [])))[:10]

    nodes = [{"id": "root", "label": "Repository", "type": "root"}]
    edges = []
    for category, files in groups.items():
        if not files:
            continue
        nodes.append({"id": category, "label": category.replace("_", " ").title(), "type": "category"})
        edges.append({"source": "root", "target": category})
        for i, path in enumerate(files[:8]):
            node_id = f"{category}-{i}"
            nodes.append({"id": node_id, "label": path.split("/")[-1], "path": path, "type": "file", "category": category})
            edges.append({"source": category, "target": node_id})

    return {
        "repo_name": meta.get("full_name", f"{owner}/{repo}"),
        "owner": owner,
        "repo": repo,
        "repo_url": f"https://github.com/{owner}/{repo}",
        "description": meta.get("description") or "No description provided.",
        "stars": meta.get("stargazers_count", 0),
        "forks": meta.get("forks_count", 0),
        "language": meta.get("language") or "Unknown",
        "default_branch": branch,
        "updated_at": meta.get("updated_at"),
        "overview": f"Start with {priority[0] if priority else 'the README'}, then follow the core files and tests.",
        "architecture": [
            "Entry points reveal how the project starts",
            "Core files contain the core application behavior",
            "Tests and docs are the safest onboarding path",
        ],
        "priority_files": priority,
        "files": groups,
        "graph": {"nodes": nodes, "edges": edges},
        "quest_board": [
            {"title": "Trace the boot sequence", "difficulty": "Beginner", "description": "Read the main entry point and follow the first execution path."},
            {"title": "Add an edge-case test", "difficulty": "Beginner", "description": "Find a nearby test and cover a behavior that is not currently documented."},
            {"title": "Improve onboarding", "difficulty": "Easy", "description": "Make setup or contribution instructions clearer for the next developer."},
            {"title": "Map a user flow", "difficulty": "Intermediate", "description": "Follow one request from entry point through core logic to final output."},
        ],
        "questions": [
            "How do I get started?",
            "What files matter most?",
            "Where should I make my first contribution?",
            "How does the main flow work?",
        ],
    }


def build_answer(repo_name: str, question: str, priority_files: list[str]) -> str:
    text = (question or "").lower()
    files = ", ".join(priority_files[:5]) if priority_files else "README and project configuration"
    if any(word in text for word in ("start", "begin", "run", "bootstrap")):
        return f"For {repo_name}, begin with {files}. Read the app entry point first, then the core modules, then the tests. That sequence gives the fastest understanding of the repo."
    if any(word in text for word in ("important", "core", "key", "file")):
        return f"The highest-value files are usually {files}. These usually include the main entry point, the core app logic, and the most relevant tests or docs."
    if any(word in text for word in ("contribute", "first", "beginner", "help")):
        return f"A safe first contribution for {repo_name} is a docs update, a missing test, or a small fix in a utility area. Start with the entry point, then the tests, then deeper logic."
    if any(word in text for word in ("flow", "request", "architecture", "work")):
        return f"The repository usually flows like this: config/setup → entry point → core logic → tests/docs. If you are tracing execution, begin at the entry point and follow the primary modules outward."
    return f"A good path for {repo_name} is to start with the app entry point, then inspect the priority files, then validate behavior with the tests and docs."


@app.get("/health")
def health():
    return {"status": "ok", "version": app.version}


@app.post("/api/analyze")
def analyze(payload: RepoRequest):
    try:
        return analyze_url(payload.repo_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/chat")
def chat(payload: ChatRequest):
    try:
        data = analyze_url(payload.repo_url)
        answer = build_answer(data["repo_name"], payload.question, data["priority_files"])

        if os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                response = OpenAI(api_key=os.getenv("OPENAI_API_KEY")).responses.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    input=[
                        {"role": "system", "content": "You are a senior software mentor. Give concise, evidence-based guidance. Prefer file paths and actionable steps. Mention uncertainty when the repo structure is ambiguous."},
                        {"role": "user", "content": f"Repository: {data['repo_name']}\nPriority files: {', '.join(data['priority_files'][:8])}\nQuestion: {payload.question}"},
                    ],
                )
                if getattr(response, "output_text", None):
                    answer = response.output_text
            except Exception:
                pass

        return {"answer": answer, "sources": data["priority_files"][:5]}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/session")
def session_status(request: Request):
    session_id = request.cookies.get("repoquest_session")
    user = get_user_from_session(session_id)
    if not user:
        return {"authenticated": False, "user": None}
    return {"authenticated": True, "user": {"id": user["id"], "login": user["github_login"], "name": user["name"], "avatar_url": user["avatar_url"]}}


@app.get("/api/history")
def history_status(request: Request):
    session_id = request.cookies.get("repoquest_session")
    user = get_user_from_session(session_id)
    if not user:
        return {"items": []}
    return {"items": get_user_history(user["id"])[:12]}


@app.post("/api/history")
def save_history(payload: HistoryRequest, request: Request):
    session_id = request.cookies.get("repoquest_session")
    user = get_user_from_session(session_id)
    if not user:
        return {"saved": False, "message": "Sign in to save repo history."}
    save_repo_history(user["id"], payload.repo_url, payload.repo_name)
    return {"saved": True}


@app.get("/api/auth/github")
def github_login():
    client_id = os.getenv("GITHUB_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=503, detail="GitHub OAuth is not configured")
    redirect_uri = os.getenv("API_URL", "http://localhost:8000") + "/api/auth/github/callback"
    params = urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "read:user user:email",
        "allow_signup": "true",
    })
    return RedirectResponse(f"https://github.com/login/oauth/authorize?{params}")


@app.get("/api/auth/github/callback")
def github_callback(code: str, response: JSONResponse):
    client_id = os.getenv("GITHUB_CLIENT_ID")
    client_secret = os.getenv("GITHUB_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise HTTPException(status_code=503, detail="GitHub OAuth is not configured")

    token_response = httpx.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
        },
        headers={"Accept": "application/json"},
        timeout=20,
    )
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="GitHub OAuth failed")

    user_data = httpx.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"},
        timeout=20,
    ).json()

    user = upsert_user(
        github_id=str(user_data.get("id")),
        github_login=user_data.get("login"),
        name=user_data.get("name"),
        avatar_url=user_data.get("avatar_url"),
        access_token=access_token,
    )
    session_id = create_session_for_user(user["id"])

    redirect = RedirectResponse(url=os.getenv("FRONTEND_URL", "http://localhost:3000"))
    redirect.set_cookie(key="repoquest_session", value=session_id, httponly=True, samesite="lax", secure=False)
    return redirect


@app.get("/api/logout")
def logout(response: JSONResponse):
    response = JSONResponse({"logged_out": True})
    response.delete_cookie("repoquest_session")
    return response
