export const metadata = { title: 'Overview · RM-KI Operator' };

export default function OverviewPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Plattform-Übersicht</h1>
      <p className="text-[hsl(var(--color-muted-foreground))]">
        Phase-1-Skelett. Hier kommt die Live-Plattform-Übersicht: Container-Health, CP-Status,
        Disk-/GPU-Auslastung, Evidence-Bundle-Stand. Alles read-only, kein Mutation-Recht.
      </p>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[
          { label: 'Container running', value: '—' },
          { label: 'CP-Slice (Head)', value: '—' },
          { label: 'Evidence-Bundle', value: '—' },
          { label: 'Disk used', value: '—' },
          { label: 'GPU temp', value: '—' },
          { label: 'Active alerts', value: '—' },
        ].map((c) => (
          <div key={c.label} className="rounded border p-4">
            <div className="text-xs uppercase text-[hsl(var(--color-muted-foreground))]">
              {c.label}
            </div>
            <div className="mt-1 text-2xl font-semibold">{c.value}</div>
          </div>
        ))}
      </div>
      <div className="rounded border border-dashed p-4 text-sm text-[hsl(var(--color-muted-foreground))]">
        TODO Phase 1: SSH-Bridge-Service zur DGX, Live-Daten via Server Components abrufen.
      </div>
    </div>
  );
}
