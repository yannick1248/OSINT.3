const $ = (selector) => document.querySelector(selector);
const modulesEl = $("#modules");
const resultsEl = $("#results");
const emptyEl = $("#empty-state");
const form = $("#investigation-form");
const statusDot = $("#api-status");
const statusText = $("#api-status-text");
const moduleCount = $("#module-count");

function setStatus(kind, text, detail) {
  statusDot.className = `status-dot ${kind}`;
  statusText.textContent = text;
  moduleCount.textContent = detail;
}

function chip(label) {
  return `<span class="pill">${label}</span>`;
}

async function loadModules() {
  try {
    const response = await fetch("/api/v1/modules");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const modules = await response.json();
    modulesEl.innerHTML = modules.map((module) => `
      <article class="module">
        <strong>${module.name}<span class="pill">${module.required_env.length ? "clé API" : "sans clé"}</span></strong>
        <p class="muted">${module.description || "Module OSINT"}</p>
        <div>${module.required_inputs.map((item) => chip(`input: ${item}`)).join("") || chip("input contextuel")}</div>
        <div>${module.required_env.map((item) => chip(`env: ${item}`)).join("")}</div>
      </article>`).join("");
    setStatus("ok", "API connectée", `${modules.length} modules chargés`);
  } catch (error) {
    modulesEl.innerHTML = `<div class="empty-state">Impossible de charger les modules: ${error.message}</div>`;
    setStatus("bad", "API indisponible", error.message);
  }
}

function formPayload() {
  const data = new FormData(form);
  return Object.fromEntries([...data.entries()].filter(([, value]) => String(value).trim() !== ""));
}

function renderReport(report) {
  const skipped = report.results.filter((item) => item.metadata?.skipped).length;
  const failed = report.results.filter((item) => !item.ok && !item.metadata?.skipped).length;
  const findings = report.findings.length;
  emptyEl.hidden = true;
  resultsEl.hidden = false;
  resultsEl.innerHTML = `
    <div class="summary-grid">
      <div class="metric"><small>Investigation</small><b>${report.investigation_id.slice(0, 8)}</b></div>
      <div class="metric"><small>Findings</small><b>${findings}</b></div>
      <div class="metric"><small>Modules ignorés</small><b>${skipped}</b></div>
      <div class="metric"><small>Erreurs</small><b>${failed}</b></div>
    </div>
    <h3>Fiche entité</h3>
    <pre>${JSON.stringify(report.entity, null, 2)}</pre>
    <h3>Synthèse modules</h3>
    <table class="result-table">
      <thead><tr><th>Module</th><th>Statut</th><th>Findings</th><th>Erreurs</th></tr></thead>
      <tbody>${report.results.map((item) => `
        <tr>
          <td><strong>${item.module}</strong></td>
          <td class="${item.ok ? "ok-text" : "bad-text"}">${item.metadata?.skipped ? "skipped" : item.ok ? "ok" : "error"}</td>
          <td>${item.findings.length}</td>
          <td>${item.errors.join("<br>") || "—"}</td>
        </tr>`).join("")}</tbody>
    </table>
    <h3>Findings normalisés</h3>
    <pre>${JSON.stringify(report.findings, null, 2)}</pre>
    <h3>Audit trail</h3>
    <pre>${JSON.stringify(report.audit_trail, null, 2)}</pre>`;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = form.querySelector("button[type='submit']");
  button.disabled = true;
  button.textContent = "Enquête en cours…";
  try {
    const response = await fetch("/api/v1/investigate/missing-person", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(formPayload()),
    });
    const body = await response.json();
    if (!response.ok) throw new Error(typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail));
    renderReport(body);
  } catch (error) {
    emptyEl.hidden = true;
    resultsEl.hidden = false;
    resultsEl.innerHTML = `<div class="empty-state bad-text">${error.message}</div>`;
  } finally {
    button.disabled = false;
    button.textContent = "Lancer l'enquête";
  }
});

$("#fill-demo").addEventListener("click", () => {
  form.elements.name.value = "Jane Doe";
  form.elements.username.value = "janedoe";
  form.elements.email.value = "jane@example.org";
  form.elements.phone.value = "+41790000000";
  form.elements.domain.value = "example.org";
});

loadModules();
