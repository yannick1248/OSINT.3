import Link from 'next/link';

const DISCLAIMER =
  'Usage légal et éthique uniquement. Toute requête est journalisée pour audit trail.';

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col items-start gap-8 px-6 py-10">
      <header className="space-y-3">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-400">OSINT OMÉGA AI</p>
        <h1 className="gradient-text text-4xl font-black leading-tight md:text-5xl">
          Web app prête pour iPhone
        </h1>
        <p className="max-w-2xl text-base text-slate-300 md:text-lg">
          Ajoutez l&apos;app à l&apos;écran d&apos;accueil iOS via Safari (Partager → Sur l&apos;écran d&apos;accueil)
          pour un accès rapide, même avec réseau instable.
        </p>
      </header>

      <section className="rounded-2xl border border-amber-500/30 bg-amber-500/5 p-4 text-sm text-amber-200">
        <strong className="mr-2">Avertissement légal :</strong>
        {DISCLAIMER}
      </section>

      <section className="rounded-2xl border border-sky-500/30 bg-sky-500/5 p-4 text-sm text-sky-200">
        <strong className="mr-2">Mode hors-ligne :</strong>
        Le shell de navigation est mis en cache via Service Worker.
      </section>

      <section className="grid w-full gap-4 md:grid-cols-3">
        {[
          { title: 'Modules', href: '/modules', desc: 'Parcourir les modules OSINT enregistrés.' },
          { title: 'Investigations', href: '/investigations', desc: 'Cas récents et suivi d’état.' },
          { title: 'Audit trail', href: '/audit', desc: 'Historique des actions journalisées.' },
        ].map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="group rounded-2xl border border-slate-700/60 bg-slate-900/50 p-5 transition hover:border-accent-blue hover:bg-slate-900"
          >
            <h2 className="text-lg font-semibold text-slate-100 group-hover:text-accent-blue">{card.title}</h2>
            <p className="mt-2 text-sm text-slate-400">{card.desc}</p>
          </Link>
        ))}
      </section>
    </main>
  );
}
