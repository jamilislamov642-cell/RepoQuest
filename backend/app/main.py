from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from urllib.parse import urlencode
import httpx, os, re
from typing import Any

app = FastAPI(title="RepoQuest API", version="0.3.0")
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class RepoRequest(BaseModel): repo_url: str
class ChatRequest(BaseModel): repo_url: str; question: str

def parts(url: str):
    match = re.search(r"github\.com[:/]+([^/]+)/([^/#?]+)", url.strip().rstrip("/"))
    if not match: raise ValueError("Use a valid GitHub URL: https://github.com/owner/repo")
    return match.group(1), match.group(2).removesuffix(".git")

def gh(url: str) -> Any:
    headers = {"Accept":"application/vnd.github+json", "User-Agent":"RepoQuest"}
    if os.getenv("GITHUB_TOKEN"): headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    response = httpx.get(url, headers=headers, timeout=25)
    if response.status_code != 200: raise HTTPException(400, f"GitHub request failed ({response.status_code})")
    return response.json()

def analyze_url(url: str):
    owner, repo = parts(url)
    meta = gh(f"https://api.github.com/repos/{owner}/{repo}")
    branch = meta.get("default_branch", "main")
    tree = gh(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1")
    paths = [x["path"] for x in tree.get("tree", []) if x.get("type") == "blob" and x.get("path")]
    groups = {"entry_points":[], "core_files":[], "config_files":[], "docs_files":[], "tests_files":[]}
    for path in paths:
        p = path.lower()
        if p.endswith((".md", ".rst", ".txt")): groups["docs_files"].append(path)
        elif any(x in p for x in ("test", "spec")) and p.endswith((".js", ".ts", ".tsx", ".py", ".go", ".rs")): groups["tests_files"].append(path)
        elif p.endswith((".json", ".yaml", ".yml", ".toml", ".ini", ".env", ".config")): groups["config_files"].append(path)
        elif any(x in p for x in ("main.", "index.", "app.", "server.", "router.", "bootstrap.", "entry.")): groups["entry_points"].append(path)
        elif any(x in p for x in ("src/", "app/", "lib/", "server/", "api/", "routes/", "core/", "cmd/")): groups["core_files"].append(path)
    groups = {k:v[:12] for k,v in groups.items()}
    priority = list(dict.fromkeys(sum([groups[k][:3] for k in ("entry_points","core_files","docs_files","tests_files","config_files")], [])))[:10]
    nodes = [{"id":"root","label":"Repository","type":"root"}]; edges=[]
    for category, files in groups.items():
        if not files: continue
        nodes.append({"id":category,"label":category.replace("_"," ").title(),"type":"category"}); edges.append({"source":"root","target":category})
        for i, path in enumerate(files[:8]):
            node_id=f"{category}-{i}"; nodes.append({"id":node_id,"label":path.split("/")[-1],"path":path,"type":"file","category":category}); edges.append({"source":category,"target":node_id})
    return {"repo_name":meta.get("full_name", f"{owner}/{repo}"),"owner":owner,"repo":repo,"repo_url":f"https://github.com/{owner}/{repo}","description":meta.get("description") or "No description provided.","stars":meta.get("stargazers_count",0),"forks":meta.get("forks_count",0),"language":meta.get("language") or "Unknown","default_branch":branch,"overview":f"Start with {priority[0] if priority else 'the README'}, then follow core modules and tests.","architecture":["Entry points reveal startup flow","Core files contain application behavior","Tests and docs are the safest onboarding path"],"priority_files":priority,"files":groups,"graph":{"nodes":nodes,"edges":edges},"quest_board":[{"title":"Trace the boot sequence","difficulty":"Beginner","description":"Read the main entry point and follow the first execution path."},{"title":"Add an edge-case test","difficulty":"Beginner","description":"Find a nearby test and cover an undocumented behavior."},{"title":"Improve onboarding","difficulty":"Easy","description":"Make setup or contribution instructions clearer."},{"title":"Map a user flow","difficulty":"Intermediate","description":"Follow a request from entry point through core logic to output."}],"questions":["How do I get started?","What files matter most?","Where should I make my first contribution?","How does the main flow work?"]}

@app.get("/health")
def health(): return {"status":"ok","version":app.version}
@app.post("/api/analyze")
def analyze(payload: RepoRequest):
    try: return analyze_url(payload.repo_url)
    except ValueError as e: raise HTTPException(400, str(e))
@app.post("/api/chat")
def chat(payload: ChatRequest):
    data=analyze_url(payload.repo_url); files=", ".join(data["priority_files"][:8]) or "README and project configuration"
    answer=f"For {data['repo_name']}, begin with {files}. Follow the entry point into core logic, then use tests and docs to validate your understanding. Question: {payload.question}"
    if os.getenv("OPENAI_API_KEY"):
        try:
            from openai import OpenAI
            response=OpenAI().responses.create(model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),input=f"You are a senior developer mentor. Cite relevant file paths, avoid unsupported claims, and give concise actionable guidance. Repository: {data['repo_name']}\nFiles: {files}\nQuestion: {payload.question}")
            answer=response.output_text or answer
        except Exception: pass
    return {"answer":answer,"sources":data["priority_files"][:5]}
@app.get("/api/auth/github")
def github_login():
    if not os.getenv("GITHUB_CLIENT_ID"): raise HTTPException(503,"GitHub OAuth is not configured")
    query=urlencode({"client_id":os.getenv("GITHUB_CLIENT_ID"),"redirect_uri":f"{os.getenv('API_URL','http://localhost:8000')}/api/auth/github/callback","scope":"read:user user:email"})
    return RedirectResponse(f"https://github.com/login/oauth/authorize?{query}")
@app.get("/api/auth/github/callback")
def github_callback(code: str):
    if not os.getenv("GITHUB_CLIENT_SECRET"): raise HTTPException(503,"GitHub OAuth is not configured")
    token=httpx.post("https://github.com/login/oauth/access_token",data={"client_id":os.getenv("GITHUB_CLIENT_ID"),"client_secret":os.getenv("GITHUB_CLIENT_SECRET"),"code":code},headers={"Accept":"application/json"},timeout=20).json().get("access_token")
    if not token: raise HTTPException(400,"GitHub OAuth failed")
    user=gh("https://api.github.com/user")
    return {"user": {"login":user.get("login"),"name":user.get("name"),"avatar_url":user.get("avatar_url")},"access_token":token}
