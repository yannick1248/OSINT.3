import type { Metadata, Viewport } from 'next';
import './globals.css';
import { MobileNav } from './components/mobile-nav';
import { SWRegister } from './components/sw-register';

export const metadata: Metadata = {
  title: 'OSINT OMÉGA AI',
  description: "Plateforme d'investigation OSINT modulaire — usage légal et éthique uniquement.",
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'OSINT OMÉGA AI',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  themeColor: '#0ea5e9',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body className="min-h-screen bg-slate-950 pb-16 antialiased md:pb-0">
        <SWRegister />
        {children}
        <MobileNav />
      </body>
    </html>
  );
}
