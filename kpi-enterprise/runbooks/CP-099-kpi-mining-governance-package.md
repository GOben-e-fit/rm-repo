# CP-099 KPI Mining Governance Package — Runbook

**Status:** proposed (no-apply)
**Risk:** medium
**Mode:** observe → classify → approve → integrate
**SelfCLAW:** evidence + approval + rollback + audit Pflicht
**Stand:** 2026-05-10

> Wrapper-Runbook für die parallele KPI-Mining-Worktree.
> Verbindlich für jeden Apply-Schritt am laufenden DGX-System.
> Kein Auto-Apply. Sequenzierung: erst CP-099 schließen, dann CP-100…CP-103.

---

## 0. Verlinkung

- Architektur-Quelle: [`../ARCHITECTURE-v2.md`](../ARCHITECTURE-v2.md)
- API-Vertrag: [`../api/openapi.v1.yaml`](../api/openapi.v1.yaml)
- Tenant-Vertrag: [`../tenants/TENANT-ISOLATION-CONTRACT.md`](../tenants/TENANT-ISOLATION-CONTRACT.md)
- Agent-Topologie: [`../agents/AGENT-TOPOLOGY.md`](../agents/AGENT-TOPOLOGY.md)
- Codex-Preflight-Skript: [`../../../_dgx_cp094_work/scripts/selfclaw_cp099_kpi_mining_integration_governance.py`](../../../_dgx_cp094_work/scripts/selfclaw_cp099_kpi_mining_integration_governance.py)
- Codex v1-Materialisierung (lokal, nicht apply): [`../../../.codex-work/cp075/overrides/dev/kpi-mining/`](../../../.codex-work/cp075/overrides/dev/kpi-mining/)
- DGX-Orig-Pfad (uncommitted Override): `/opt/rm-ki-appliance/repo/overrides/dev/kpi-mining/` auf `spark-dev-01`
- Akte-Trennung: Routing-Mutationen → [`../../08-dgx-cloudflare-routing`](../../08-dgx-cloudflare-routing/), Container/Compose-Mutationen → [`../../09-dgx-core-platform`](../../09-dgx-core-platform/), LiteLLM/Langfuse/Keycloak → [`../../10-dgx-litellm-langfuse-keycloak`](../../10-dgx-litellm-langfuse-keycloak/).

## 1. Ziel

CP-099 wickelt den **untracked KPI-Mining-Override** auf der DGX governance-konform ein:

1. Inventar (Files, Größen, Typen, Secret-Scan).
2. Vergleich Container-Stand ↔ Repo-Stand ↔ Codex-v1.
3. Klassifikation (Owner, Tenant, Datenklasse, Audit-Namespace).
4. Vertrags-Definition (OpenMetadata, OpenSearch, Trino, LiteLLM, Guard, Audit, Tenant).
5. Apply-Vorbereitung (Pre-/Post-/Rollback-Smokes).
6. Stop-Kriterien.

CP-099 selbst **commited keine KPI-App-Files** und **deployed nichts**. Erst CP-100 bis CP-103 führen die normalisierte Materialisierung und das Apply durch.

## 2. Pre-Conditions

| Check | Wie | Erwartung |
| --- | --- | --- |
| Hostname | `hostname` | `spark-dev-01` |
| Branch | `git -C /opt/rm-ki-appliance/repo rev-parse --abbrev-ref HEAD` | `dev` |
| KPI-Override-Pfad existiert | `test -d /opt/rm-ki-appliance/repo/overrides/dev/kpi-mining` | true |
| Compose-Override existiert | `test -f /opt/rm-ki-appliance/repo/overrides/dev/docker-compose.kpi-mining.override.yml` | true |
| Tunnel ingress aktiv | Cloudflare API `cfd_tunnel/spark-dev-01/configurations` | enthält `kpi.* → kpi-mining:80` |
| Secrets-Scan clean | Preflight-Skript `--write-current` | `secret_pattern_hit_files: 0` |

## 3. Inventar (read-only Schritt)

```powershell
# Aus Windows via Posh-SSH (no secret echo!)
$session = New-PSSession -HostName admin@192.168.50.250
Invoke-Command -Session $session -ScriptBlock {
  cd /opt/rm-ki-appliance/repo
  python3 _dgx_cp094_work/scripts/selfclaw_cp099_kpi_mining_integration_governance.py --write-current
}
```

Ergebnis-Artefakte (im DGX-Repo):
- `selfclaw/evidence/kpi-mining-integration-governance.current.json`
- `selfclaw/policies/kpi-mining-integration-governance.json`
- `selfclaw/tests/kpi-mining-integration-governance.json`
- `selfclaw/runbooks/change-proposals/CP-099-kpi-mining-integration-governance.md`
- `docs/control-room/...` Mirror

## 4. Klassifikation

Pro File im KPI-Override mindestens entscheiden:

| Frage | Wertebereich |
| --- | --- |
| Owner-Squad | platform, product, agents, data |
| Ziel-Tenant | platform-shared, tnt_medialine, tnt_benefit, tnt_kiguru |
| Datenklasse | public, internal, confidential, pii |
| Audit-Namespace | `kpi-mining` (default) oder spezifisch |
| Cross-Tenant-Risk | none, low, medium, high |
| External LLM Touch | yes/no |

Output: `evidence/cp099/file-classification.csv`.

## 5. Vertrags-Definition (Pflicht vor CP-100)

| Plattform-Komponente | Vertrag |
| --- | --- |
| OpenMetadata | KPI-Datasets, Metric Definitions, Owners, Lineage, Sensitivity (Pflicht-Tags) |
| OpenSearch | Index-Pattern `kpi-<tenant>-{candidates,observations,evidence,search}` mit DLS |
| Trino | Catalog `kpi`, Schema `<slug>`, Read-only Views via Privacy-Gate |
| Langfuse/ClickHouse | Project + Tabelle pro Tenant, Trace pro Agent-Run |
| LiteLLM | Virtual-Keys + Tag-Convention `tenant=<id>;agent=<name>;skill=<id>` |
| Tenant Plane | `app.tenant`-Setting im Gateway, RLS auf shared Tabellen |

## 6. Apply-Sequenz CP-100 bis CP-103

| CP | Inhalt | Approval-Bedarf |
| --- | --- | --- |
| CP-100 | Cockpit-UI replace `/`, `/enterprise/`, `/console`, `/tools` | 2 reviewer + Wartungsfenster |
| CP-101 | Static `/api/v1/*` + OpenAPI-Mount für Smoke + Demo | 1 reviewer |
| CP-102 | Healthcheck-Smoke + Cloudflare Per-Path-Status | 1 reviewer |
| CP-103 | Evidence-Bundle + Apply via Wartungsfenster | 2 reviewer + DGX-Owner |

## 7. Pre-Apply-Smoke

Vor CP-103 Apply:

```powershell
# Lokal (Cache-Bust)
$paths = @('/', '/enterprise/', '/console.html', '/tools.html', '/openapi.json',
           '/api/health', '/api/v1/tenants', '/api/v1/sources', '/api/v1/metric-definitions')
foreach ($p in $paths) {
  $url = "https://kpi.medialine.app$p?_cb=$(Get-Random)"
  try {
    $r = Invoke-WebRequest -Uri $url -UseBasicParsing -MaximumRedirection 0
    "{0,-30} {1,4} {2}" -f $p, $r.StatusCode, $r.Headers['Content-Type']
  } catch {
    $sc = $_.Exception.Response.StatusCode.Value__
    "{0,-30} {1,4} ERROR" -f $p, $sc
  }
}
```

Erwartung: alle 200, korrekter Content-Type. `/` und `/enterprise/` liefern `text/html`, `/openapi.json` liefert `application/json`, `/api/health` liefert `{"status":"ok",...}`.

## 8. Post-Apply-Smoke

Zusätzlich gegen `kpi.ben-e-fit.ai` und `kpi.ki-guru.com` (Brand-Switch testen):

- DOM enthält `data-brand="ben-e-fit"` bzw. `"ki-guru"`,
- Logo-/Farb-Token wechselt,
- Cookie-Banner und Footer respektieren Brand,
- Login-Flow leitet auf passenden Keycloak-Realm um.

## 9. Rollback

Trigger: irgendein Smoke-Check ≠ 200, oder DOM-Brand-Mismatch, oder DLS-Test schlägt fehl.

```bash
# Auf DGX
cd /opt/rm-ki-appliance/repo
git checkout HEAD~1 -- overrides/dev/kpi-mining/
git checkout HEAD~1 -- overrides/dev/docker-compose.kpi-mining.override.yml
docker compose -f overrides/dev/docker-compose.dev-stack.yml up -d kpi-mining
# Re-run Pre-Apply-Smoke
```

Bei produktivem Routing-Drift zusätzlich Cloudflare-Tunnel-Configuration über Akte 08 zurückrollen.

## 10. Stop-Kriterien

- Secret-Scan-Hit auf KPI-Files → CP sofort stoppen, Datei isolieren.
- Cross-Tenant-Deny-Test rot → Stopp, an Akte 11 + 14-Owner eskalieren.
- Cloudflare zeigt mindestens 1 Path ≠ 200 → Apply nur weiter, wenn Akte 08 bestätigt, dass Drift erwartet ist.
- LiteLLM-Quota für Pilot-Tenant fehlt → Apply pausieren, Akte 10 ergänzt.

## 11. Audit-Output

Nach CP-103 sind diese Artefakte unter `evidence/<yyyy>/<mm>/<dd>/cp103/` Pflicht:

- `pre-apply-smoke.json`
- `post-apply-smoke.json`
- `cloudflare-route-snapshot.json` (sanitized)
- `compose-override-diff.txt`
- `nginx-conf-diff.txt`
- `openapi-validate.txt` (Spectral)
- `tenant-deny-test.json` (mind. 2 Test-Tenants)
- `approver-list.txt`
- `rollback-snapshot.tar.gz` (Pfad-Liste, kein Inhalt mit Secrets)

## 12. Skill-Trigger

Bei jedem Schritt: passenden Skill aktivieren (siehe [`../SKILLS.md`](../SKILLS.md)):
- Inventar/Apply → `kpi-mining-ops`
- UX-Aspekte → `kpi-mining-product`
- Eval/Smoke → `kpi-evals`
- Tenant-Vertrag → `kpi-tenant-onboarding`
