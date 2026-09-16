"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type RepoCard = {
  id: number;
  full_name: string;
  html_url: string;
  description: string | null;
  stargazers_count: number;
  language: string | null;
  topics?: string[];
};

export default function DiscoverPage() {
  const [query, setQuery] = useState("developer tools");
  const [repos, setRepos] = useState<RepoCard[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function discover(nextQuery = query) {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API}/api/discover?q=${encodeURIComponent(nextQuery)}`);
      if (!response.ok) throw new Error("Discovery request failed");
      const result = await response.json();
      setRepos(result.items || []);
    } catch {
      setError("Discovery is temporarily unavailable. Try again in a moment.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { discover("developer tools"); }, []);

  return (
    <main className="page-shell">
      <nav className="nav"><Link href="/" className="brand">◈ RepoQuest</Link><span className="muted">Discover interesting codebases</span></nav>
      <section className="hero-copy card discover-hero">
        <div className="eyebrow">DISCOVER</div>
        <h1>Find your next repository quest.</h1>
        <p>Explore popular, growing, and contributor-friendly projects through RepoQuest.</p>
        <form className="input-row" onSubmit={(event) => { event.preventDefault(); discover(); }}>
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search GitHub repositories" />
          <button disabled={loading}>{loading ? "Searching..." : "Search"}</button>
        </form>
      </section>
      {error && <div className="error-box">{error}</div>}
      <section className="discover-grid">
        {repos.map((repo) => {
          const [owner, name] = repo.full_name.split("/");
          return <article className="repo-card card" key={repo.id}>
            <div className="repo-card-top"><span className="language-dot" /> <span>{repo.language || "Various"}</span><span className="stars">★ {repo.stargazers_count.toLocaleString()}</span></div>
            <h3>{repo.full_name}</h3>
            <p>{repo.description || "No description provided."}</p>
            <div className="card-actions"><Link className="primary-link" href={`/share/${owner}/${name}`}>Open quest</Link><a href={repo.html_url} target="_blank" rel="noreferrer">GitHub ↗</a></div>
          </article>;
        })}
      </section>
    </main>
  );
}
