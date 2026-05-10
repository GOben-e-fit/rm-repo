"""Smoke tests covering every route from openapi.v1.yaml."""
from __future__ import annotations

from fastapi.testclient import TestClient

T = "tnt_demo"
H = {"X-Tenant-Id": T}


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_ready(client: TestClient) -> None:
    assert client.get("/ready").status_code == 200


def test_openapi_doc(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json()["paths"]
    # cover the canonical surface
    for p in [
        "/v1/tenants",
        "/v1/sources",
        "/v1/datasets",
        "/v1/metric-definitions",
        "/v1/kpi-candidates",
        "/v1/kpi-observations",
        "/v1/driver-trees",
        "/v1/insights",
        "/v1/briefings",
        "/v1/agent-runs",
        "/v1/benchmarks",
        "/v1/webhooks",
    ]:
        assert p in paths, f"missing route {p}"


def test_tenants_seeded(client: TestClient) -> None:
    r = client.get("/v1/tenants")
    assert r.status_code == 200
    ids = {t["id"] for t in r.json()}
    assert {"tnt_benefit", "tnt_medialine", "tnt_kiguru", "tnt_demo"} <= ids


def test_tenant_lifecycle(client: TestClient) -> None:
    payload = {
        "slug": "acmeco",
        "display_name": "Acme Co",
        "brand": "ben-e-fit",
        "admin_email": "owner@acme.example",
    }
    r = client.post("/v1/tenants", json=payload)
    assert r.status_code == 201, r.text
    tid = r.json()["id"]
    assert tid.startswith("tnt_")

    r = client.get(f"/v1/tenants/{tid}")
    assert r.status_code == 200
    assert r.json()["display_name"] == "Acme Co"

    r = client.patch(f"/v1/tenants/{tid}", json={"display_name": "Acme Holdings"})
    assert r.status_code == 200
    assert r.json()["display_name"] == "Acme Holdings"

    r = client.delete(f"/v1/tenants/{tid}")
    assert r.status_code == 202


def test_metric_definitions(client: TestClient) -> None:
    r = client.get("/v1/metric-definitions", headers=H)
    assert r.status_code == 200
    assert any(m["name"] == "monthly_recurring_revenue" for m in r.json())

    new_metric = {
        "name": "gross_margin",
        "display_name": "Gross Margin",
        "owner": "controller@demo.example",
        "domain": "finance",
        "unit": "percent",
        "granularity": "month",
        "direction": "up_is_favorable",
        "expression": "(SUM(revenue) - SUM(cogs)) / NULLIF(SUM(revenue),0)",
    }
    r = client.post("/v1/metric-definitions", json=new_metric, headers=H)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["tenant_id"] == T
    assert body["version"] == 1


def test_sources_crud(client: TestClient) -> None:
    payload = {"type": "airbyte", "name": "primary-erp", "config": {"connector_id": "datev"}}
    r = client.post("/v1/sources", json=payload, headers=H)
    assert r.status_code == 201
    src_id = r.json()["id"]

    r = client.get("/v1/sources", headers=H)
    assert any(s["id"] == src_id for s in r.json())

    r = client.post(f"/v1/sources/{src_id}/sync", headers=H)
    assert r.status_code == 202
    assert r.json()["status"] == "queued"


def test_kpi_observations_synthetic(client: TestClient) -> None:
    r = client.get("/v1/kpi-observations", params={"metric_id": "metric_demo_mrr"}, headers=H)
    assert r.status_code == 200
    obs = r.json()
    assert len(obs) == 7
    assert all(o["metric_id"] == "metric_demo_mrr" for o in obs)


def test_driver_tree_with_nodes(client: TestClient) -> None:
    r = client.post("/v1/driver-trees", json={"name": "Revenue Tree", "owner": "cfo@demo"}, headers=H)
    assert r.status_code == 201
    tid = r.json()["id"]

    node_payload = {"id": "node_revenue", "metric_id": "metric_demo_mrr", "label": "Revenue"}
    r = client.post(f"/v1/driver-trees/{tid}/nodes", json=node_payload, headers=H)
    assert r.status_code == 201

    r = client.get(f"/v1/driver-trees/{tid}/nodes", headers=H)
    assert any(n["id"] == "node_revenue" for n in r.json())

    edge_payload = {"id": "edge_1", "from_node": "node_revenue", "to_node": "node_revenue", "weight": 1.0}
    r = client.post(f"/v1/driver-trees/{tid}/edges", json=edge_payload, headers=H)
    assert r.status_code == 201


def test_briefing_async(client: TestClient) -> None:
    payload = {"type": "weekly", "audience": "cfo", "delivery": ["email"]}
    r = client.post("/v1/briefings", json=payload, headers=H)
    assert r.status_code == 202
    assert r.json()["status"] == "queued"

    r = client.get("/v1/briefings", headers=H)
    assert len(r.json()) >= 1


def test_insights_seeded(client: TestClient) -> None:
    r = client.get("/v1/insights", headers=H)
    assert r.status_code == 200
    items = r.json()
    assert items, "demo insight should be seeded"
    assert items[0]["severity"] in {"info", "warn", "critical"}
