import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'OSINT OMÉGA AI',
    short_name: 'OMEGA',
    description: 'Web app OSINT installable et utilisable sur iPhone (mode hors ligne partiel).',
    start_url: '/',
    display: 'standalone',
    background_color: '#020617',
    theme_color: '#0ea5e9',
    orientation: 'portrait',
    lang: 'fr',
    icons: [
      { src: '/icon?size=192', sizes: '192x192', type: 'image/png' },
      { src: '/icon?size=512', sizes: '512x512', type: 'image/png' },
      { src: '/apple-icon', sizes: '180x180', type: 'image/png' },
    ],
  };
}
