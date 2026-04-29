# OSINT OMÉGA — Frontend

Next.js 15 (App Router) + TypeScript strict + Tailwind CSS.

## Commandes

```bash
npm install
npm run dev        # http://localhost:3000
npm run type-check
npm run build
```

## API

Le frontend pointe vers l'API via `NEXT_PUBLIC_API_BASE_URL` (défaut `http://localhost:8000`).

## PWA (iPhone)

- Manifest web (`/manifest.webmanifest`) et icônes générées.
- Service Worker (`public/sw.js`) avec stratégie cache-first puis network.
- Installation iPhone : Safari → Partager → **Sur l'écran d'accueil**.
