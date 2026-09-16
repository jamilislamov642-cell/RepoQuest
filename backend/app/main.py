from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import re
import os
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


class ChatRequest(BaseModel):
    repo_url: str
    question: str


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
        elif any(lower.endswith(ext) for ext in (".test.js", ".test.ts", ".spec.js", ".spec.ts", ".test.py", ".spec.py", ".go", ".rs")):
            tests_files.append(path)
        elif any(seg in lower for seg in ("app/", "src/", "lib/", "server/", "api/", "routes/", "core/", "cmd/")):
            core_files.append(path)
        elif lower.endswith((".json", ".yaml", ".yml", ".toml", ".ini", ".env", ".config")):
            config_files.append(path)
        elif any(seg in lower for seg in ("main.", "index.", "app.", "server.", "router.", "routes.", "bootstrap.", "entry.")):
            entry_points.append(path)

    return {
        "entry_points": entry_points[:10],
        "core_files": core_files[:12],
        "config_files": config_files[:10],
        "docs_files": docs_files[:8],
        "tests_files": tests_files[:8],
    }


def build_quests(files: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    quests = []

    if files["entry_points"]:
        quests.append({
            "title": "Bootstrap the app",
            "difficulty": "Beginner",
            "description": f"Read the startup path in {files['entry_points'][0]} and understand how the app begins execution.",
        })

    if files["config_files"]:
        quests.append({
            "title": "Understand setup and config",
            "difficulty": "Easy",
            "description": "Inspect environment and config files to understand required variables, dependencies, and runtime setup.",
        })

    if files["tests_files"]:
        quests.append({
            "title": "Cover a missing edge case",
            "difficulty": "Beginner",
            "description": "Pick a test file and add a realistic edge-case check to understand expected behavior.",
        })

    quests.append({
        "title": "Trace a user flow",
        "difficulty": "Intermediate",
        "description": "Follow one user-facing request from input to output and map the main files involved.",
    })

    quests.append({
        "title": "Improve onboarding docs",
        "difficulty": "Easy",
        "description": "Look for missing setup details or confusing user instructions and help make the repo easier for new contributors.",
    })

    return quests


def infer_architecture(files: Dict[str, List[str]]) -> List[str]:
    architecture = []
    if files["entry_points"]:
        architecture.append("Entry points define startup and the app’s main execution flow")
    if files["core_files"]:
        architecture.append("Core source files hold major business logic and application behavior")
    if files["config_files"]:
        architecture.append("Configuration files describe environment, dependencies, and runtime setup")
    if files["tests_files"]:
        architecture.append("Tests provide the clearest idea of expected behavior and edge cases")
    if files["docs_files"]:
        architecture.append("Documentation files explain setup, architecture, and contributor onboarding")
    return architecture


def generate_questions(repo_name: str) -> List[str]:
    return [
        f"How does {repo_name} start its app?",
        f"What are the most important files in {repo_name}?",
        f"Where should a new contributor begin?",
        f"How do requests flow through this project?",
        f"What is the safest area to make a first contribution?",
    ]


def build_priority_files(files: Dict[str, List[str]]) -> List[str]:
    priority = []
    priority.extend(files.get("entry_points", [])[:3])
    priority.extend(files.get("core_files", [])[:5])
    priority.extend(files.get("docs_files", [])[:2])
    priority.extend(files.get("tests_files", [])[:2])
    unique = []
    seen = set()
    for item in priority:
        if item and item not in seen:
            unique.append(item)
            seen.add(item)
    return unique[:8]


def get_simple_answer(repo_name: str, question: str, files: Dict[str, List[str]]) -> str:
    question_lower = question.lower()

    if any(word in question_lower for word in ("start", "run", "begin", "bootstrap")):
        if files.get("entry_points"):
            return (
                f"Start with the repo’s entry point: {files['entry_points'][0]}. "
                "This file usually shows how the project boots and where the first execution flow begins. "
                "After that, read the core logic files and the config files to understand dependencies and runtime setup."
            )
        return f"To get started in {repo_name}, review the docs and project config first, then inspect the main application and route files."

    if any(word in question_lower for word in ("important", "core", "key", "files")):
        important = build_priority_files(files)
        if important:
            return (
                f"The most valuable files to inspect first are: {', '.join(important[:5])}. "
                "These usually include the entry point, core application logic, and the most relevant documentation or tests."
            )
        return f"This project looks relatively small, so start with the app entry point, config files, and a major test file."

    if any(word in question_lower for word in ("contribute", "first", "beginner", "help")):
        return (
            f"A good first contribution path for {repo_name} is: read the docs, inspect the startup file, find a test file, and then make a small improvement or add a missing test case. "
            "This is the lowest-risk way to understand the project before making code changes."
        )

    if any(word in question_lower for word in ("flow", "request", "architecture", "how it works")):
        return (
            f"The project usually flows like this: setup/config → app entry point → core logic → tests/docs. "
            "If you want to understand request flow, start from the app entry point and follow the logic into routing, services, and validation."
        )

    if any(word in question_lower for word in ("safe", "risk", "easy")):
        if files.get("tests_files"):
            return "The safest contribution area is usually the tests and docs. Start by fixing a failing test or improving documentation before touching deeper business logic."
        return "The safest contribution area is usually the documentation and configuration layer, followed by small bug fixes in isolated utility modules."

    return (
        f"For {repo_name}, the best path is to begin with the app startup file, then the core application logic, and finally the tests/docs. "
        "That sequence gives you the fastest understanding of how the project is structured."
    )


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
            "forks": repo_meta.get("forks_count", 0),
            "language": repo_meta.get("language") or "Not detected",
            "default_branch": default_branch,
            "last_updated": repo_meta.get("updated_at"),
            "overview": f"{repo_name} appears to be a {repo_meta.get('language') or 'general'} codebase focused on application logic, configuration, and developer workflows.",
            "hero_message": f"This repo is a {repo_meta.get('language') or 'general'} project with a clear structure for exploration, contribution, and onboarding.",
            "architecture": infer_architecture(files),
            "entry_points": files["entry_points"],
            "core_files": files["core_files"],
            "config_files": files["config_files"],
            "docs_files": files["docs_files"],
            "tests_files": files["tests_files"],
            "priority_files": build_priority_files(files),
            "quest_board": build_quests(files),
            "questions": generate_questions(repo_name),
            "ai_summary": (
                f"{repo_name} looks like a practical codebase with a defined startup path, core logic, and contributor-oriented documentation. "
                "The most promising onboarding path is to start from the app entry point and then inspect the tests and docs before larger implementation work."
            ),
        }

        return summary

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/chat")
async def chat_with_repo(payload: ChatRequest):
    try:
        owner, repo = extract_owner_repo(payload.repo_url)
        repo_meta = get_repo_metadata(owner, repo)
        default_branch = repo_meta.get("default_branch", "main")
        paths = get_repo_tree(owner, repo, default_branch)
        files = classify_files(paths)
        repo_name = repo_meta.get("full_name", repo)

        answer = get_simple_answer(repo_name, payload.question, files)

        if os.getenv("OPENAI_API_KEY"):
            try:
                import openai

                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {
                            "role": "system",
                            "content": "You are a senior software mentor helping developers understand a repository quickly. Keep answers concise, practical, and actionable.",
                        },
                        {
                            "role": "user",
                            "content": f"Repository: {repo_name}\nQuestion: {payload.question}\nImportant files: {', '.join(build_priority_files(files)[:6])}",
                        },
                    ],
                )
                if getattr(response, "output_text", None):
                    answer = response.output_text
            except Exception:
                answer = answer

        return {"answer": answer}

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
