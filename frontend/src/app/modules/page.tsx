import { listModules } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function ModulesPage() {
  let modules: Awaited<ReturnType<typeof listModules>> = [];
  let error: string | null = null;

  try {
    modules = await listModules();
  } catch (e) {
    error = e instanceof Error ? e.message : "unknown error";
  }

  return (
    <main className="mx-auto min-h-screen max-w-5xl px-6 py-16">
      <h1 className="gradient-text text-4xl font-black">Modules OSINT</h1>
      <p className="mt-2 text-sm text-slate-400">
        Modules enregistrés dans le backend.
      </p>

      {error && (
        <div className="mt-6 rounded-2xl border border-red-500/30 bg-red-500/5 p-4 text-sm text-red-200">
          Impossible de joindre l&apos;API&nbsp;: {error}
        </div>
      )}

      <ul className="mt-8 grid gap-4 md:grid-cols-2">
        {modules.map((m) => (
          <li
            key={m.name}
            className="rounded-2xl border border-slate-700/60 bg-slate-900/50 p-5"
          >
            <div className="flex items-center justify-between">
              <h2 className="font-mono text-lg font-semibold text-accent-blue">
                {m.name}
              </h2>
              <div className="flex gap-1">
                {m.confidence_levels.map((c) => (
                  <span
                    key={c}
                    className="rounded-full border border-slate-600 px-2 py-0.5 text-[10px] text-slate-300"
                  >
                    {c}
                  </span>
                ))}
              </div>
            </div>
            <p className="mt-2 text-sm text-slate-300">{m.description}</p>
          </li>
        ))}
      </ul>
    </main>
  );
}
