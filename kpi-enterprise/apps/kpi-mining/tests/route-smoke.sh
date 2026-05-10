#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:8088}"
TENANT_ID="${2:-demo-ceo-office}"
BASE_URL="${BASE_URL%/}"

routes=(
  "/ html"
  "/enterprise/ html"
  "/console.html html"
  "/tools.html html"
  "/openapi.json json"
  "/api/health json"
  "/api/v1/metric-definitions json"
  "/api/v1/kpi-observations json"
  "/api/v1/driver-trees json"
  "/api/v1/agent-runs json"
)

failures=0
for entry in "${routes[@]}"; do
  path="${entry% *}"
  expected="${entry#* }"
  url="$BASE_URL$path"
  tmp="$(mktemp)"
  code="$(curl -k -sS -L --max-redirs 0 -H "X-Tenant-Id: $TENANT_ID" -o "$tmp" -w "%{http_code}" "$url" || true)"
  if [[ "$code" != "200" ]]; then
    echo "FAIL $code $url"
    failures=$((failures + 1))
    rm -f "$tmp"
    continue
  fi
  if [[ "$expected" == "json" ]]; then
    if ! python3 -m json.tool "$tmp" >/dev/null; then
      echo "FAIL invalid-json $url"
      failures=$((failures + 1))
      rm -f "$tmp"
      continue
    fi
  fi
  echo "PASS $code $url"
  rm -f "$tmp"
done

if [[ "$failures" -gt 0 ]]; then
  echo "Route smoke test failed for $failures route(s)." >&2
  exit 1
fi

echo "KPI route smoke passed for $BASE_URL"
