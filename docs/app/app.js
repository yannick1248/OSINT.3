// OSINT OMÉGA — Mobile web app
// Static, runs entirely in the browser. Zero backend dependency.
// Every tool and link performs a REAL query — no placeholders.

import { detectTargetType, TargetType } from "./lib/detect.js";
import { evaluateGate } from "./lib/gate.js";
import { TOOLS } from "./lib/tools.js";
import { LINK_TREE } from "./lib/links.js";
import { loadHistory, saveHistory, clearHistory, exportHistory } from "./lib/history.js";

const state = {
  scope: "OWNED_ASSETS",
  target: null,
  gateDecision: null,
  results: [],
  history: loadHistory(),
};

const SCOPE_HELP = {
  SANDBOX_TEST: "Tests et formation. Personnes physiques fortement découragées.",
  OWNED_ASSETS: "Vos domaines, comptes, infrastructures. Usage recommandé.",
  CLIENT_AUTHORIZED_SCOPE: "Mandat écrit obligatoire (pentest, due diligence).",
  PUBLIC_INTEREST_RESEARCH: "Journalisme, recherche académique. Minimisation requise.",
  INTERNAL_AUDIT: "Audit de conformité interne de votre propre organisation.",
  LEGALLY_RESTRICTED: "Bloqué. Aucun outil ne s'exécute.",
};

function $(sel) { return document.querySelector(sel); }
function $$(sel) { return document.querySelectorAll(sel); }

function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;",
  }[c]));
}

function renderScopeHelp() {
  $("#scope-help").textContent = SCOPE_HELP[state.scope] || "";
}

function renderTargetType() {
  const el = $("#target-type");
  if (!state.target) { el.textContent = ""; return; }
  el.innerHTML = `Type détecté&nbsp;: <strong>${state.target.type}</strong> · valeur: <code>${escapeHtml(state.target.value)}</code>`;
}

function renderGate() {
  const el = $("#gate-result");
  if (!state.gateDecision) { el.classList.add("hidden"); return; }
  const d = state.gateDecision;
  el.classList.remove("hidden", "gate-allowed", "gate-restricted", "gate-refused");
  let cls = "gate-allowed";
  let title = "✅ Mission autorisée";
  if (!d.allowed) { cls = "gate-refused"; title = "⛔ Mission refusée"; }
  else if (d.restricted) { cls = "gate-restricted"; title = "⚠ Mission autorisée avec restrictions"; }
  el.classList.add(cls);
  const notes = d.notes.length
    ? `<ul>${d.notes.map(n => `<li>${escapeHtml(n)}</li>`).join("")}</ul>`
    : "";
  el.innerHTML = `<strong>${title}</strong>${notes}`;
}

function showTabs() {
  $("#tabs").classList.remove("hidden");
}

function selectTab(name) {
  $$(".tab").forEach(t => t.classList.toggle("active", t.dataset.tab === name));
  $("#panel-tools").classList.toggle("hidden", name !== "tools");
  $("#panel-links").classList.toggle("hidden", name !== "links");
  $("#panel-results").classList.toggle("hidden", name !== "results");
  $("#panel-history").classList.toggle("hidden", name !== "history");
}

function renderTools() {
  const grid = $("#tools-grid");
  grid.innerHTML = "";
  if (!state.target) {
    grid.innerHTML = `<p class="hint">Analysez une cible pour afficher les outils compatibles.</p>`;
    return;
  }
  const applicable = TOOLS.filter(t => t.targets.includes(state.target.type));
  if (!applicable.length) {
    grid.innerHTML = `<p class="hint">Aucun outil intégré pour ce type de cible. Voir l'onglet Dorks.</p>`;
    return;
  }
  const blocked = !state.gateDecision?.allowed;
  for (const tool of applicable) {
    const card = document.createElement("div");
    card.className = "tool-card";
    card.innerHTML = `
      <div class="tool-head">
        <span class="tool-title">${escapeHtml(tool.label)}</span>
        <span class="pill pill-${tool.kind === "local" ? "local" : "api"}">${tool.kind}</span>
      </div>
      <div class="tool-desc">${escapeHtml(tool.description)}</div>
      <button class="btn btn-primary" type="button" ${blocked ? "disabled" : ""} data-tool="${tool.id}">
        ${blocked ? "Bloqué par le gate" : "Exécuter"}
      </button>
    `;
    card.querySelector("button").addEventListener("click", () => runTool(tool));
    grid.appendChild(card);
  }
}

function renderLinks() {
  const container = $("#links-tree");
  container.innerHTML = "";
  if (!state.target) {
    container.innerHTML = `<p class="hint">Analysez une cible pour afficher les recherches ciblées.</p>`;
    return;
  }
  const sections = LINK_TREE[state.target.type] || [];
  if (!sections.length) {
    container.innerHTML = `<p class="hint">Aucun dork prédéfini pour ce type.</p>`;
    return;
  }
  for (const section of sections) {
    const wrap = document.createElement("div");
    wrap.className = "link-tree-section";
    wrap.innerHTML = `<h3>${escapeHtml(section.title)} <span class="pill pill-dork">${section.links.length}</span></h3>`;
    const grid = document.createElement("div");
    grid.className = "grid";
    for (const link of section.links) {
      const url = link.url(state.target.value);
      const card = document.createElement("div");
      card.className = "link-card";
      card.innerHTML = `
        <div class="link-head">
          <span class="link-title">${escapeHtml(link.label)}</span>
          <span class="pill pill-dork">${escapeHtml(link.tag || "open")}</span>
        </div>
        <div class="link-desc">${escapeHtml(link.description || "")}</div>
        <a class="btn btn-primary" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">Lancer</a>
      `;
      grid.appendChild(card);
    }
    wrap.appendChild(grid);
    wrap.querySelector("h3").addEventListener("click", () => wrap.classList.toggle("collapsed"));
    container.appendChild(wrap);
  }
}

function renderResults() {
  const summary = $("#results-summary");
  const list = $("#results-list");
  list.innerHTML = "";
  if (!state.results.length) {
    summary.innerHTML = `<p class="hint">Aucun résultat encore. Lancez un outil depuis l'onglet "Outils".</p>`;
    return;
  }
  const agg = aggregateConfidence(state.results);
  summary.innerHTML = `
    <p><strong>${state.results.length}</strong> résultats ·
      Confiance agrégée&nbsp;: <span class="pill pill-${confClass(agg)}">${agg}</span></p>
  `;
  for (const r of state.results) {
    const card = document.createElement("div");
    card.className = "result-card";
    const body = r.data ? `<pre>${escapeHtml(JSON.stringify(r.data, null, 2))}</pre>` : "";
    const err = r.error ? `<p class="hint" style="color:#fca5a5">${escapeHtml(r.error)}</p>` : "";
    card.innerHTML = `
      <div class="result-head">
        <strong>${escapeHtml(r.source)}</strong>
        <span class="pill pill-${r.status === "success" ? "high" : r.status === "partial" ? "med" : "low"}">${r.status}</span>
        <span class="pill pill-${confClass(r.confidence)}">${r.confidence}</span>
      </div>
      ${err}
      <div class="result-body">${body}</div>
    `;
    list.appendChild(card);
  }
}

function confClass(c) {
  return { LOW: "low", MEDIUM: "med", HIGH: "high", VERY_HIGH: "veryhigh" }[c] || "low";
}

function aggregateConfidence(results) {
  const rank = { LOW: 1, MEDIUM: 2, HIGH: 3, VERY_HIGH: 4 };
  const successes = results.filter(r => r.status === "success");
  if (!successes.length) return "LOW";
  let max = 0;
  for (const r of successes) max = Math.max(max, rank[r.confidence] || 1);
  // Corroboration bonus: ≥3 independent sources at ≥HIGH → VERY_HIGH
  const highCount = successes.filter(r => (rank[r.confidence] || 1) >= 3).length;
  if (highCount >= 3) max = 4;
  return ["LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"][max];
}

function renderHistory() {
  const list = $("#history-list");
  list.innerHTML = "";
  if (!state.history.length) {
    list.innerHTML = `<li>Aucune mission enregistrée.</li>`;
    return;
  }
  for (const m of state.history) {
    const li = document.createElement("li");
    li.textContent = `${m.ts} · [${m.scope}] ${m.targetType}:${m.target} → ${m.tools.join(", ")}`;
    list.appendChild(li);
  }
}

async function runTool(tool) {
  const btn = document.querySelector(`[data-tool="${tool.id}"]`);
  if (btn) { btn.disabled = true; btn.innerHTML = `<span class="spinner"></span> en cours`; }
  try {
    const result = await tool.run(state.target.value);
    state.results.unshift(result);
  } catch (e) {
    state.results.unshift({
      source: tool.id,
      status: "failed",
      confidence: "LOW",
      error: `${e.name || "Error"}: ${e.message || e}`,
    });
  }
  if (btn) { btn.disabled = false; btn.textContent = "Relancer"; }
  logMission([tool.id]);
  renderResults();
  selectTab("results");
}

function logMission(toolIds) {
  const entry = {
    ts: new Date().toISOString(),
    scope: state.scope,
    target: state.target.value,
    targetType: state.target.type,
    tools: toolIds,
  };
  state.history.unshift(entry);
  state.history = state.history.slice(0, 200);
  saveHistory(state.history);
  renderHistory();
}

function analyze() {
  const raw = $("#target-input").value.trim();
  if (!raw) return;
  state.target = detectTargetType(raw);
  state.gateDecision = evaluateGate(state.target, state.scope);
  state.results = [];
  renderTargetType();
  renderGate();
  showTabs();
  selectTab("tools");
  renderTools();
  renderLinks();
  renderResults();
}

function wireUp() {
  $("#scope-select").value = state.scope;
  $("#scope-select").addEventListener("change", e => {
    state.scope = e.target.value;
    renderScopeHelp();
    if (state.target) {
      state.gateDecision = evaluateGate(state.target, state.scope);
      renderGate();
      renderTools();
    }
  });
  renderScopeHelp();

  $("#detect-btn").addEventListener("click", analyze);
  $("#target-input").addEventListener("keydown", e => {
    if (e.key === "Enter") analyze();
  });

  $$(".tab").forEach(t => t.addEventListener("click", () => selectTab(t.dataset.tab)));

  $$("[data-close]").forEach(b => b.addEventListener("click", () => {
    $("#" + b.dataset.close).classList.add("hidden");
  }));

  $("#export-btn").addEventListener("click", exportHistory);
  $("#clear-btn").addEventListener("click", () => {
    if (!confirm("Effacer tout le journal local ?")) return;
    state.history = [];
    clearHistory();
    renderHistory();
  });

  renderHistory();
}

// PWA install
let deferredInstall = null;
window.addEventListener("beforeinstallprompt", e => {
  e.preventDefault();
  deferredInstall = e;
  $("#install-btn").classList.remove("hidden");
});
$("#install-btn")?.addEventListener("click", async () => {
  if (!deferredInstall) return;
  deferredInstall.prompt();
  await deferredInstall.userChoice;
  deferredInstall = null;
  $("#install-btn").classList.add("hidden");
});

// Service worker for offline UI shell
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  });
}

// Export enum for debugging in dev console.
window.__OMEGA__ = { state, TargetType };

wireUp();
