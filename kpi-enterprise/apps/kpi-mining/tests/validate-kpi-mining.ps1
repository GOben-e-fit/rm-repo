$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot

$requiredFiles = @(
  'Dockerfile',
  'nginx.conf',
  'index.html',
  'enterprise/index.html',
  'console.html',
  'tools.html',
  'openapi.json',
  'README.md',
  'data-contracts/kpi-metric-contracts.yaml'
)

foreach ($relativePath in $requiredFiles) {
  $path = Join-Path $root $relativePath
  if (-not (Test-Path -LiteralPath $path)) {
    throw "Missing required file: $relativePath"
  }
}

$jsonFiles = @(Get-ChildItem -LiteralPath (Join-Path $root 'api') -Recurse -Filter '*.json')
$jsonFiles += Get-Item -LiteralPath (Join-Path $root 'openapi.json')

foreach ($file in $jsonFiles) {
  Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json | Out-Null
}

$openapi = Get-Content -LiteralPath (Join-Path $root 'openapi.json') -Raw | ConvertFrom-Json
$requiredPaths = @(
  '/api/health',
  '/api/v1/tenants',
  '/api/v1/sources',
  '/api/v1/datasets',
  '/api/v1/metric-definitions',
  '/api/v1/kpi-observations',
  '/api/v1/kpi-candidates',
  '/api/v1/driver-trees',
  '/api/v1/okr-links',
  '/api/v1/insights',
  '/api/v1/briefings',
  '/api/v1/agent-runs',
  '/api/v1/evidence',
  '/api/v1/benchmarks',
  '/api/v1/webhooks'
)

$actualPaths = @($openapi.paths.PSObject.Properties.Name)
foreach ($path in $requiredPaths) {
  if ($actualPaths -notcontains $path) {
    throw "OpenAPI is missing path: $path"
  }
}

$index = Get-Content -LiteralPath (Join-Path $root 'index.html') -Raw
foreach ($needle in @('C-Level Performance OS', 'Metric Store', '/api/v1/metric-definitions', '/enterprise/')) {
  if ($index -notmatch [regex]::Escape($needle)) {
    throw "index.html is missing marker: $needle"
  }
}

$nginx = Get-Content -LiteralPath (Join-Path $root 'nginx.conf') -Raw
foreach ($needle in @('location /enterprise', 'location @agent_api', 'agents-orchestrator', 'proxy_pass http://$orch:8000', 'try_files $uri $uri.json @agent_api')) {
  if ($nginx -notmatch [regex]::Escape($needle)) {
    throw "nginx.conf is missing marker: $needle"
  }
}

$contracts = Get-Content -LiteralPath (Join-Path $root 'data-contracts/kpi-metric-contracts.yaml') -Raw
foreach ($needle in @('require_tenant_id: true', 'net_revenue_retention', 'cash_conversion_cycle')) {
  if ($contracts -notmatch [regex]::Escape($needle)) {
    throw "metric contract is missing marker: $needle"
  }
}

Write-Host "KPI mining validation passed: $($jsonFiles.Count) JSON files checked, $($requiredPaths.Count) OpenAPI paths verified."
