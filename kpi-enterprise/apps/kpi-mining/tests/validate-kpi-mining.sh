#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

required_files=(
  "Dockerfile"
  "nginx.conf"
  "index.html"
  "enterprise/index.html"
  "console.html"
  "tools.html"
  "openapi.json"
  "README.md"
  "data-contracts/kpi-metric-contracts.yaml"
)

for relative_path in "${required_files[@]}"; do
  if [[ ! -f "$ROOT/$relative_path" ]]; then
    echo "Missing required file: $relative_path" >&2
    exit 1
  fi
done

python3 - "$ROOT" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
json_files = sorted((root / "api").rglob("*.json")) + [root / "openapi.json"]
for path in json_files:
    with path.open("r", encoding="utf-8") as handle:
        json.load(handle)

openapi = json.loads((root / "openapi.json").read_text(encoding="utf-8"))
required_paths = [
    "/api/health",
    "/api/v1/tenants",
    "/api/v1/sources",
    "/api/v1/datasets",
    "/api/v1/metric-definitions",
    "/api/v1/kpi-observations",
    "/api/v1/kpi-candidates",
    "/api/v1/driver-trees",
    "/api/v1/okr-links",
    "/api/v1/insights",
    "/api/v1/briefings",
    "/api/v1/agent-runs",
    "/api/v1/evidence",
    "/api/v1/benchmarks",
    "/api/v1/webhooks",
]
missing = [path for path in required_paths if path not in openapi.get("paths", {})]
if missing:
    raise SystemExit(f"OpenAPI missing paths: {missing}")
print(f"KPI mining validation passed: {len(json_files)} JSON files checked, {len(required_paths)} OpenAPI paths verified.")
PY

grep -q "location /enterprise" "$ROOT/nginx.conf"
grep -q "location @agent_api" "$ROOT/nginx.conf"
grep -q "agents-orchestrator" "$ROOT/nginx.conf"
grep -q "try_files \$uri \$uri.json @agent_api" "$ROOT/nginx.conf"
grep -q "require_tenant_id: true" "$ROOT/data-contracts/kpi-metric-contracts.yaml"
