// Interactive graph view (Cytoscape.js) of target → tools → results.
// `cytoscape` is loaded as a CDN UMD global on window.cytoscape.

const NET_COLORS = {
  target:  { bg: "#fbbf24", border: "#fde68a" },
  tool:    { bg: "#3b82f6", border: "#93c5fd" },
  result:  { bg: "#10b981", border: "#6ee7b7" },
  failed:  { bg: "#ef4444", border: "#fca5a5" },
  partial: { bg: "#f59e0b", border: "#fcd34d" },
};

let cy = null;

export function ensureGraph(container) {
  if (typeof window.cytoscape !== "function") return null;
  if (cy && cy.container() === container) return cy;
  if (cy) try { cy.destroy(); } catch { /* ignore */ }
  cy = window.cytoscape({
    container,
    elements: [],
    style: [
      { selector: "node", style: {
        "label": "data(label)",
        "color": "#fff",
        "font-size": 11,
        "font-weight": 700,
        "text-outline-width": 2,
        "text-outline-color": "#020817",
        "text-valign": "center",
        "text-halign": "center",
        "text-wrap": "wrap",
        "text-max-width": 90,
        "background-color": "data(bg)",
        "border-color": "data(border)",
        "border-width": 2,
        "width": "data(size)",
        "height": "data(size)",
      }},
      { selector: "node:selected", style: {
        "border-color": "#fbbf24",
        "border-width": 4,
      }},
      { selector: "edge", style: {
        "line-color": "rgba(99,179,237,0.4)",
        "target-arrow-color": "rgba(99,179,237,0.6)",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        "width": 1.5,
      }},
    ],
    layout: { name: "concentric", padding: 20, animate: false },
    minZoom: 0.3,
    maxZoom: 3,
    wheelSensitivity: 0.25,
  });
  return cy;
}

export function setGraphData(target, applicableTools, results, onSelect) {
  if (!cy) return;
  const nodes = [];
  const edges = [];
  const c = NET_COLORS;

  nodes.push({
    data: {
      id: "root",
      label: `🎯 ${target.value}\n[${target.type}]`,
      bg: c.target.bg, border: c.target.border, size: 80,
      kind: "target", payload: target,
    },
  });

  for (const tool of applicableTools) {
    const id = `tool:${tool.id}`;
    const r = results.find(x => x.source === tool.id);
    const palette = r
      ? (r.status === "success" ? c.result : r.status === "partial" ? c.partial : c.failed)
      : c.tool;
    nodes.push({
      data: {
        id, label: tool.label, bg: palette.bg, border: palette.border, size: 56,
        kind: r ? "result" : "tool",
        payload: r || { id: tool.id, label: tool.label, description: tool.description, kind: tool.kind },
      },
    });
    edges.push({ data: { source: "root", target: id } });
  }

  cy.elements().remove();
  cy.add([...nodes, ...edges]);
  cy.layout({ name: "concentric", padding: 20, animate: false, minNodeSpacing: 30 }).run();
  cy.fit(undefined, 30);

  cy.removeListener("tap", "node");
  cy.on("tap", "node", evt => {
    const n = evt.target;
    if (typeof onSelect === "function") onSelect(n.data("payload"), n.data("kind"));
  });
}

export function fitGraph() { if (cy) cy.fit(undefined, 30); }
export function relayoutGraph() {
  if (cy) cy.layout({ name: "concentric", padding: 20, animate: true, minNodeSpacing: 30 }).run();
}
