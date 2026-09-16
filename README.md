html, body {
  margin: 0;
  padding: 0;
  background: radial-gradient(circle at top, rgba(124, 58, 237, 0.16), transparent 30%), linear-gradient(180deg, #f8fafc, #eef2ff);
  color: #0f172a;
  font-family: Arial, Helvetica, sans-serif;
}

* { box-sizing: border-box; }
button, input { font: inherit; }
a { color: inherit; text-decoration: none; }

.page-shell {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 20px 80px;
}

.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 26px;
}

.brand {
  font-size: 1.25rem;
  font-weight: 900;
  letter-spacing: -0.05em;
  color: #111827;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.nav-link {
  color: #4338ca;
  font-weight: 700;
}

.ghost, .share-button, .history-list button, .quick-questions button, .primary-link, .card-actions a {
  border: 1px solid #ddd6fe;
  background: #fff;
  color: #5b21b6;
  border-radius: 10px;
  padding: 9px 12px;
  cursor: pointer;
}

.user-pill {
  padding: 8px 10px;
  border-radius: 999px;
  background: #eef2ff;
  color: #312e81;
  font-weight: 700;
}

.hero {
  display: grid;
  grid-template-columns: 1.5fr 0.8fr;
  gap: 20px;
}

.hero-copy, .hero-card, .card, .quest-card {
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 22px;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
}

.hero-copy {
  padding: 42px 30px;
}

.hero-card {
  padding: 28px 26px;
  background: linear-gradient(135deg, #111827, #312e81);
  color: #fff;
}

.eyebrow, .mini-label {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
  font-weight: 700;
  color: #7c3aed;
}

.hero-card .mini-label { color: #c4b5fd; }

.hero h1 {
  margin: 14px 0;
  font-size: clamp(2.5rem, 5vw, 4.4rem);
  line-height: 1.02;
  letter-spacing: -0.06em;
}

.hero p, .muted, .repo-header p {
  color: #475569;
  line-height: 1.7;
}

.input-row, .chat-controls {
  display: flex;
  gap: 10px;
  margin-top: 22px;
  flex-wrap: wrap;
}

.input-row input, .chat-controls input {
  flex: 1;
  min-width: 220px;
  border: 1px solid #dfe4ee;
  border-radius: 12px;
  padding: 14px 16px;
  outline: none;
}

.input-row button, .chat-controls button {
  border: 0;
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: #fff;
  border-radius: 12px;
  padding: 14px 20px;
  font-weight: 700;
  cursor: pointer;
}

.error-box {
  margin-top: 14px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 12px;
  padding: 12px;
}

.history, .repo-header, .discover-hero, .graph-section, .chat-box, .quests-section {
  margin-top: 22px;
}

.card {
  padding: 22px 20px;
}

.history-list, .stats-row, .quick-questions, .card-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.repo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.repo-header h2 {
  margin: 8px 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-top: 18px;
}

.highlight-card {
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.08), rgba(79, 70, 229, 0.08));
}

.card ul {
  margin: 0;
  padding-left: 18px;
  line-height: 1.8;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-top: 18px;
}

.graph-section {
  padding: 22px 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.section-header h3, .quests-section h2 {
  margin: 0;
}

.repo-graph {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  background: linear-gradient(90deg, #f8fafc, #eef2ff);
  border-radius: 16px;
  padding: 18px 8px 10px;
}

.graph-column {
  min-width: 170px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.graph-category {
  background: #312e81;
  color: white;
  border-radius: 10px;
  padding: 10px;
  font-weight: 700;
  text-align: center;
}

.graph-file {
  background: #fff;
  border: 1px solid #ddd6fe;
  border-radius: 9px;
  padding: 8px;
  font-size: 13px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.quest-grid, .discover-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-top: 16px;
}

.quest-card {
  padding: 20px;
}

.quest-badge {
  display: inline-block;
  background: #ede9fe;
  color: #6d28d9;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.quest-card p, .repo-card p {
  color: #4b5563;
  line-height: 1.7;
}

.chat-answer {
  margin-top: 14px;
  padding: 16px;
  background: #f5f3ff;
  border: 1px solid #ddd6fe;
  border-radius: 14px;
  line-height: 1.7;
}

.discover-hero { padding: 30px; }

.repo-card {
  padding: 18px;
}

.repo-card-top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  margin-bottom: 12px;
}

.language-pill {
  background: #eef2ff;
  color: #3730a3;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 700;
}

.stars {
  color: #f59e0b;
  font-weight: 700;
}

.card-actions {
  margin-top: 18px;
}

.primary-link {
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: #fff;
}

@media (max-width: 900px) {
  .hero, .summary-grid, .metrics-grid, .quest-grid, .discover-grid {
    grid-template-columns: 1fr;
  }

  .repo-header {
    display: block;
  }

  .stats-row {
    justify-content: flex-start;
    margin-top: 14px;
  }
}
