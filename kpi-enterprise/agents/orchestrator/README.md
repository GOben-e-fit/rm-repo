# agents-orchestrator

FastAPI service that implements the KPI Enterprise Mining v1 API
(`kpi-enterprise/api/openapi.v1.yaml`). v1 status: **demo skeleton with
in-memory store** — production wiring (Postgres RLS, ClickHouse,
Trino, Neo4j, Qdrant, OpenSearch, LiteLLM, Langfuse) lands in CP-104
onward (`../../runbooks/CP-099-kpi-mining-governance-package.md`).

## Quick start

```bash
cd kpi-enterprise/agents/orchestrator
python -m venv .venv && source .venv/Scripts/activate     # PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[test]"
pytest -v
uvicorn app.main:app --reload --port 8000
# open http://127.0.0.1:8000/docs
```

Or via Docker:

```bash
docker compose -f kpi-enterprise/infra/compose/docker-compose.dev.yml up -d agents-orchestrator
curl -H 'X-Tenant-Id: tnt_demo' http://localhost:8000/v1/metric-definitions
```

## Auth modes

- `KPI_AUTH_MODE=demo` (default) — tenant comes from `X-Tenant-Id` header,
  defaults to `tnt_demo`. **Only for local development.**
- `KPI_AUTH_MODE=jwt` — Keycloak Bearer token verification (CP-104+).

## Tenant-isolation contract

Every endpoint that touches tenant data depends on `CurrentTenant`,
which extracts and validates the tenant pattern `^tnt_[a-z0-9]{4,32}$`.
The in-memory `TenantStore` is bucketed per tenant_id; cross-tenant
reads return empty. Negative deny-tests live in
`tests/test_tenant_deny.py` and are release-blocking
(`../../tenants/TENANT-ISOLATION-CONTRACT.md §6`).

## Tests

```
pytest -v                                                    # all (smoke + tenant-deny)
pytest tests/test_tenant_deny.py                             # release-blocker subset
```

CI: `.github/workflows/orchestrator-tests.yml` runs pytest + asserts
that the FastAPI-generated OpenAPI covers the canonical surface from
the spec file.

## File layout

```
agents/orchestrator/
├── app/
│   ├── main.py        # FastAPI app + all routes (single-file by design at v1)
│   ├── models.py      # Pydantic schemas mirroring api/openapi.v1.yaml
│   ├── store.py       # In-memory tenant-scoped store + demo seed
│   ├── auth.py        # X-Tenant-Id (demo) / JWT (prod, stub)
│   ├── config.py      # Pydantic-Settings (env prefix KPI_)
│   └── __init__.py
├── tests/
│   ├── conftest.py    # Resets store between tests, seeds demo tenants
│   ├── test_smoke.py  # Coverage of every public route
│   └── test_tenant_deny.py
├── pyproject.toml
├── Dockerfile
└── README.md
```

When a domain grows real implementation logic (e.g. Trino tool calls),
split it out into `app/routers/<domain>.py` and `app/agents/<name>.py`.
