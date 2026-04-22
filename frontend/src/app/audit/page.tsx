const ENTRIES = [
  '08:42 — run_module(domain_lookup) — actor: mobile_ops',
  '08:37 — export rapport PDF — actor: analyste_1',
  '08:31 — ouverture dossier INV-2026-041 — actor: lead_investigator',
];

export default function AuditPage() {
  return (
    <main className="mx-auto min-h-screen max-w-5xl px-6 py-10">
      <h1 className="gradient-text text-3xl font-black md:text-4xl">Audit trail</h1>
      <p className="mt-2 text-sm text-slate-400">Journaux d’activité pour suivi opérationnel.</p>

      <div className="mt-6 rounded-2xl border border-slate-700/60 bg-slate-900/50 p-4">
        <ul className="space-y-2 text-sm text-slate-300">
          {ENTRIES.map((entry) => (
            <li key={entry} className="rounded-lg border border-slate-800 p-3 font-mono">
              {entry}
            </li>
          ))}
        </ul>
      </div>
    </main>
  );
}
