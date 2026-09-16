"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SharePage({ params }: { params: { owner: string; repo: string } }) {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_url: `https://github.com/${params.owner}/${params.repo}` }),
    })
      .then((res) => res.json())
      .then(setData)
      .catch(() => setError("This repository could not be loaded."));
  }, [params.owner, params.repo]);

  if (error) {
    return (
      <main className="page-shell">
        <p>{error}</p>
        <Link href="/">Back to RepoQuest</Link>
      </main>
    );
  }

  if (!data) {
    return (
      <main className="page-shell">
        <p>Loading public repo map…</p>
      </main>
    );
  }

  return (
    <main className="page-shell">
      <nav className="nav">
        <Link href="/" className="brand">◈ RepoQuest</Link>
        <a href={data.repo_url} target="_blank" rel="noreferrer">View on GitHub ↗</a>
      </nav>

      <section className="hero-copy card">
        <div className="eyebrow">PUBLIC REPO QUEST</div>
        <h1>{data.repo_name}</h1>
        <p>{data.description}</p>
        <p className="muted">{data.overview}</p>
      </section>

      <section className="graph-section card">
        <div className="mini-label">Architecture map</div>
        <div className="repo-graph">
          {data.graph.nodes.filter((n: any) => n.type === "category").map((category: any) => (
            <div className="graph-column" key={category.id}>
              <div className="graph-category">{category.label}</div>
              {data.graph.nodes.filter((n: any) => n.category === category.id).map((node: any) => (
                <div className="graph-file" key={node.id}>{node.label}</div>
              ))}
            </div>
          ))}
        </div>
      </section>

      <section className="quests-section">
        <h2>Contributor quests</h2>
        <div className="quest-grid">
          {data.quest_board.map((quest: any) => (
            <div className="quest-card" key={quest.title}>
              <span className="quest-badge">{quest.difficulty}</span>
              <h3>{quest.title}</h3>
              <p>{quest.description}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
