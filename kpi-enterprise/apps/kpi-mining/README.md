# KPI Enterprise Mining Override

This directory is the repo-canonical dev override for the KPI Enterprise Mining product.
It restores the stronger DGX container shape that existed outside the repository:
`/`, `/enterprise`, `/console.html`, `/tools.html`, `/openapi.json`, `/api/health`
and `/api/v1/*`.

## Runtime Contract

- `/` serves the C-Level Performance OS cockpit.
- `/enterprise/` serves the enterprise readiness and architecture map.
- `/console.html` gives a lightweight tenant-aware API smoke console.
- `/tools.html` documents the agent and tool plane for operators.
- `/openapi.json` documents the public v1 API surface.
- `/api/v1/*` first serves static JSON fallback files and then proxies misses to
  `agents-orchestrator:8000`.

The fallback JSON is intentional. It keeps route tests, UX demos and contract checks
working while the full agent/data plane is being wired behind the API.

## Product Boundary

This is not a classic BI dashboard. The target product is a tenant-aware C-Level
Performance Operating System:

- KPI discovery and metric governance
- source onboarding and data contracts
- driver trees and OKR lineage
- anomaly detection, root cause analysis and forecasting
- action orchestration with owner, SLA and approval state
- audit-ready agent execution with evidence artifacts

## Tenant and Governance Rules

- Every event, metric, trace and evidence artifact must carry `tenant_id`.
- External model usage is denied for sensitive data unless policy explicitly allows
  anonymized or public payloads.
- Runtime changes on DGX follow SelfCLAW governance: inventory, evidence, approval,
  rollback plan, validation and audit bundle.
- Release gates include cross-tenant negative tests.

## Local Validation

Run from this directory:

```powershell
powershell -ExecutionPolicy Bypass -File .\tests\validate-kpi-mining.ps1
```

On Linux/DGX:

```bash
bash ./tests/validate-kpi-mining.sh
```

Route smoke test against a running container or public domain:

```powershell
powershell -ExecutionPolicy Bypass -File .\tests\route-smoke.ps1 -BaseUrl http://localhost:8088
powershell -ExecutionPolicy Bypass -File .\tests\route-smoke.ps1 -BaseUrl https://kpi.medialine.app
```

On Linux/DGX:

```bash
bash ./tests/route-smoke.sh http://localhost:8088
bash ./tests/route-smoke.sh https://kpi.medialine.app
```

Optional container smoke test:

```powershell
docker build -t kpi-mining-local .
docker run --rm -d --name kpi-mining-local -p 8088:80 kpi-mining-local
curl.exe -fsS http://localhost:8088/api/health
curl.exe -fsS http://localhost:8088/openapi.json
docker stop kpi-mining-local
```

## Dev Compose

The `kpi-mining` service in `../docker-compose.dev-stack.yml` should build this
directory and mount it read-only so all routes are available in the container.

## DGX Route Recovery Notes

Cloudflare Tunnel should route `kpi.ben-e-fit.ai` and `kpi.medialine.app` to
`http://kpi-mining:80`. If `kpi.ben-e-fit.ai` redirects to the root hub while
`kpi.medialine.app` serves KPI content, the Cloudflare route is not the primary
fault; the running `kpi-mining` container likely still contains the old redirect
or incomplete mounted files. Redeploy the dev override through the approved
SelfCLAW flow, then run the route smoke test for both domains.
