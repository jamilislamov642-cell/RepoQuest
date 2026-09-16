RepoQuest

Turn any GitHub repo into a playable contribution journey.

I built RepoQuest because when I open an unfamiliar GitHub repository, the hardest part isn’t always understanding the code — it’s figuring out where to start.

RepoQuest takes a GitHub repository, analyzes its structure, finds the important files, maps out the architecture, and turns the whole thing into a guided exploration experience.

Instead of opening hundreds of files and guessing what matters, I wanted to give developers an actual path.

What I Built

With RepoQuest, I can:

* Analyze a public GitHub repository
* Find important entry points and core files
* Classify files by their purpose
* Understand the basic project architecture
* Get recommended files to read first
* Generate contribution quests
* Ask questions about the repository
* Explore public repositories through Discover
* Save repositories and browsing history
* Share analyzed repositories through public pages

Quests

One of the main ideas behind RepoQuest is turning repository exploration into something more interactive.

Instead of just showing a file tree, I generate tasks such as:

* Trace the boot sequence
* Map an important user flow
* Find a low-risk fix
* Add an edge-case test
* Improve onboarding documentation

The idea is to make exploring a codebase feel less like reading a wall of code and more like following a path.

AI Assistant

I also added a repo-specific AI assistant.

I can ask things like:

How do I get started?

Where should I contribute first?

What are the most important files?

When an OpenAI API key is configured, RepoQuest can generate richer answers using the repository’s structure and analysis.

Tech Stack

Frontend

* Next.js
* React
* TypeScript
* CSS

Backend

* FastAPI
* Python

Database

* SQLite

APIs

* GitHub API
* OpenAI API (optional)

Deployment

* Vercel
* Render
* Railway

Architecture

GitHub Repository
       │
       ▼
    RepoQuest
       │
   ┌───┴────┐
   ▼        ▼
Next.js   FastAPI
Frontend   Backend
             │
       ┌─────┼─────┐
       ▼     ▼     ▼
    GitHub SQLite OpenAI
      API          API

Project Structure

RepoQuest/
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── discover/
│   │   └── share/
│   ├── globals.css
│   └── vercel.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── db.py
│   └── DISCOVER_ENDPOINT.md
│
├── render.yaml
├── railway.json
├── DEPLOYMENT.md
├── .gitignore
└── README.md

Running It

Clone the repository:

git clone https://github.com/YOUR_USERNAME/RepoQuest.git
cd RepoQuest

Start the backend:

cd backend
pip install -r requirements.txt

Then start the frontend:

cd frontend
npm install
npm run dev

Environment variables can be configured for GitHub OAuth, GitHub API access, OpenAI, and the frontend/backend URLs.

License

RepoQuest is licensed under the MIT License.

See LICENSE for the full license.

Why I Built It

I wanted RepoQuest to solve one simple problem:

You shouldn’t have to reverse-engineer an entire repository just to figure out where to begin.

I built it around that idea — take a GitHub URL, turn the repository into a map, highlight what matters, and give developers a path from first look → understanding → contribution.

Explore. Understand. Contribute.