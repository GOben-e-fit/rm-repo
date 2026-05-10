"""FastAPI app implementing the KPI Enterprise Mining v1 API contract.

This is a single-file router on purpose: it stays close to the OpenAPI doc
and easy to read. When endpoints grow real implementations they move into
`app/routers/<domain>.py`.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from time import monotonic
from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import __version__
from .auth import CurrentTenant
from .config import settings
from .models import (
    AgentRun,
    AgentRunRef,
    AgentRunStatus,
    Benchmark,
    Briefing,
    BriefingCreate,
    BriefingStatus,
    Dataset,
    DatasetProfile,
    DiscoveryRunRequest,
    DriverEdge,
    DriverNode,
    DriverTree,
    DriverTreeCreate,
    EvidenceBundle,
    Health,
    Insight,
    KpiCandidate,
    KpiObservation,
    MetricDefinition,
    MetricDefinitionCreate,
    OkrLink,
    PromoteRequest,
    Source,
    SourceCreate,
    Tenant,
    TenantCreate,
    TenantUpdate,
    Webhook,
)
from .store import _new_id, _now, global_store, seed_demo, tenant_store

START_TS = monotonic()


def create_app() -> FastAPI:
    app = FastAPI(
        title="KPI Enterprise Mining API",
        version=__version__,
        description=(
            "v1 API per `kpi-enterprise/api/openapi.v1.yaml`. "
            "Demo auth mode: pass `X-Tenant-Id: tnt_<slug>` header. "
            "Production auth: Keycloak JWT (Bearer) with `tenant_id` claim."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Tenant-Id", "X-Request-Id"],
    )

    seed_demo()

    # ---------- System ----------

    @app.get("/health", response_model=Health, tags=["system"])
    def health() -> Health:
        return Health(status="ok", version=__version__, uptime_seconds=int(monotonic() - START_TS))

    @app.get("/ready", tags=["system"])
    def ready() -> dict[str, str]:
        return {"status": "ready"}

    # ---------- Tenants ----------

    @app.get("/v1/tenants", response_model=list[Tenant], tags=["tenants"])
    def list_tenants() -> list[dict[str, Any]]:
        return global_store.list_tenants()

    @app.post(
        "/v1/tenants",
        response_model=Tenant,
        status_code=status.HTTP_201_CREATED,
        tags=["tenants"],
    )
    def create_tenant(payload: TenantCreate) -> dict[str, Any]:
        tenant_id = f"tnt_{payload.slug.lower().replace('-', '')[:20]}"
        if global_store.get_tenant(tenant_id):
            raise HTTPException(status.HTTP_409_CONFLICT, "tenant already exists")
        tenant = {
            "id": tenant_id,
            "slug": payload.slug,
            "display_name": payload.display_name,
            "brand": payload.brand.value,
            "keycloak_realm": payload.slug,
            "data_classification_default": "internal",
            "external_llm_allowed": payload.external_llm_allowed,
            "created_at": _now().isoformat(),
        }
        return global_store.put_tenant(tenant)

    @app.get("/v1/tenants/{tenant_id}", response_model=Tenant, tags=["tenants"])
    def get_tenant(tenant_id: str) -> dict[str, Any]:
        t = global_store.get_tenant(tenant_id)
        if not t:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "tenant not found")
        return t

    @app.patch("/v1/tenants/{tenant_id}", response_model=Tenant, tags=["tenants"])
    def update_tenant(tenant_id: str, payload: TenantUpdate) -> dict[str, Any]:
        t = global_store.get_tenant(tenant_id)
        if not t:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "tenant not found")
        update = payload.model_dump(exclude_unset=True)
        if "brand" in update and update["brand"] is not None:
            update["brand"] = update["brand"].value if hasattr(update["brand"], "value") else update["brand"]
        t.update(update)
        return global_store.put_tenant(t)

    @app.delete("/v1/tenants/{tenant_id}", status_code=status.HTTP_202_ACCEPTED, tags=["tenants"])
    def delete_tenant(tenant_id: str) -> dict[str, str]:
        if not global_store.delete_tenant(tenant_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "tenant not found")
        return {"status": "deletion enqueued"}

    # ---------- Sources ----------

    @app.get("/v1/sources", response_model=list[Source], tags=["sources"])
    def list_sources(tenant: CurrentTenant) -> list[dict[str, Any]]:
        return tenant_store.list(tenant, "sources")

    @app.post(
        "/v1/sources",
        response_model=Source,
        status_code=status.HTTP_201_CREATED,
        tags=["sources"],
    )
    def create_source(payload: SourceCreate, tenant: CurrentTenant) -> dict[str, Any]:
        item = {
            "id": _new_id("src"),
            **payload.model_dump(),
            "last_sync": None,
            "status": "unknown",
        }
        return tenant_store.put(tenant, "sources", item)

    @app.post(
        "/v1/sources/{source_id}/sync",
        response_model=AgentRunRef,
        status_code=status.HTTP_202_ACCEPTED,
        tags=["sources"],
    )
    def sync_source(source_id: str, tenant: CurrentTenant) -> AgentRunRef:
        if not tenant_store.get(tenant, "sources", source_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "source not found")
        run = _stub_agent_run(tenant, agent="source-sync")
        return AgentRunRef(run_id=run["run_id"], status=AgentRunStatus.QUEUED, trace_url=run.get("trace_url"))

    # ---------- Datasets ----------

    @app.get("/v1/datasets", response_model=list[Dataset], tags=["datasets"])
    def list_datasets(tenant: CurrentTenant) -> list[dict[str, Any]]:
        return tenant_store.list(tenant, "datasets")

    @app.get("/v1/datasets/{dataset_id}/profile", response_model=DatasetProfile, tags=["datasets"])
    def dataset_profile(dataset_id: str, tenant: CurrentTenant) -> DatasetProfile:
        # Demo: synthesize a small profile so consumers can develop against it.
        return DatasetProfile(
            dataset_id=dataset_id,
            columns=[
                {"name": "id", "type": "uuid", "null_ratio": 0.0, "distinct_count": 1234, "sample_values": ["a", "b"]},
                {"name": "amount", "type": "decimal", "null_ratio": 0.01, "distinct_count": 988, "sample_values": ["12.50"]},
                {"name": "email", "type": "string", "null_ratio": 0.0, "distinct_count": 1234, "sample_values": ["x@y"], "detected_pii": True},
            ],
        )

    # ---------- Metric Definitions ----------

    @app.get("/v1/metric-definitions", response_model=list[MetricDefinition], tags=["metrics"])
    def list_metric_definitions(tenant: CurrentTenant) -> list[dict[str, Any]]:
        return tenant_store.list(tenant, "metric_definitions")

    @app.post(
        "/v1/metric-definitions",
        response_model=MetricDefinition,
        status_code=status.HTTP_201_CREATED,
        tags=["metrics"],
    )
    def create_metric_definition(payload: MetricDefinitionCreate, tenant: CurrentTenant) -> dict[str, Any]:
        item = {
            "id": _new_id("metric"),
            "version": 1,
            "tenant_id": tenant,
            **payload.model_dump(mode="json"),
            "created_at": _now().isoformat(),
            "git_ref": None,
        }
        return tenant_store.put(tenant, "metric_definitions", item)

    @app.get(
        "/v1/metric-definitions/{metric_id}/versions",
        response_model=list[MetricDefinition],
        tags=["metrics"],
    )
    def metric_versions(metric_id: str, tenant: CurrentTenant) -> list[dict[str, Any]]:
        item = tenant_store.get(tenant, "metric_definitions", metric_id)
        return [item] if item else []

    # ---------- KPI Candidates ----------

    @app.get("/v1/kpi-candidates", response_model=list[KpiCandidate], tags=["metrics"])
    def list_kpi_candidates(tenant: CurrentTenant) -> list[dict[str, Any]]:
        return tenant_store.list(tenant, "kpi_candidates")

    @app.post(
        "/v1/kpi-candidates",
        response_model=AgentRunRef,
        status_code=status.HTTP_202_ACCEPTED,
        tags=["metrics"],
    )
    def trigger_discovery(payload: DiscoveryRunRequest, tenant: CurrentTenant) -> AgentRunRef:
        run = _stub_agent_run(tenant, agent="kpi-discovery")
        return AgentRunRef(run_id=run["run_id"], status=AgentRunStatus.QUEUED, trace_url=run.get("trace_url"))

    @app.post(
        "/v1/kpi-candidates/{candidate_id}/promote",
        response_model=MetricDefinition,
        status_code=status.HTTP_201_CREATED,
        tags=["metrics"],
    )
    def promote_candidate(candidate_id: str, payload: PromoteRequest, tenant: CurrentTenant) -> dict[str, Any]:
        cand = tenant_store.get(tenant, "kpi_candidates", candidate_id)
        if not cand:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "candidate not found")
        item = {
            "id": _new_id("metric"),
            "version": 1,
            "tenant_id": tenant,
            "name": payload.target_metric_name or cand["proposed_name"],
            "display_name": cand["proposed_name"].replace("_", " ").title(),
            "owner": payload.approver,
            "domain": "tbd",
            "unit": cand.get("suggested_unit") or "count",
            "granularity": cand.get("suggested_granularity") or "day",
            "direction": "neutral",
            "expression": cand.get("proposed_sql") or "SELECT 1",
            "data_classification": "internal",
            "compliance_tags": [],
            "created_at": _now().isoformat(),
            "git_ref": None,
        }
        cand["status"] = "accepted"
        return tenant_store.put(tenant, "metric_definitions", item)

    # ---------- KPI Observations ----------

    @app.get("/v1/kpi-observations", response_model=list[KpiObservation], tags=["kpis"])
    def list_observations(
        tenant: CurrentTenant,
        metric_id: str = Query(..., description="Required filter"),
        from_: datetime | None = Query(None, alias="from"),
        to: datetime | None = None,
    ) -> list[dict[str, Any]]:
        # Demo: return a synthetic 7-day series so charts can render.
        now = _now()
        series: list[dict[str, Any]] = []
        for offset in range(7):
            ts = now - timedelta(days=6 - offset)
            if from_ and ts < from_:
                continue
            if to and ts > to:
                continue
            series.append(
                {
                    "metric_id": metric_id,
                    "metric_version": 1,
                    "ts": ts.isoformat(),
                    "value": 1_000_000 + offset * 12_345,
                    "confidence": 0.92,
                }
            )
        return series

    # ---------- Driver Trees ----------

    @app.get("/v1/driver-trees", response_model=list[DriverTree], tags=["trees"])
    def list_driver_trees(tenant: CurrentTenant) -> list[dict[str, Any]]:
        return tenant_store.list(tenant, "driver_trees")

    @app.post(
        "/v1/driver-trees",
        response_model=DriverTree,
        status_code=status.HTTP_201_CREATED,
        tags=["trees"],
    )
    def create_driver_tree(payload: DriverTreeCreate, tenant: CurrentTenant) -> dict[str, Any]:
        item = {
            "id": _new_id("tree"),
            "name": payload.name,
            "owner": payload.owner,
            "node_count": 0,
            "edge_count": 0,
            "updated_at": _now().isoformat(),
        }
        return tenant_store.put(tenant, "driver_trees", item)

    @app.get(
        "/v1/driver-trees/{tree_id}/nodes",
        response_model=list[DriverNode],
        tags=["trees"],
    )
    def list_tree_nodes(tree_id: str, tenant: CurrentTenant) -> list[dict[str, Any]]:
        return tenant_store.list(tenant, f"tree:{tree_id}:nodes")

    @app.post(
        "/v1/driver-trees/{tree_id}/nodes",
        response_model=DriverNode,
        status_code=status.HTTP_201_CREATED,
        tags=["trees"],
    )
    def add_tree_node(tree_id: str, payload: DriverNode, tenant: CurrentTenant) -> dict[str, Any]:
        item = payload.model_dump(mode="json")
        item.setdefault("id", _new_id("node"))
        return tenant_store.put(tenant, f"tree:{tree_id}:nodes", item)

    @app.get(
        "/v1/driver-trees/{tree_id}/edges",
        response_model=list[DriverEdge],
        tags=["trees"],
    )
    def list_tree_edges(tree_id: str, tenant: CurrentTenant) -> list[dict[str, Any]]:
        return tenant_store.list(tenant, f"tree:{tree_id}:edges")

    @app.post(
        "/v1/driver-trees/{tree_id}/edges",
        response_model=DriverEdge,
        status_code=status.HTTP_201_CREATED,
        tags=["trees"],
    )
    def add_tree_edge(tree_id: str, payload: DriverEdge, tenant: CurrentTenant) -> dict[str, Any]:
        item = payload.model_dump(mode="json")
        item.setdefault("id", _new_id("edge"))
        return tenant_store.put(tenant, f"tree:{tree_id}:edges", item)

    # ---------- OKR Links ----------

    @app.get("/v1/okr-links", response_model=list[OkrLink], tags=["okrs"])
    def list_okr_links(tenant: CurrentTenant) -> list[dict[str, Any]]:
        return tenant_store.list(tenant, "okr_links")

    @app.post(
        "/v1/okr-links",
        response_model=OkrLink,
        status_code=status.HTTP_201_CREATED,
        tags=["okrs"],
    )
    def create_okr_link(payload: OkrLink, tenant: CurrentTenant) -> dict[str, Any]:
        item = payload.model_dump()
        item.setdefault("id", _new_id("okr"))
        return tenant_store.put(tenant, "okr_links", item)

    # ---------- Insights ----------

    @app.get("/v1/insights", response_model=list[Insight], tags=["insights"])
    def list_insights(
        tenant: CurrentTenant,
        severity: str | None = Query(None),
    ) -> list[dict[str, Any]]:
        items = tenant_store.list(tenant, "insights")
        if severity:
            items = [i for i in items if i.get("severity") == severity]
        return items

    # ---------- Briefings ----------

    @app.get("/v1/briefings", response_model=list[Briefing], tags=["briefings"])
    def list_briefings(tenant: CurrentTenant) -> list[dict[str, Any]]:
        return tenant_store.list(tenant, "briefings")

    @app.post(
        "/v1/briefings",
        response_model=AgentRunRef,
        status_code=status.HTTP_202_ACCEPTED,
        tags=["briefings"],
    )
    def create_briefing(payload: BriefingCreate, tenant: CurrentTenant) -> AgentRunRef:
        briefing_id = _new_id("brief")
        tenant_store.put(
            tenant,
            "briefings",
            {
                "id": briefing_id,
                "type": payload.type.value,
                "audience": payload.audience,
                "status": BriefingStatus.QUEUED.value,
                "delivered_to": [],
                "created_at": _now().isoformat(),
            },
        )
        run = _stub_agent_run(tenant, agent="briefing-generator", linked_briefing=briefing_id)
        return AgentRunRef(run_id=run["run_id"], status=AgentRunStatus.QUEUED, trace_url=run.get("trace_url"))

    @app.get("/v1/briefings/{briefing_id}", response_model=Briefing, tags=["briefings"])
    def get_briefing(briefing_id: str, tenant: CurrentTenant) -> dict[str, Any]:
        b = tenant_store.get(tenant, "briefings", briefing_id)
        if not b:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "briefing not found")
        return b

    # ---------- Agent Runs ----------

    @app.get("/v1/agent-runs", response_model=list[AgentRun], tags=["agents"])
    def list_agent_runs(
        tenant: CurrentTenant,
        agent: str | None = None,
        run_status: str | None = Query(None, alias="status"),
    ) -> list[dict[str, Any]]:
        runs = tenant_store.list(tenant, "agent_runs")
        if agent:
            runs = [r for r in runs if r.get("agent") == agent]
        if run_status:
            runs = [r for r in runs if r.get("status") == run_status]
        return runs

    @app.get("/v1/agent-runs/{run_id}", response_model=AgentRun, tags=["agents"])
    def get_agent_run(run_id: str, tenant: CurrentTenant) -> dict[str, Any]:
        r = tenant_store.get(tenant, "agent_runs", run_id)
        if not r:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "agent run not found")
        return r

    @app.get("/v1/evidence/{evidence_id}", response_model=EvidenceBundle, tags=["agents"])
    def get_evidence(evidence_id: str, tenant: CurrentTenant) -> EvidenceBundle:
        return EvidenceBundle(
            id=evidence_id,
            run_id=evidence_id.replace("ev_", "run_"),
            signed_url=f"https://lake.medialine.app/{tenant}/evidence/{evidence_id}?sig=demo",
            expires_at=_now() + timedelta(hours=24),
            sha256=None,
        )

    # ---------- Benchmarks ----------

    @app.get("/v1/benchmarks", response_model=list[Benchmark], tags=["benchmarks"])
    def list_benchmarks(tenant: CurrentTenant) -> list[dict[str, Any]]:
        return tenant_store.list(tenant, "benchmarks")

    # ---------- Webhooks ----------

    @app.get("/v1/webhooks", response_model=list[Webhook], tags=["webhooks"])
    def list_webhooks(tenant: CurrentTenant) -> list[dict[str, Any]]:
        return tenant_store.list(tenant, "webhooks")

    @app.post(
        "/v1/webhooks",
        response_model=Webhook,
        status_code=status.HTTP_201_CREATED,
        tags=["webhooks"],
    )
    def create_webhook(payload: Webhook, tenant: CurrentTenant) -> dict[str, Any]:
        item = payload.model_dump()
        item.setdefault("id", _new_id("hook"))
        return tenant_store.put(tenant, "webhooks", item)

    # ---------- Helpers ----------

    def _stub_agent_run(tenant: str, agent: str, linked_briefing: str | None = None) -> dict[str, Any]:
        run_id = _new_id("run")
        item = {
            "id": run_id,
            "run_id": run_id,
            "tenant_id": tenant,
            "agent": agent,
            "status": AgentRunStatus.QUEUED.value,
            "started_at": _now().isoformat(),
            "ended_at": None,
            "tools_used": [],
            "llm_calls": [],
            "evidence_bundle": None,
            "approval": {"required": False, "approvers": [], "granted": False},
            "rollback_snapshot": None,
            "linked_briefing": linked_briefing,
            "trace_url": f"https://trace.medialine.app/runs/{run_id}",
        }
        tenant_store.put(tenant, "agent_runs", item)
        return item

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_, exc: HTTPException) -> JSONResponse:  # type: ignore[override]
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.__class__.__name__, "detail": exc.detail},
        )

    return app


app = create_app()
