import Link from 'next/link';
import type { ReactNode } from 'react';

const NAV = [
  { href: '/overview', label: 'Overview' },
  { href: '/cp-status', label: 'CP-Status' },
  { href: '/litellm', label: 'LiteLLM' },
  { href: '/cloudflare', label: 'Cloudflare' },
  { href: '/containers', label: 'Container' },
  { href: '/audits', label: 'Audits' },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="grid min-h-screen grid-cols-[240px_1fr]">
      <aside className="border-r bg-[hsl(var(--color-muted))] p-4">
        <div className="mb-6 font-semibold">RM-KI Operator</div>
        <nav className="flex flex-col gap-1 text-sm">
          {NAV.map((i) => (
            <Link key={i.href} href={i.href} className="rounded px-2 py-1.5 hover:bg-white/50">
              {i.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="p-6">{children}</main>
    </div>
  );
}
