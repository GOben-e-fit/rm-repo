"""In-memory tenant-scoped demo store.

Production replaces this with Postgres + ClickHouse + Neo4j + MinIO. The
contract here is that every accessor takes a tenant_id and must never leak
across tenants. Cross-tenant leakage in the store is a release-blocker.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class TenantStore:
    """Per-tenant collections. tenant_id -> resource type -> id -> object."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, dict[str, Any]]] = defaultdict(
            lambda: defaultdict(dict)
        )

    def list(self, tenant_id: str, kind: str) -> list[dict[str, Any]]:
        return list(self._data[tenant_id][kind].values())

    def get(self, tenant_id: str, kind: str, item_id: str) -> dict[str, Any] | None:
        return self._data[tenant_id][kind].get(item_id)

    def put(self, tenant_id: str, kind: str, item: dict[str, Any]) -> dict[str, Any]:
        item_id = item["id"]
        self._data[tenant_id][kind][item_id] = item
        return item

    def delete(self, tenant_id: str, kind: str, item_id: str) -> bool:
        return self._data[tenant_id][kind].pop(item_id, None) is not None


class GlobalStore:
    """Platform-level entries (tenants registry, agent runs index)."""

    def __init__(self) -> None:
        self._tenants: dict[str, dict[str, Any]] = {}

    def list_tenants(self) -> list[dict[str, Any]]:
        return list(self._tenants.values())

    def get_tenant(self, tenant_id: str) -> dict[str, Any] | None:
        return self._tenants.get(tenant_id)

    def put_tenant(self, tenant: dict[str, Any]) -> dict[str, Any]:
        self._tenants[tenant["id"]] = tenant
        return tenant

    def delete_tenant(self, tenant_id: str) -> bool:
        return self._tenants.pop(tenant_id, None) is not None


tenant_store = TenantStore()
global_store = GlobalStore()


def seed_demo() -> None:
    """Seed three canonical demo tenants and a small set of metrics/insights."""
    canonical = [
        ("tnt_benefit", "ben-e-fit", "ben-e-fit", "ben-e-fit"),
        ("tnt_medialine", "medialine", "medialine", "medialine"),
        ("tnt_kiguru", "ki-guru", "ki-guru", "ki-guru"),
        ("tnt_demo", "demo", "medialine", "demo"),
    ]
    for tenant_id, slug, brand, realm in canonical:
        if global_store.get_tenant(tenant_id):
            continue
        global_store.put_tenant(
            {
                "id": tenant_id,
                "slug": slug,
                "display_name": slug.title(),
                "brand": brand,
                "keycloak_realm": realm,
                "data_classification_default": "internal",
                "external_llm_allowed": tenant_id == "tnt_demo",
                "created_at": _now().isoformat(),
            }
        )

    # Demo metric per tenant
    for tenant_id, _, _, _ in canonical:
        metric_id = "metric_demo_mrr"
        if tenant_store.get(tenant_id, "metric_definitions", metric_id):
            continue
        tenant_store.put(
            tenant_id,
            "metric_definitions",
            {
                "id": metric_id,
                "version": 1,
                "tenant_id": tenant_id,
                "name": "monthly_recurring_revenue",
                "display_name": "Monthly Recurring Revenue",
                "owner": f"cfo@{tenant_id}.example",
                "domain": "finance",
                "unit": "EUR",
                "granularity": "month",
                "direction": "up_is_favorable",
                "expression": "SUM(mrr_eur)",
                "data_classification": "internal",
                "compliance_tags": ["GDPR.none"],
                "refresh_cron": "0 2 * * *",
                "anomaly": {"method": "stl_zscore", "threshold": 3.0},
                "created_at": _now().isoformat(),
                "git_ref": "contracts/metric-contracts/example/mrr.yaml@demo",
            },
        )
        tenant_store.put(
            tenant_id,
            "insights",
            {
                "id": f"ins_{tenant_id}_demo",
                "type": "anomaly",
                "metric_id": metric_id,
                "severity": "warn",
                "what_happened": f"MRR von {tenant_id} liegt 7% unter Forecast.",
                "why_hypothesis": "Erhöhter Churn in Tier-S-Segment der letzten 14 Tage.",
                "what_to_do": [
                    {
                        "action_template": "retention_call_top10_churn_risk",
                        "expected_impact": "+2pp Retention im Folgemonat",
                    }
                ],
                "owner": f"cfo@{tenant_id}.example",
                "evidence_id": f"ev_{tenant_id}_demo",
                "created_at": _now().isoformat(),
            },
        )


__all__ = [
    "GlobalStore",
    "TenantStore",
    "global_store",
    "tenant_store",
    "seed_demo",
    "_now",
    "_new_id",
]
