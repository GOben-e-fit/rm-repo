"""End-to-end test: POST /v1/kpi-candidates triggers heuristic discovery
and persists candidates into the tenant store, isolated per tenant."""
from __future__ import annotations

from fastapi.testclient import TestClient

H = {"X-Tenant-Id": "tnt_demo"}


def test_discovery_creates_candidates(client: TestClient) -> None:
    # initially empty for the requested dataset surface
    initial = client.get("/v1/kpi-candidates", headers=H).json()
    initial_count = len(initial)

    payload = {
        "dataset_ids": [
            "ds_finance_subscriptions",
            "ds_finance_invoices",
            "ds_sales_pipeline",
            "ds_ops_orders",
            "ds_support_surveys",
        ],
        "scope_hint": "demo-fixtures",
    }
    r = client.post("/v1/kpi-candidates", json=payload, headers=H)
    assert r.status_code == 202, r.text
    body = r.json()
    assert body["status"] == "succeeded"

    # candidates should now be visible
    after = client.get("/v1/kpi-candidates", headers=H).json()
    assert len(after) > initial_count
    template_ids = {c.get("template_id") for c in after if "template_id" in c}
    assert "finance.mrr" in template_ids
    assert "support.nps" in template_ids


def test_discovery_isolated_per_tenant(client: TestClient) -> None:
    A = {"X-Tenant-Id": "tnt_benefit"}
    B = {"X-Tenant-Id": "tnt_kiguru"}

    payload = {"dataset_ids": ["ds_finance_subscriptions"]}
    client.post("/v1/kpi-candidates", json=payload, headers=A)

    cands_a = client.get("/v1/kpi-candidates", headers=A).json()
    cands_b = client.get("/v1/kpi-candidates", headers=B).json()
    assert any(c.get("template_id") == "finance.mrr" for c in cands_a)
    assert all(c.get("template_id") != "finance.mrr" for c in cands_b), (
        "MRR candidate from Tenant A leaked into Tenant B"
    )


def test_unknown_dataset_skipped_gracefully(client: TestClient) -> None:
    payload = {"dataset_ids": ["ds_does_not_exist"]}
    r = client.post("/v1/kpi-candidates", json=payload, headers=H)
    assert r.status_code == 202
    # the agent_run should record the skip
    runs = client.get("/v1/agent-runs", headers=H, params={"agent": "kpi-discovery"}).json()
    assert any(
        r.get("outputs", {}).get("datasets_skipped") for r in runs
    ), "expected skipped_datasets to be reported in agent_run outputs"
