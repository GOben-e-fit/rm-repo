param(
  [string]$BaseUrl = 'http://localhost:8088',
  [string]$TenantId = 'demo-ceo-office'
)

$ErrorActionPreference = 'Stop'

$base = $BaseUrl.TrimEnd('/')
$routes = @(
  @{ Path = '/'; Expect = 'html' },
  @{ Path = '/enterprise/'; Expect = 'html' },
  @{ Path = '/console.html'; Expect = 'html' },
  @{ Path = '/tools.html'; Expect = 'html' },
  @{ Path = '/openapi.json'; Expect = 'json' },
  @{ Path = '/api/health'; Expect = 'json' },
  @{ Path = '/api/v1/metric-definitions'; Expect = 'json' },
  @{ Path = '/api/v1/kpi-observations'; Expect = 'json' },
  @{ Path = '/api/v1/driver-trees'; Expect = 'json' },
  @{ Path = '/api/v1/agent-runs'; Expect = 'json' }
)

$results = foreach ($route in $routes) {
  $url = "$base$($route.Path)"
  try {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -Headers @{ 'X-Tenant-Id' = $TenantId } -TimeoutSec 20 -MaximumRedirection 0
    if ($route.Expect -eq 'json') {
      $response.Content | ConvertFrom-Json | Out-Null
    }
    [pscustomobject]@{
      Url = $url
      Status = [int]$response.StatusCode
      Type = $response.Headers['Content-Type']
      Result = 'pass'
    }
  } catch {
    $status = 'error'
    $type = ''
    $message = $_.Exception.Message
    if ($_.Exception.Response) {
      $status = [int]$_.Exception.Response.StatusCode
      $type = $_.Exception.Response.Headers['Content-Type']
      $message = "http_$status"
    }
    [pscustomobject]@{
      Url = $url
      Status = $status
      Type = $type
      Result = $message
    }
  }
}

$results | Format-Table -AutoSize

$failed = @($results | Where-Object { $_.Result -ne 'pass' -or $_.Status -ne 200 })
if ($failed.Count -gt 0) {
  throw "Route smoke test failed for $($failed.Count) route(s)."
}

Write-Host "KPI route smoke passed for $base"
