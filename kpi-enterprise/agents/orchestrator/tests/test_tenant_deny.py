"""Negative tenant-isolation tests — release-blocking per TENANT-ISOLATION-CONTRACT §6."""
from __future__ import annotations

from fastapi.testclient import TestClient

A = {"X-Tenant-Id": "tnt_testa"}
B = {"X-Tenant-Id": "tnt_testb"}


def _make_metric(client: TestClient, headers: dict[str, str], name: str) -> str:
    r = client.post(
        "/v1/metric-definitions",
        json={
            "name": name,
            "display_name": name,
            "owner": f"owner@{headers['X-Tenant-Id']}.example",
            "domain": "test",
            "unit": "count",
            "granularity": "day",
            "direction": "neutral",
            "expression": "SELECT 1",
        },
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_invalid_tenant_format_rejected(client: TestClient) -> None:
    r = client.get("/v1/metric-definitions", headers={"X-Tenant-Id": "not-a-tenant!"})
    assert r.status_code == 400


def test_metric_not_visible_across_tenants(client: TestClient) -> None:
    metric_a = _make_metric(client, A, "exclusive_to_a")
    metric_b = _make_metric(client, B, "exclusive_to_b")

    list_a = client.get("/v1/metric-definitions", headers=A).json()
    list_b = client.get("/v1/metric-definitions", headers=B).json()

    ids_a = {m["id"] for m in list_a}
    ids_b = {m["id"] for m in list_b}

    assert metric_a in ids_a
    assert metric_a not in ids_b, "Tenant A's metric leaked into Tenant B"
    assert metric_b in ids_b
    assert metric_b not in ids_a, "Tenant B's metric leaked into Tenant A"


def test_source_not_visible_across_tenants(client: TestClient) -> None:
    payload = {"type": "upload", "name": "csv-a"}
    r = client.post("/v1/sources", json=payload, headers=A)
    assert r.status_code == 201
    src_a = r.json()["id"]

    sources_b = client.get("/v1/sources", headers=B).json()
    assert all(s["id"] != src_a for s in sources_b), "Tenant A's source leaked into Tenant B"


def test_driver_tree_not_visible_across_tenants(client: TestClient) -> None:
    r = client.post("/v1/driver-trees", json={"name": "Tree A", "owner": "o@a"}, headers=A)
    tree_a = r.json()["id"]

    trees_b = client.get("/v1/driver-trees", headers=B).json()
    assert all(t["id"] != tree_a for t in trees_b)


def test_briefing_not_visible_across_tenants(client: TestClient) -> None:
    r = client.post(
        "/v1/briefings",
        json={"type": "ad_hoc", "audience": "cfo"},
        headers=A,
    )
    assert r.status_code == 202

    briefings_b = client.get("/v1/briefings", headers=B).json()
    a_count = len(client.get("/v1/briefings", headers=A).json())
    b_count = len(briefings_b)
    assert b_count < a_count or b_count == 0, "Tenant B sees briefings from A"


def test_agent_run_not_visible_across_tenants(client: TestClient) -> None:
    # Trigger discovery in A
    r = client.post(
        "/v1/kpi-candidates",
        json={"dataset_ids": ["ds_demo"]},
        headers=A,
    )
    run_id = r.json()["run_id"]

    r = client.get(f"/v1/agent-runs/{run_id}", headers=A)
    assert r.status_code == 200

    r = client.get(f"/v1/agent-runs/{run_id}", headers=B)
    assert r.status_code == 404, "Tenant B can read A's agent run"
