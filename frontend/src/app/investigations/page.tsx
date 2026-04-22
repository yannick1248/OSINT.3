const CASES = [
  { id: 'INV-2026-041', title: 'Fuite de données', status: 'En cours' },
  { id: 'INV-2026-038', title: 'Usurpation d’identité', status: 'Validation' },
  { id: 'INV-2026-032', title: 'Fraude au domaine', status: 'Clôturé' },
];

export default function InvestigationsPage() {
  return (
    <main className="mx-auto min-h-screen max-w-5xl px-6 py-10">
      <h1 className="gradient-text text-3xl font-black md:text-4xl">Investigations</h1>
      <p className="mt-2 text-sm text-slate-400">Vue mobile-first, optimisée pour iPhone.</p>

      <ul className="mt-6 space-y-3">
        {CASES.map((item) => (
          <li key={item.id} className="rounded-2xl border border-slate-700/60 bg-slate-900/50 p-4">
            <p className="font-mono text-xs text-slate-400">{item.id}</p>
            <h2 className="mt-1 text-base font-semibold text-slate-100">{item.title}</h2>
            <p className="mt-1 text-sm text-sky-300">{item.status}</p>
          </li>
        ))}
      </ul>
    </main>
  );
}
