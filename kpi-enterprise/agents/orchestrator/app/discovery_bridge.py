"""Bridge between the orchestrator HTTP layer and the kpi-discovery package.

The orchestrator uses an in-memory dataset profile fixture for v1; in
production this fetches profiles from OpenMetadata + Trino sample queries.
The bridge keeps the HTTP layer unaware of the discovery package internals.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Discovery package lives next to the orchestrator inside agents/.
# parents: [app, orchestrator, agents, kpi-enterprise-mining]
_DISCOVERY_PKG = Path(__file__).resolve().parents[2] / "kpi-discovery"
if str(_DISCOVERY_PKG) not in sys.path:
    sys.path.insert(0, str(_DISCOVERY_PKG))

from kpi_discovery import ColumnProfile, DatasetProfile, discover  # noqa: E402

from .store import _new_id, _now, tenant_store


def _demo_dataset_profiles(dataset_ids: list[str]) -> list[DatasetProfile]:
    """Return synthetic profiles for the requested dataset IDs.

    v1 is deterministic and offline. v2 will replace this with a real
    pull from OpenMetadata/Trino. The synthetic profiles are intentionally
    rich enough that the heuristic engine produces ≥ 4 candidate KPIs.
    """
    fixtures: dict[str, DatasetProfile] = {
        "ds_finance_subscriptions": DatasetProfile(
            id="ds_finance_subscriptions",
            name="finance_subscriptions",
            domain_hint="finance",
            columns=[
                ColumnProfile(name="subscription_id", type="uuid", distinct_count=2400),
                ColumnProfile(name="mrr_eur", type="decimal", distinct_count=1800),
                ColumnProfile(name="active", type="bool", distinct_count=2),
            ],
        ),
        "ds_finance_invoices": DatasetProfile(
            id="ds_finance_invoices",
            name="finance_invoices",
            domain_hint="finance",
            columns=[
                ColumnProfile(name="invoice_id", type="uuid", distinct_count=15000),
                ColumnProfile(name="total_amount", type="decimal", distinct_count=12000),
                ColumnProfile(name="cost_amount", type="decimal", distinct_count=11000),
                ColumnProfile(name="created_at", type="timestamp", distinct_count=15000),
            ],
        ),
        "ds_sales_pipeline": DatasetProfile(
            id="ds_sales_pipeline",
            name="sales_pipeline",
            domain_hint="sales",
            columns=[
                ColumnProfile(name="opportunity_id", type="uuid", distinct_count=4200),
                ColumnProfile(name="stage", type="string", distinct_count=6),
                ColumnProfile(name="created_at", type="timestamp", distinct_count=4200),
                ColumnProfile(name="closed_at", type="timestamp", null_ratio=0.4, distinct_count=2800),
            ],
        ),
        "ds_ops_orders": DatasetProfile(
            id="ds_ops_orders",
            name="ops_orders",
            domain_hint="ops",
            columns=[
                ColumnProfile(name="order_id", type="uuid", distinct_count=88000),
                ColumnProfile(name="open_amount", type="decimal", distinct_count=15000),
            ],
        ),
        "ds_support_surveys": DatasetProfile(
            id="ds_support_surveys",
            name="support_nps_surveys",
            domain_hint="support",
            columns=[
                ColumnProfile(name="ticket_id", type="uuid", distinct_count=12000),
                ColumnProfile(name="nps_score", type="int", distinct_count=11),
            ],
        ),
    }
    profiles: list[DatasetProfile] = []
    for did in dataset_ids:
        profiles.append(fixtures.get(did) or DatasetProfile(id=did, name=did, columns=[]))
    return profiles


def run_discovery(tenant_id: str, dataset_ids: list[str], scope_hint: str | None = None) -> dict[str, Any]:
    """Profile the requested datasets and persist KpiCandidates into the tenant store.

    Returns the synthetic agent_run record (also persisted) so the HTTP
    layer can hand back an AgentRunRef.
    """
    profiles = _demo_dataset_profiles(dataset_ids)
    result = discover(profiles)

    persisted: list[dict[str, Any]] = []
    for cand in result.candidates:
        item = cand.model_dump()
        item["status"] = "new"
        item["tenant_id"] = tenant_id
        if scope_hint:
            item.setdefault("scope_hint", scope_hint)
        tenant_store.put(tenant_id, "kpi_candidates", item)
        persisted.append(item)

    run_id = _new_id("run")
    run_item = {
        "id": run_id,
        "run_id": run_id,
        "tenant_id": tenant_id,
        "agent": "kpi-discovery",
        "status": "succeeded",
        "started_at": _now().isoformat(),
        "ended_at": _now().isoformat(),
        "tools_used": ["dataset.profile.fixture", "kpi_discovery.discover"],
        "llm_calls": [],
        "evidence_bundle": None,
        "approval": {"required": False, "approvers": [], "granted": False},
        "rollback_snapshot": None,
        "trace_url": f"https://trace.medialine.app/runs/{run_id}",
        "outputs": {
            "candidates_persisted": len(persisted),
            "datasets_profiled": result.profiled_datasets,
            "datasets_skipped": result.skipped_datasets,
        },
    }
    tenant_store.put(tenant_id, "agent_runs", run_item)
    return run_item
