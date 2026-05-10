# TENANT-ISOLATION-CONTRACT — KPI Enterprise Mining

**Stand:** 2026-05-10 · abgeleitet aus [`../ARCHITECTURE-v2.md`](../ARCHITECTURE-v2.md) (NFR-01, §3.5)
**Owner:** Tenants (kpi-tenant-onboarding Skill)

> Verbindlicher Vertrag für Tenant-Isolation. Verstöße sind release-blocking.
> Negative Cross-Tenant-Tests sind Pflicht in CI.

---

## 1. Kanonische Tenant-IDs (Bootstrap)

| `tenant_id` | Slug | Brand | Realm | Default-Klassifikation | External-LLM |
| --- | --- | --- | --- | --- | --- |
| `tnt_medialine` | medialine | medialine | `medialine` | internal | nein |
| `tnt_benefit` | ben-e-fit | ben-e-fit | `ben-e-fit` | internal | nein |
| `tnt_kiguru` | ki-guru | ki-guru | `ki-guru` | internal | nein |
| `tnt_demo` | demo | medialine | `demo` | public | ja (gated) |

Pattern für Mandanten: `tnt_[a-z0-9]{4,32}`.

## 2. Pflicht-Layer-Mapping

Jeder Tenant **muss** folgende Ressourcen besitzen — Onboarding-Wizard provisioniert sie:

| Layer | Ressource | Naming | Provisioniert von |
| --- | --- | --- | --- |
| Auth | Keycloak Realm | `<slug>` | tenant-onboarding |
| Auth | OIDC Client `kpi-mining-bff-<slug>` | – | tenant-onboarding |
| Postgres | Schema | `tnt_<slug>` | tenant-onboarding migration |
| Postgres | RLS Policy auf shared tables | `USING (tenant_id = current_setting('app.tenant')::text)` | dbt + bootstrap |
| MinIO | Bucket-Prefix | `s3://lake/<tenant_id>/{bronze,silver,gold,evidence,models}/` | tenant-onboarding |
| MinIO | Service-Account + STS | tenant-bound IAM Policy | tenant-onboarding |
| ClickHouse | Database | `kpi_<slug>` | tenant-onboarding |
| ClickHouse | User + Quota | `kpi_<slug>_app` | tenant-onboarding |
| Trino | Catalog/Schema-Mapping | `kpi.<slug>` | trino config + ACL |
| Qdrant | Collection | `kpi-<slug>` | tenant-onboarding |
| Qdrant | API-Key | `qdr_<tenant_id>` | tenant-onboarding |
| OpenSearch | Index-Pattern | `kpi-<slug>-*` mit DLS Filter | tenant-onboarding |
| Neo4j | Database (Enterprise) oder Property+RBAC (Community) | `kpi_<slug>` | tenant-onboarding |
| LiteLLM | Virtual Key | `vk_<tenant_id>` mit Quota | tenant-onboarding |
| Langfuse | Project | `<slug>` | tenant-onboarding |
| n8n | Project / Tag | `<slug>` | tenant-onboarding |
| Audit | ClickHouse-Tabelle | `agent_runs_<slug>` immutable, TTL 7y | tenant-onboarding |

## 3. JWT-Claim-Vertrag

Jeder Bearer-Token hat die folgenden Pflicht-Claims:

```json
{
  "sub": "user@tenant.example",
  "tenant_id": "tnt_acme",
  "tenant_slug": "acme",
  "realm_access": { "roles": ["cfo", "tenant_admin"] },
  "scope": "openid kpi.read metric.write tree.write brief.read",
  "iss": "https://auth.medialine.app/realms/acme",
  "exp": 1715260800
}
```

`tenant_id` und `tenant_slug` sind **mandatory**. Fehlen sie, antwortet das Gateway mit `401`.

## 4. Gateway-Pflicht-Sequenz pro Request

```
1. Verify JWT signature gegen Realm-JWKS
2. Extract tenant_id, tenant_slug, roles
3. Resolve target tenant für angefragte Ressource (path/query)
4. Wenn tenant != JWT-tenant_id und kein platform_admin Role → 403
5. SET app.tenant = tenant_id (Postgres-Session)
6. Inject tenant_id als Tag in Outbound-Calls (LiteLLM, Langfuse, ClickHouse)
7. Forward + Log
```

## 5. Datenklassifikation und externe Modelle

| Klassifikation | Beschreibung | Externer LLM-Call |
| --- | --- | --- |
| `public` | öffentlich verfügbar (z. B. Markt-Benchmarks) | erlaubt, wenn Tenant-Policy erlaubt |
| `internal` | intern, kein PII | erlaubt nach explizitem Skill-Manifest `external = true` und Tenant-Policy |
| `confidential` | sensibel, kein PII (z. B. Financials) | nur lokal |
| `pii` | PII-haltig | nur lokal, **niemals** extern |

Presidio scannt **vor** jedem LLM-Call. Hit auf PII bei `internal/public` → Reklassifikation auf `pii` + Force-Local + Audit.

## 6. Negative Deny-Tests (Release-Gate)

CI startet zwei Test-Tenants `tnt_test_a` und `tnt_test_b` und prüft folgende Cross-Tenant-Zugriffe:

| Test | Erwartetes Ergebnis |
| --- | --- |
| Tenant A liest Postgres-Zeile von B | empty (RLS) oder 403 |
| Tenant A queried Trino auf B's Schema | 403 (ACL) |
| Tenant A liest MinIO-Object von B | 403 (Bucket-Policy) |
| Tenant A queried ClickHouse DB von B | 403 (RBAC) |
| Tenant A queried Qdrant Collection von B | 401 (API-Key) |
| Tenant A liest OpenSearch Index `kpi-b-*` | 0 docs (DLS) |
| Tenant A traversiert Neo4j-Property `tenant_id=B` | 0 nodes (procedure) |
| Tenant A's Briefing erscheint in B's Langfuse-Projekt | nein |
| Tenant A's LiteLLM-Virtual-Key wird mit B's Tag geloggt | nein |

Schlägt **irgendein** Test fehl: Release blockiert. Skript: `evals/tenant-deny/` im rm-repo.

## 7. Tenant-Lifecycle

### 7.1 Onboarding (Wizard)

1. POST `/v1/tenants` mit `slug, display_name, brand, admin_email`.
2. Provisionierung (idempotent, mit Rollback): Keycloak → Postgres → MinIO → ClickHouse → Trino → Qdrant → OpenSearch → Neo4j → LiteLLM → Langfuse → n8n → Audit.
3. Initial Admin-Email mit Reset-Link.
4. Brand-Switch via `data-brand` im Cockpit.
5. Connector-Setup-Wizard (mind. 1 Source).
6. Initial KPI-Discovery (asynchron).
7. Approver-Rollen festlegen.

**Time-to-First-Briefing-Ziel:** ≤ 4h.

### 7.2 Offboarding

- Soft-Delete: Tenant `status = suspended`, alle Reads liefern 410, Writes 423.
- Hard-Delete (nach Vertragsende + Aufbewahrungsfrist): alle Layer-Ressourcen werden in umgekehrter Onboarding-Reihenfolge entfernt; Audit-Log bleibt nach HGB §257 (10 Jahre) als immutable Snapshot in MinIO.

### 7.3 Backup/Restore pro Tenant

- Postgres: pg_dump per Schema, täglich.
- MinIO: restic-Snapshot mit Tag `tenant=<id>`, täglich.
- ClickHouse: BACKUP TABLE pro tenant DB, täglich.
- Qdrant: Snapshot pro Collection, täglich.
- Neo4j: dump-database pro Tenant, täglich.
- Restore-Test: monatlich auf `kpi.staging.medialine.app` für 1 zufälligen Tenant.

## 8. Audit-Trail-Pflicht

Pro Agent-Run:

- `run_id`, `tenant_id`, `agent`, `status`, `started/ended_at`,
- `tools_used` mit args (PII-redacted via Presidio),
- `llm_calls` mit Model, Tokens, Cost, **`external` Flag**, **`policy_decision` Reason**,
- `evidence_bundle` URI (signed, 24h),
- `approval` Block (required, approvers, granted),
- `rollback_snapshot` URI.

Persistiert in ClickHouse `agent_runs_<slug>` (immutable) + Langfuse Project. Cross-Tenant-Read in Langfuse ist deaktiviert (Project pro Tenant).

## 9. Verstöße / Eskalation

- Cross-Tenant-Leak (auch nur theoretisch im Code-Pfad) → Release-Blocker P0.
- Externer LLM-Call mit PII → Incident-Report nach EU AI Act Art. 26 Pflicht.
- Fehlender `tenant_id`-Claim → Gateway 401, Audit, Auto-Alert.
- Fehlerhafte RLS-Policy beim Schema-Migration → Rollback automatisch.
