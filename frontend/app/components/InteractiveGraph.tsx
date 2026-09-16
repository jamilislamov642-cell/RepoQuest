"use client";

import { useMemo, useState } from "react";

type GraphNode = { id: string; label: string; path?: string; type: string; category?: string };
type GraphData = { nodes: GraphNode[]; edges: { source: string; target: string }[] };

export function InteractiveGraph({ graph }: { graph: GraphData }) {
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [selected, setSelected] = useState<GraphNode | null>(null);
  const categories = graph.nodes.filter((node) => node.type === "category");
  const files = useMemo(() => graph.nodes.filter((node) => node.type === "file" && (!activeCategory || node.category === activeCategory)), [graph.nodes, activeCategory]);

  return <div className="interactive-graph">
    <div className="graph-toolbar"><div className="graph-filters"><button className={!activeCategory ? "filter-active" : ""} onClick={() => setActiveCategory(null)}>All</button>{categories.map((category) => <button className={activeCategory === category.id ? "filter-active" : ""} key={category.id} onClick={() => setActiveCategory(category.id)}>{category.label}</button>)}</div><span className="muted">Click a file for details</span></div>
    <div className="graph-canvas"><div className="graph-root">Repository</div><div className="graph-columns">{categories.filter((category) => !activeCategory || category.id === activeCategory).map((category) => <div className="graph-column" key={category.id}><button className="graph-category" onClick={() => setActiveCategory(category.id)}>{category.label}</button>{files.filter((file) => file.category === category.id).map((file) => <button className={`graph-file ${selected?.id === file.id ? "graph-selected" : ""}`} key={file.id} onClick={() => setSelected(file)} title={file.path}>{file.label}</button>)}</div>)}</div></div>
    {selected && <div className="graph-detail"><strong>{selected.path}</strong><span>{selected.category?.replace("_", " ")}</span><a href={`https://github.com/${selected.path || ""}`} target="_blank" rel="noreferrer">Inspect file ↗</a></div>}
  </div>;
}
