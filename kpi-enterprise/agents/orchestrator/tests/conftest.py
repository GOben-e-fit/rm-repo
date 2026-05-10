import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("KPI_AUTH_MODE", "demo")


@pytest.fixture()
def client() -> TestClient:
    from app.main import app, create_app  # noqa: F401  (import to register lifespan)
    from app.store import global_store, tenant_store, seed_demo

    # reset store between tests
    global_store._tenants.clear()
    tenant_store._data.clear()
    seed_demo()
    return TestClient(app)
