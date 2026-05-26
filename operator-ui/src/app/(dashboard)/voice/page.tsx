import { voiceTiles } from '@/lib/voice-tiles';

export const metadata = { title: 'Voice / Telefonie · RM-KI Operator' };

const STATUS_BADGE: Record<string, { label: string; className: string }> = {
  live: { label: 'LIVE', className: 'bg-green-100 text-green-800 border-green-300' },
  soon: { label: 'COMING SOON', className: 'bg-amber-100 text-amber-800 border-amber-300' },
  maintenance: { label: 'WARTUNG', className: 'bg-red-100 text-red-800 border-red-300' },
};

export default function VoicePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Sprach-Agenten & Telefonie</h1>
        <p className="mt-1 text-sm text-[hsl(var(--color-muted-foreground))]">
          Native Voice-Bot- und Telefonie-Integration auf der DGX Spark. STT (Faster-Whisper)
          und TTS (Piper) sind bereits live. Die LiveKit-/SIP-/Pipecat-Schicht ist
          productized (Slice <code>voice-stack-v1</code>) und wartet auf die
          Netzwerk-Entscheidung (UDP/TURN-Weg) sowie die Promotion-Phrase.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {voiceTiles.map((t) => {
          const badge = STATUS_BADGE[t.status];
          return (
            <a
              key={t.id}
              href={t.href}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded border p-4 transition hover:border-[hsl(var(--color-primary))] hover:shadow"
            >
              <div className="flex items-start justify-between gap-2">
                <h2 className="font-semibold leading-snug">{t.title}</h2>
                <span
                  className={`whitespace-nowrap rounded border px-2 py-0.5 text-[10px] font-medium uppercase ${badge.className}`}
                >
                  {badge.label}
                </span>
              </div>
              <p className="mt-2 text-sm text-[hsl(var(--color-muted-foreground))]">
                {t.description}
              </p>
              <div className="mt-3 flex flex-wrap gap-1">
                {t.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded bg-[hsl(var(--color-muted))] px-1.5 py-0.5 text-[10px] text-[hsl(var(--color-muted-foreground))]"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </a>
          );
        })}
      </div>

      <details className="rounded border border-dashed p-4 text-sm">
        <summary className="cursor-pointer font-medium">
          Architektur & Promotion-Status
        </summary>
        <div className="mt-3 space-y-2 text-[hsl(var(--color-muted-foreground))]">
          <p>
            Slice-ID: <code>voice-stack-v1</code> · Promotion-Phrase:{' '}
            <code>Genehmigt: promote voice-stack-v1 to deploy</code>
          </p>
          <p>
            Stack: LiveKit Server + LiveKit SIP + LiveKit Agents (Pipecat-Library) + coturn.
            Additiv zu bestehendem Faster-Whisper, OpenedAI-Speech, LiteLLM, Langfuse, Keycloak.
          </p>
          <p>
            Blocker fuer Deploy: Netzwerk-Entscheidung Weg A (Direkt-Public-IP+UDP-Forward) /
            B (Cloudflare Spectrum) / C (Cloud-VPS-Relay) / D (Tailscale-only). Cloudflare-Tunnel
            allein reicht fuer WebRTC und SIP nicht.
          </p>
          <p>
            Productization-Artefakte:{' '}
            <code>~/Documents/voice-stack-productization-2026-05-26/</code> — ADR, Compose-Overlay,
            Cloudflare-Plan, LiteLLM-Patch, Pipecat-Agent-Runner, Promotion-Checklist.
          </p>
        </div>
      </details>
    </div>
  );
}
