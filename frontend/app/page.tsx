"use client";

import { useState } from "react";

type Quest = {
  title: string;
  difficulty: string;
  description: string;
};

type RepoData = {
  repo_name: string;
  description: string;
  stars: number;
  forks: number;
  language: string;
  overview: string;
  hero_message: string;
  ai_summary: string;
  architecture: string[];
  entry_points: string[];
  core_files: string[];
  config_files: string[];
  docs_files: string[];
  tests_files: string[];
  priority_files: string[];
  quest_board: Quest[];
  questions: string[];
};

export default function HomePage() {
  const [repoUrl, setRepoUrl] = useState("https://github.com/vercel/next.js");
  const [loading, setLoading] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [data, setData] = useState<RepoData | null>(null);
  const [error, setError] = useState("");
  const [chatQuestion, setChatQuestion] = useState("How do I get started?");
  const [chatAnswer, setChatAnswer] = useState("");

  async function handleAnalyze() {
    setLoading(true);
    setError("");
    setChatAnswer("");
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl }),
      });

      if (!res.ok) {
        throw new Error("Could not analyze repository.");
      }

      const result = await res.json();
      setData(result);
    } catch (err) {
      setError("Something went wrong. Try a valid public GitHub repo URL.");
    } finally {
      setLoading(false);
    }
  }

  async function handleAskRepo() {
    if (!repoUrl || !data) return;
    setChatLoading(true);
    setChatAnswer("");

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl, question: chatQuestion }),
      });

      if (!res.ok) {
        throw new Error("Chat request failed.");
      }

      const result = await res.json();
      setChatAnswer(result.answer || "I couldn’t generate a reliable answer for that question yet.");
    } catch (err) {
      setChatAnswer("I couldn’t answer that yet. Try a more direct question like: How do I start? Where should a contributor begin?");
    } finally {
      setChatLoading(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <div className="hero-inner">
          <div className="hero-copy">
            <div className="eyebrow">REPOQUEST</div>
            <h1>Turn any GitHub repo into a contribution adventure.</h1>
            <p>
              Explore architecture, understand the flow, spot high-value files, and unlock contributor quests in minutes.
            </p>
            <div className="input-row">
              <input
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/owner/repo"
                aria-label="GitHub repo URL"
              />
              <button onClick={handleAnalyze} disabled={loading}>
                {loading ? "Analyzing..." : "Analyze repo"}
              </button>
            </div>
            {error && <div className="error-box">{error}</div>}
          </div>
          <div className="hero-card">
            <div className="mini-label">Repository preview</div>
            <h3>How it works</h3>
            <ul>
              <li>Inspect architecture</li>
              <li>Find contributor entry points</li>
              <li>Generate beginner quests</li>
              <li>Answer repo questions</li>
            </ul>
          </div>
        </div>
      </section>

      {data && (
        <>
          <section className="repo-header card">
            <div>
              <div className="mini-label">Repository</div>
              <h2>{data.repo_name}</h2>
            </div>
            <div className="stats-row">
              <span>⭐ {data.stars}</span>
              <span>🍴 {data.forks}</span>
              <span>{data.language}</span>
            </div>
          </section>

          <section className="summary-grid">
            <div className="card highlight-card">
              <div className="mini-label">AI summary</div>
              <p>{data.hero_message}</p>
              <p className="muted">{data.ai_summary}</p>
            </div>
            <div className="card">
              <div className="mini-label">Description</div>
              <p>{data.description || "No description provided."}</p>
              <p className="muted">{data.overview}</p>
            </div>
          </section>

          <section className="metrics-grid">
            <Card title="Architecture">
              <ul>
                {data.architecture.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </Card>

            <Card title="Priority files">
              <ul>
                {data.priority_files.length ? data.priority_files.map((item) => <li key={item}>{item}</li>) : <li>No priority files detected.</li>}
              </ul>
            </Card>

            <Card title="Entry points">
              <ul>
                {data.entry_points.length ? data.entry_points.map((item) => <li key={item}>{item}</li>) : <li>No entry points found.</li>}
              </ul>
            </Card>
          </section>

          <section className="metrics-grid second-grid">
            <Card title="Core files">
              <ul>
                {data.core_files.length ? data.core_files.map((item) => <li key={item}>{item}</li>) : <li>No core files detected.</li>}
              </ul>
            </Card>

            <Card title="Config / setup">
              <ul>
                {data.config_files.length ? data.config_files.map((item) => <li key={item}>{item}</li>) : <li>No config files detected.</li>}
              </ul>
            </Card>

            <Card title="Tests / docs">
              <ul>
                {data.tests_files.length ? data.tests_files.map((item) => <li key={item}>{item}</li>) : <li>No tests detected.</li>}
              </ul>
            </Card>
          </section>

          <section className="quests-section">
            <div className="section-header">
              <h3>Quest board</h3>
            </div>
            <div className="quest-grid">
              {data.quest_board.map((quest) => (
                <div key={quest.title} className="quest-card">
                  <span className="quest-badge">{quest.difficulty}</span>
                  <h4>{quest.title}</h4>
                  <p>{quest.description}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="chat-box card">
            <div className="section-header">
              <h3>Ask about this repo</h3>
            </div>
            <div className="chat-controls">
              <input
                value={chatQuestion}
                onChange={(e) => setChatQuestion(e.target.value)}
                placeholder="e.g. How do I start? Where should I contribute?"
              />
              <button onClick={handleAskRepo} disabled={chatLoading}>
                {chatLoading ? "Thinking..." : "Ask"}
              </button>
            </div>
            {chatAnswer && <div className="chat-answer">{chatAnswer}</div>}
            <div className="quick-questions">
              {data.questions.slice(0, 4).map((q) => (
                <button key={q} onClick={() => setChatQuestion(q)}>{q}</button>
              ))}
            </div>
          </section>
        </>
      )}
    </main>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card">
      <div className="mini-label">{title}</div>
      {children}
    </div>
  );
}
