"""Deterministic tests for the heuristic KPI discovery agent."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kpi_discovery import ColumnProfile, DatasetProfile, discover  # noqa: E402


def _col(name: str, dtype: str = "decimal", **kw) -> ColumnProfile:
    defaults = {"null_ratio": 0.0, "distinct_count": 1000, "sample_values": []}
    defaults.update(kw)
    return ColumnProfile(name=name, type=dtype, **defaults)


def test_finds_mrr_in_finance_dataset() -> None:
    ds = DatasetProfile(
        id="ds_finance_subscriptions",
        name="finance_subscriptions",
        columns=[
            _col("subscription_id", "uuid"),
            _col("mrr_eur", "decimal"),
            _col("active", "bool"),
        ],
        domain_hint="finance",
    )
    result = discover([ds])
    assert result.profiled_datasets == 1
    names = {c.proposed_name for c in result.candidates}
    assert "monthly_recurring_revenue" in names
    mrr = next(c for c in result.candidates if c.proposed_name == "monthly_recurring_revenue")
    assert mrr.score >= 0.9
    assert "SUM(mrr_eur)" in mrr.proposed_sql
    assert mrr.suggested_unit == "EUR"
    assert mrr.suggested_direction == "up_is_favorable"


def test_finds_revenue_and_cogs_in_invoice_dataset() -> None:
    ds = DatasetProfile(
        id="ds_invoices",
        name="finance_invoices",
        columns=[
            _col("invoice_id", "uuid"),
            _col("total_amount", "decimal"),
            _col("cost_amount", "decimal"),
            _col("created_at", "timestamp"),
        ],
    )
    result = discover([ds])
    found = {c.template_id for c in result.candidates}
    assert "finance.revenue" in found
    assert "finance.cogs" in found


def test_low_quality_column_lowers_score() -> None:
    ds = DatasetProfile(
        id="ds_x",
        name="finance",
        columns=[
            _col("revenue", "decimal", null_ratio=0.7, distinct_count=2),
        ],
    )
    result = discover([ds])
    rev = next(c for c in result.candidates if c.template_id == "finance.revenue")
    assert rev.score < 0.85  # base 0.85 minus penalties


def test_pii_columns_excluded_from_finance_aggregates() -> None:
    ds = DatasetProfile(
        id="ds_y",
        name="finance",
        columns=[
            _col("revenue", "decimal", detected_pii=True),
        ],
    )
    result = discover([ds])
    assert all(c.template_id != "finance.revenue" for c in result.candidates), (
        "PII-flagged finance.revenue column should be skipped"
    )


def test_min_score_threshold_filters() -> None:
    ds = DatasetProfile(
        id="ds_z",
        name="random",
        columns=[
            _col("revenue", "decimal", null_ratio=0.6, distinct_count=2),
        ],
    )
    high = discover([ds], min_score=0.4)
    low = discover([ds], min_score=0.95)
    assert any(c.template_id == "finance.revenue" for c in high.candidates)
    assert all(c.template_id != "finance.revenue" for c in low.candidates)


def test_reproducible_output_for_same_input() -> None:
    ds = DatasetProfile(
        id="ds_repro",
        name="sales_pipeline",
        columns=[
            _col("opportunity_id", "uuid"),
            _col("stage", "string", distinct_count=4),
            _col("created_at", "timestamp"),
            _col("closed_at", "timestamp", null_ratio=0.4),
        ],
    )
    a = discover([ds])
    b = discover([ds])
    assert [c.id for c in a.candidates] == [c.id for c in b.candidates]
    assert [round(c.score, 4) for c in a.candidates] == [round(c.score, 4) for c in b.candidates]


def test_empty_dataset_skipped() -> None:
    ds = DatasetProfile(id="ds_empty", name="x", columns=[])
    result = discover([ds])
    assert result.profiled_datasets == 0
    assert "ds_empty" in result.skipped_datasets


def test_multi_domain_dataset_picks_strongest_per_template() -> None:
    ds = DatasetProfile(
        id="ds_orders",
        name="ops_orders",
        columns=[
            _col("order_id", "uuid"),
            _col("open_amount", "decimal"),
            _col("revenue", "decimal", distinct_count=500),
        ],
    )
    result = discover([ds])
    template_ids = [c.template_id for c in result.candidates]
    # at most one per template per dataset
    assert len(template_ids) == len(set(template_ids))


def test_sales_cycle_template_matches_timestamp_pair() -> None:
    ds = DatasetProfile(
        id="ds_opps",
        name="sales_pipeline",
        columns=[
            _col("opportunity_id", "uuid"),
            _col("created_at", "timestamp"),
            _col("closed_at", "timestamp"),
            _col("stage", "string", distinct_count=4),
        ],
    )
    result = discover([ds])
    assert any(c.template_id == "sales.cycle_days" for c in result.candidates)


def test_candidate_id_is_stable_and_safe() -> None:
    ds = DatasetProfile(
        id="ds_finance/01",
        name="weird name",
        columns=[_col("MRR EUR  ", "decimal")],
    )
    # column with weird name should not crash the matcher (regex is on name, not id)
    result = discover([ds])
    # may or may not find a candidate, but ids must be safe
    for c in result.candidates:
        assert c.id.startswith("cand_")
        assert all(ch.isalnum() or ch == "_" for ch in c.id)
