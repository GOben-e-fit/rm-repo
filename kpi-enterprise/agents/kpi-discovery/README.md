# kpi-discovery

Heuristic, deterministic KPI candidate discovery — **no LLM**, no I/O.
Given a set of dataset profiles (column statistics + sample values),
emits scored `KpiCandidate` proposals using a curated template library
across finance, sales, ops, support, hr, marketing.

## Why heuristic before LLM?

- Reproducible byte-for-byte (eval-friendly).
- Zero cost / zero latency.
- Defines the floor: any LLM-augmented v2 must beat this on the eval set
  (`../kpi-evals/` future).
- Demonstrates the contract that the LLM stage will need to honour
  (Pydantic-typed `KpiCandidate` output).

## Public API

```python
from kpi_discovery import ColumnProfile, DatasetProfile, discover

result = discover([
    DatasetProfile(
        id="ds_finance_invoices",
        name="finance_invoices",
        columns=[
            ColumnProfile(name="total_amount", type="decimal"),
            ColumnProfile(name="cost_amount",  type="decimal"),
            ColumnProfile(name="created_at",   type="timestamp"),
        ],
        domain_hint="finance",
    )
])
for c in result.candidates:
    print(c.proposed_name, c.score, c.template_id)
```

## Templates

Currently 14 templates across 6 domains. Each template carries:
- column-name regex with alphanumeric word boundaries (treats `_` and `-` as separators)
- numeric-required flag (skips text columns where SUM is meaningless)
- domain hint bonus (+0.05 if dataset name matches)
- quality penalties for high null_ratio / low distinct_count
- PII guard (PII-flagged columns excluded from finance/ops aggregates)
- canonical SQL skeleton, unit, granularity, direction, base score

Add new templates in `kpi_discovery/profiler.py` and add a test in
`tests/test_discovery.py`.

## Tests

```bash
pip install -e ".[test]"
pytest -v
```

10 tests cover: positive matching, multi-domain isolation, low-quality
penalty, PII exclusion, score thresholding, reproducibility, empty/safe
inputs.

## Integration

The orchestrator wires this in via `app/discovery_bridge.py`. POST
`/v1/kpi-candidates` runs `discover()` synchronously and persists each
`KpiCandidate` to the tenant store, also recording an `agent_run`
audit entry.
