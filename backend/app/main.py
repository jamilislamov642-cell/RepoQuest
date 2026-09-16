from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import re
from typing import List, Dict, Any

app = FastAPI(title="RepoQuest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RepoRequest(BaseModel):
    repo_url: str


def normalize_repo_url(repo_url: str) -> str:
    repo_url = repo_url.strip()
    if repo_url.endswith("/"):
        repo_url = repo_url[:-1]

    match = re.search(r"github\.com[:/]+([^/]+)/([^/]+)", repo_url)
    if not match:
        raise ValueError("Invalid GitHub repo URL")

    owner, repo = match.groups()
    return f"{owner}/{repo}"


def extract_owner_repo(repo_url: str) -> tuple[str, str]:
    repo_url = repo_url.strip()
    repo_url = repo_url.rstrip("/")
    match = re.search(r"github\.com[:/]+([^/]+)/([^/]+)", repo_url)
    if not match:
        raise ValueError("Invalid GitHub repo URL")
    return match.groups()


def get_repo_metadata(owner: str, repo: str) -> Dict[str, Any]:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = httpx.get(url, timeout=20)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Unable to fetch repository metadata")
    return response.json()


def get_repo_tree(owner: str, repo: str, default_branch: str) -> List[str]:
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
    response = httpx.get(url, timeout=20)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Unable to fetch repository tree")

    data = response.json()
    tree = data.get("tree", [])
    return [item.get("path", "") for item in tree if item.get("path")]


def classify_files(paths: List[str]) -> Dict[str, List[str]]:
    entry_points = []
    core_files = []
    config_files = []
    docs_files = []
    tests_files = []

    for path in paths:
        lower = path.lower()

        if lower.endswith((".md", ".rst", ".txt")):
            docs_files.append(path)
        elif any(lower.endswith(ext) for ext in (".test.js", ".test.ts", ".spec.js", ".spec.ts", ".py", ".go", ".rs")):
            tests_files.append(path)
        elif any(seg in lower for seg in ("app/", "src/", "lib/", "server/", "api/", "routes/")):
            core_files.append(path)
        elif lower.endswith((".json", ".yaml", ".yml", ".toml", ".ini", ".env")):
            config_files.append(path)
        elif any(seg in lower for seg in ("main.", "index.", "app.", "server.", "routes.")):
            entry_points.append(path)

    return {
        "entry_points": entry_points[:10],
        "core_files": core_files[:12],
        "config_files": config_files[:10],
        "docs_files": docs_files[:8],
        "tests_files": tests_files[:8],
    }


def build_quests(files: Dict[str, List[str]], repo_name: str) -> List[Dict[str, Any]]:
    quests = []

    if files["entry_points"]:
        quests.append({
            "title": "Bootstrap the app",
            "difficulty": "Beginner",
            "description": f"Start by reading the main entry point in {files['entry_points'][0]} and understand how the app boots."
        })

    if files["config_files"]:
        quests.append({
            "title": "Configure the environment",
            "difficulty": "Easy",
            "description": "Review the config and environment files to understand runtime setup and dependencies."
        })

    if files["tests_files"]:
        quests.append({
            "title": "Add or improve tests",
            "difficulty": "Beginner",
            "description": "Find a test file and add a missing edge-case check to understand the project workflow."
        })

    quests.append({
        "title": "Trace a user-facing flow",
        "difficulty": "Intermediate",
        "description": "Follow a request from entry to output and note which files are responsible for routing and rendering."
    })

    quests.append({
        "title": "Improve contributor docs",
        "difficulty": "Easy",
        "description": "Look for missing setup details and suggest improvements to onboarding documentation."
    })

    return quests


def infer_architecture(files: Dict[str, List[str]]) -> List[str]:
    architecture = []
    if files["entry_points"]:
        architecture.append("Entry points define application startup and routing")
    if files["core_files"]:
        architecture.append("Core source files hold business logic and app behavior")
    if files["config_files"]:
        architecture.append("Configuration files define environment, dependencies, and runtime setup")
    if files["tests_files"]:
        architecture.append("Tests are the safest place to understand expected behavior")
    if files["docs_files"]:
        architecture.append("Documentation files explain setup, architecture, and contribution flow")

    return architecture


def generate_questions(repo_name: str) -> List[str]:
    return [
        f"How does {repo_name} start its app?",
        f"What are the most important files in {repo_name}?",
        f"Where should a new contributor begin?",
        f"How do requests flow through this project?",
    ]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze_repo(payload: RepoRequest):
    try:
        owner, repo = extract_owner_repo(payload.repo_url)
        repo_meta = get_repo_metadata(owner, repo)
        default_branch = repo_meta.get("default_branch", "main")
        paths = get_repo_tree(owner, repo, default_branch)

        files = classify_files(paths)
        repo_name = repo_meta.get("full_name", repo)

        summary = {
            "repo_name": repo_name,
            "description": repo_meta.get("description") or "No description provided.",
            "stars": repo_meta.get("stargazers_count", 0),
            "language": repo_meta.get("language") or "Not detected",
            "default_branch": default_branch,
            "overview": f"{repo_name} appears to be a {repo_meta.get('language') or 'general'} codebase focused on application logic, configuration, and developer workflows.",
            "architecture": infer_architecture(files),
            "entry_points": files["entry_points"],
            "core_files": files["core_files"],
            "config_files": files["config_files"],
            "docs_files": files["docs_files"],
            "tests_files": files["tests_files"],
            "quest_board": build_quests(files, repo_name),
            "questions": generate_questions(repo_name),
        }

        return summary

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
