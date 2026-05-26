// Voice / Telefonie Tile-Definitions (Slice voice-stack-v1, 2026-05-26).
// Append-only data; status switches from "soon" to "live" via /api/voice/status
// once the LiveKit/SIP stack is promoted to deploy.

export type VoiceTileStatus = 'soon' | 'live' | 'maintenance';

export type VoiceTile = {
  id: string;
  title: string;
  description: string;
  href: string;
  statusUrl?: string;
  status: VoiceTileStatus;
  tags: string[];
};

export const voiceTiles: VoiceTile[] = [
  {
    id: 'voice-customer-service',
    title: 'Kundenservice-Sprachbot',
    description:
      'Inbound-Anrufe -> STT (Whisper) -> LLM (LiteLLM) -> TTS (Piper) -> Antwort. ' +
      'EU-AI-Act-Disclosure am Call-Anfang. Langfuse-Trace pro Call.',
    href: 'https://voice.ben-e-fit.ai/admin/customer-service',
    statusUrl: 'https://agents.ben-e-fit.ai/healthz',
    status: 'soon',
    tags: ['voice', 'stt', 'tts', 'llm', 'telefonie'],
  },
  {
    id: 'voice-pbx-integration',
    title: 'TK-Anlagen-Integration',
    description:
      'SIP-Trunk-Anbindung an vorhandene PBX (Sipgate, NFON, Telekom CompanyFlex, ' +
      'easybell, AudioCodes SBC). Inbound + Outbound + Call-Transfer.',
    href: 'https://voice.ben-e-fit.ai/admin/trunks',
    status: 'soon',
    tags: ['sip', 'pbx', 'telefonie'],
  },
  {
    id: 'voice-webrtc-widget',
    title: 'WebRTC-Sprach-Widget',
    description:
      'Browser-basierter Sprach-Assistent - einbettbar als <script> auf jeder ' +
      'Tenant-Website. Nutzt LiveKit Rooms direkt, keine Telefonie noetig.',
    href: 'https://voice.ben-e-fit.ai/widget/demo',
    status: 'soon',
    tags: ['webrtc', 'widget', 'voice'],
  },
  {
    id: 'voice-call-analytics',
    title: 'Call-Analytics',
    description:
      'Live-Dashboard: aktive Calls, durchschnittliche Latenz, STT-Confidence, ' +
      'Langfuse-Traces pro Tenant. Drill-down zu Transkripten in OWUI-KB.',
    href: 'https://trace.ben-e-fit.ai/?tag=channel%3Dvoice',
    statusUrl: 'https://trace.ben-e-fit.ai/api/public/health',
    status: 'soon',
    tags: ['observability', 'voice', 'langfuse'],
  },
  {
    id: 'voice-admin-livekit',
    title: 'LiveKit Admin',
    description:
      'Server-Side-Admin fuer Rooms, Tokens, SIP-Trunks. Cloudflare-Access geschuetzt.',
    href: 'https://livekit.ben-e-fit.ai/',
    status: 'soon',
    tags: ['admin', 'livekit'],
  },
  {
    id: 'voice-stt-whisper',
    title: 'STT — Faster-Whisper (live)',
    description:
      'Speech-to-Text Service, OpenAI-API-kompatibel. Wird vom Voice-Agent und ' +
      'von Meetily fuer Transkripte genutzt. Liefert ohne Bearer 401.',
    href: 'https://whisper.ben-e-fit.ai/',
    statusUrl: 'https://whisper.ben-e-fit.ai/',
    status: 'live',
    tags: ['stt', 'whisper', 'live'],
  },
  {
    id: 'voice-tts-piper',
    title: 'TTS — OpenedAI-Speech / Piper (live)',
    description:
      'Text-to-Speech Service, OpenAI-API-kompatibel. Default tts-1 / tts-1-hd ' +
      'in Dify und LiteLLM. Liefert ohne Bearer 401.',
    href: 'https://tts.impulse.kim/',
    statusUrl: 'https://tts.impulse.kim/',
    status: 'live',
    tags: ['tts', 'piper', 'live'],
  },
];
