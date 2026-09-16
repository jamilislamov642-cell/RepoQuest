from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from urllib.parse import quote, urlencode
from typing import Any, Dict, List
import httpx
import os
import re

from .db import create_session_for_user, get_user_from_session, get_user_history, save_repo_history, upsert_user

app = FastAPI(title="RepoQuest API", version="0.5.0")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
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


def normalize_repo_url(repo_url: str) -> str:
    cleaned = repo_url.strip().rstrip("/")
    match = re.search(r"github\.com[:/]+([^/]+)/([^/#?]+)", cleaned)
    if not match:
        raise ValueError("Use a valid GitHub URL like https://github.com/owner/repo")
    owner, repo = match.groups()
    return f"{owner}/{repo}".removesuffix(".git")


def github_get(url: str) -> Any:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "RepoQuest"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = httpx.get(url, headers=headers, timeout=25)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"GitHub request failed ({response.status_code})")
    return response.json()


def classify_files(paths: List[str]) -> Dict[str, List[str]]:
    result = {"entry_points": [], "core_files": [], "config_files": [], "docs_files": [], "tests_files": []}
    for path in paths:
        lower = path.lower()
        if lower.endswith((".md", ".rst", ".txt")):
            result["docs_files"].append(path)
        elif any(token in lower for token in ("test", "spec")) and lower.endswith((".js", ".ts", ".tsx", ".py", ".go", ".rs")):
            result["tests_files"].append(path)
        elif lower.endswith((".json", ".yaml", ".yml", ".toml", ".ini", ".env", ".config")):
            result["config_files"].append(path)
        elif any(token in lower for token in ("main.", "index.", "app.", "server.", "router.", "bootstrap.", "entry.")):
            result["entry_points"].append(path)
        elif any(token in lower for token in ("src/", "app/", "lib/", "server/", "api/", "routes/", "core/", "cmd/")):
            result["core_files"].append(path)
    return {key: sorted(set(value))[:12] for key, value in result.items()}


def build_priority_files(files: Dict[str, List[str]]) -> List[str]:
    priority = []
    for key in ("entry_points", "core_files", "docs_files", "tests_files", "config_files"):
        priority.extend(files.get(key, [])[:3])
    unique = []
    seen = set()
    for item in priority:
        if item and item not in seen:
            unique.append(item)
            seen.add(item)
    return unique[:10]


def build_quests(files: Dict[str, List[str]]) -> List[Dict[str, str]]:
    quests = []
    if files.get("entry_points"):
        quests.append({
            "title": "Trace the boot sequence",
            "difficulty": "Beginner",
            "description": f"Read {files['entry_points'][0]} and follow the first execution path to understand how the project starts.",
        })
    if files.get("tests_files"):
        quests.append({
            "title": "Add an edge-case test",
            "difficulty": "Beginner",
            "description": "Cover a missing or under-tested behavior to understand the expected project flow.",
        })
    if files.get("docs_files"):
        quests.append({
            "title": "Improve onboarding clarity",
            "difficulty": "Easy",
            "description": "Make docs easier to follow by improving setup, contribution, or architecture guidance.",
        })
    quests.extend([
        {
            "title": "Map a user flow",
            "difficulty": "Intermediate",
            "description": "Trace one request or feature from entry point to output and identify the main files involved.",
        },
        {
            "title": "Find a low-risk fix",
            "difficulty": "Easy",
            "description": "Start with docs, config, or a small utility improvement before touching deeper application logic.",
        },
    ])
    return quests


def infer_architecture(files: Dict[str, List[str]]) -> List[str]:
    architecture = []
    if files.get("entry_points"):
        architecture.append("Entry points reveal the main startup path and execution flow.")
    if files.get("core_files"):
        architecture.append("Core files hold the main application logic and business behavior.")
    if files.get("config_files"):
        architecture.append("Config files define dependencies, environment variables, and runtime setup.")
    if files.get("tests_files"):
        architecture.append("Tests clarify expected behavior and point to the safest contribution areas.")
    if files.get("docs_files"):
        architecture.append("Documentation helps new contributors understand how the project is organized.")
    return architecture


def generate_questions(repo_name: str) -> List[str]:
    return [
        f"How does {repo_name} start its app?",
        f"What are the most important files in {repo_name}?",
        f"Where should a new contributor begin?",
        f"How does data or traffic flow through this project?",
        f"What is the safest first contribution?",
    ]


def build_graph(paths: List[str], files: Dict[str, List[str]]) -> Dict[str, List[Dict[str, Any]]]:
    nodes = [{"id": "root", "label": "Repository", "type": "root"}]
    edges = []
    for category, items in files.items():
        if not items:
            continue
        nodes.append({"id": category, "label": category.replace("_", " ").title(), "type": "category"})
        edges.append({"source": "root", "target": category})
        for index, path in enumerate(items[:8]):
            node_id = f"{category}-{index}"
            nodes.append({"id": node_id, "label": path.split("/")[-1], "path": path, "type": "file", "category": category})
            edges.append({"source": category, "target": node_id})
    return {"nodes": nodes, "edges": edges}


def repo_summary(repo_url: str) -> Dict[str, Any]:
    owner, repo = normalize_repo_url(repo_url).split("/")
    meta = github_get(f"https://api.github.com/repos/{owner}/{repo}")
    default_branch = meta.get("default_branch", "main")
    tree = github_get(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1")
    paths = [item["path"] for item in tree.get("tree", []) if item.get("type") == "blob" and item.get("path")]
    files = classify_files(paths)
    priority = build_priority_files(files)
    repo_name = meta.get("full_name", f"{owner}/{repo}")

    summary = {
        "repo_name": repo_name,
        "owner": owner,
        "repo": repo,
        "repo_url": f"https://github.com/{owner}/{repo}",
        "description": meta.get("description") or "No description provided.",
        "stars": meta.get("stargazers_count", 0),
        "forks": meta.get("forks_count", 0),
        "language": meta.get("language") or "Unknown",
        "default_branch": default_branch,
        "updated_at": meta.get("updated_at"),
        "overview": f"This repository is organized around a clear startup path, core logic, and contributor-friendly docs. Start with {priority[0] if priority else 'the README'} and then move into the tests.",
        "architecture": infer_architecture(files),
        "priority_files": priority,
        "files": files,
        "quest_board": build_quests(files),
        "questions": generate_questions(repo_name),
        "graph": build_graph(paths, files),
    }
    return summary


def build_answer(repo_name: str, question: str, priority_files: List[str]) -> str:
    lower = (question or "").lower()
    file_list = ", ".join(priority_files[:5]) if priority_files else "README and project config"
    if any(token in lower for token in ("start", "begin", "run", "bootstrap")):
        return f"For {repo_name}, begin with {file_list}. Read the entry point first, then the core logic, then the tests and docs. That gives the fastest understanding of the repo."
    if any(token in lower for token in ("important", "core", "key", "files")):
        return f"The highest-value files are usually {file_list}. These usually include the startup file, core logic, and a few relevant tests or docs."
    if any(token in lower for token in ("contribute", "first", "beginner", "help")):
        return f"A safe first contribution for {repo_name} is a docs update, a missing test, or a very small utility fix. Start with the app entry point, then jump into the tests, then deeper modules."
    if any(token in lower for token in ("flow", "request", "architecture", "how it works")):
        return f"The typical project flow is config/setup → entry point → core logic → tests/docs. If you want to trace behavior, start from the entry point and follow the main modules outward."
    return f"A good path for {repo_name} is to inspect the entry point, then the highest-priority files, then check the tests and docs before changing deeper logic."


@app.get("/health")
def health():
    return {"status": "ok", "version": app.version}


@app.get("/api/discover")
def discover(q: str = "developer tools", page: int = 1):
    query = q.strip() or "developer tools"
    result = github_get(
        f"https://api.github.com/search/repositories?q={quote(query)}&sort=stars&order=desc&per_page=18&page={max(1, min(page, 10))}"
    )
    return {"items": result.get("items", []), "total_count": result.get("total_count", 0)}


@app.post("/api/analyze")
def analyze(payload: RepoRequest):
    try:
        return repo_summary(payload.repo_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/chat")
def chat(payload: ChatRequest):
    try:
        data = repo_summary(payload.repo_url)
        answer = build_answer(data["repo_name"], payload.question, data["priority_files"])
        if os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                response = OpenAI(api_key=os.getenv("OPENAI_API_KEY")).responses.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    input=[
                        {
                            "role": "system",
                            "content": "You are a senior software mentor. Give concise, concrete, repo-aware guidance. Prefer evidence from repo files and mention uncertainty when the repository structure is ambiguous.",
                        },
                        {
                            "role": "user",
                            "content": f"Repository: {data['repo_name']}\nPriority files: {', '.join(data['priority_files'][:8])}\nQuestion: {payload.question}",
                        },
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
        return {"saved": False, "message": "Sign in to save history."}
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
def github_callback(code: str):
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
    secure_flag = os.getenv("SESSION_COOKIE_SECURE") == "true"
    redirect.set_cookie(
        key="repoquest_session",
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=secure_flag,
    )
    return redirect


@app.get("/api/logout")
def logout():
    response = JSONResponse({"logged_out": True})
    response.delete_cookie("repoquest_session")
    return response
