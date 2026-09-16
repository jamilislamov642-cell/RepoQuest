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
  language: string;
  overview: string;
  architecture: string[];
  entry_points: string[];
  core_files: string[];
  config_files: string[];
  docs_files: string[];
  tests_files: string[];
  quest_board: Quest[];
  questions: string[];
};

export default function HomePage() {
  const [repoUrl, setRepoUrl] = useState("https://github.com/vercel/next.js");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<RepoData | null>(null);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    setLoading(true);
    setError("");
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

  return (
    <main style={{ maxWidth: 1200, margin: "0 auto", padding: 32 }}>
      <div style={{ marginBottom: 32 }}>
        <p style={{ color: "#7c3aed", fontWeight: 700, letterSpacing: 1 }}>REPOQUEST</p>
        <h1 style={{ fontSize: 52, margin: "8px 0" }}>Turn any GitHub repo into a contribution game</h1>
        <p style={{ fontSize: 18, color: "#555" }}>
          Explore architecture, uncover beginner tasks, and discover where a contributor should start.
        </p>
      </div>

      <div style={{ display: "flex", gap: 12, marginBottom: 24 }}>
        <input
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/owner/repo"
          style={{
            flex: 1,
            padding: "14px 16px",
            borderRadius: 12,
            border: "1px solid #ddd",
            fontSize: 16,
          }}
        />
        <button
          onClick={handleAnalyze}
          disabled={loading}
          style={{
            background: "#7c3aed",
            color: "white",
            border: "none",
            borderRadius: 12,
            fontSize: 16,
            fontWeight: 700,
            padding: "14px 22px",
            cursor: "pointer",
          }}
        >
          {loading ? "Analyzing..." : "Analyze repo"}
        </button>
      </div>

      {error && (
        <div style={{ background: "#fee2e2", color: "#991b1b", padding: 12, borderRadius: 10 }}>
          {error}
        </div>
      )}

      {data && (
        <>
          <section
            style={{
              background: "linear-gradient(135deg, #111827, #312e81)",
              color: "white",
              borderRadius: 18,
              padding: 26,
              marginBottom: 24,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <p style={{ margin: 0, opacity: 0.8 }}>Repository</p>
                <h2 style={{ margin: 0, fontSize: 28 }}>{data.repo_name}</h2>
              </div>
              <div style={{ textAlign: "right" }}>
                <div>⭐ {data.stars}</div>
                <div>{data.language}</div>
              </div>
            </div>

            <p style={{ marginTop: 16, fontSize: 17 }}>{data.description}</p>
            <p style={{ marginTop: 12, color: "#dbeafe" }}>{data.overview}</p>
          </section>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 18 }}>
            <Card title="Architecture">
              <ul>
                {data.architecture.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </Card>

            <Card title="Likely entry points">
              <ul>
                {data.entry_points.length ? data.entry_points.map((item) => <li key={item}>{item}</li>) : <li>No entry points found.</li>}
              </ul>
            </Card>

            <Card title="Core files">
              <ul>
                {data.core_files.length ? data.core_files.map((item) => <li key={item}>{item}</li>) : <li>No core files detected.</li>}
              </ul>
            </Card>
          </div>

          <div style={{ marginTop: 24, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 18 }}>
            <Card title="Config / setup">
              <ul>
                {data.config_files.length ? data.config_files.map((item) => <li key={item}>{item}</li>) : <li>No config files detected.</li>}
              </ul>
            </Card>

            <Card title="Docs">
              <ul>
                {data.docs_files.length ? data.docs_files.map((item) => <li key={item}>{item}</li>) : <li>No docs detected.</li>}
              </ul>
            </Card>

            <Card title="Tests">
              <ul>
                {data.tests_files.length ? data.tests_files.map((item) => <li key={item}>{item}</li>) : <li>No test files detected.</li>}
              </ul>
            </Card>
          </div>

          <div style={{ marginTop: 30 }}>
            <h3>Quest board</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16 }}>
              {data.quest_board.map((quest) => (
                <div key={quest.title} style={{ border: "1px solid #e5e7eb", borderRadius: 16, padding: 18 }}>
                  <p style={{ color: "#7c3aed", fontWeight: 700 }}>{quest.difficulty}</p>
                  <h4>{quest.title}</h4>
                  <p style={{ color: "#4b5563" }}>{quest.description}</p>
                </div>
              ))}
            </div>
          </div>

          <div style={{ marginTop: 30 }}>
            <h3>Questions you could ask</h3>
            <ul>
              {data.questions.map((q) => <li key={q}>{q}</li>)}
            </ul>
          </div>
        </>
      )}
    </main>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: 18, padding: 18, background: "#fff" }}>
      <h3>{title}</h3>
      {children}
    </div>
  );
}
