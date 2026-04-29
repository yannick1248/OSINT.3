'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const ITEMS = [
  { href: '/', label: 'Accueil' },
  { href: '/modules', label: 'Modules' },
  { href: '/investigations', label: 'Investigations' },
  { href: '/audit', label: 'Audit' },
];

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed inset-x-0 bottom-0 z-50 border-t border-slate-800 bg-slate-950/95 px-2 py-2 backdrop-blur md:hidden">
      <ul className="grid grid-cols-4 gap-1">
        {ITEMS.map((item) => {
          const active = pathname === item.href;
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                className={`block rounded-lg px-2 py-2 text-center text-xs ${
                  active ? 'bg-sky-500/20 text-sky-300' : 'text-slate-400'
                }`}
              >
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
