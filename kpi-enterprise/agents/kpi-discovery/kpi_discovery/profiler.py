"""Deterministic, LLM-free KPI candidate discovery.

The discovery agent takes a list of dataset profiles (table name + column
statistics) and emits scored KpiCandidate proposals. Templates encode
common business KPIs across finance, sales, ops, support, marketing, hr.

Templates are matched by combining:
  * column-name regex against profile.columns
  * column-type compatibility (numeric for SUM/AVG, etc.)
  * dataset/table-name hints for domain
  * a base score per template, adjusted up by name specificity and down by
    null_ratio / low distinct_count

Heuristic-only on purpose: outputs must be reproducible byte-for-byte
without external state. LLM-assisted discovery comes in v2 and lives
behind LiteLLM via an explicit policy gate.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

from pydantic import BaseModel, Field


# ---------- Inputs ----------

class ColumnProfile(BaseModel):
    name: str
    type: str  # canonical: int, decimal, float, string, date, timestamp, bool, uuid, json
    null_ratio: float = 0.0
    distinct_count: int = 0
    sample_values: list[str] = Field(default_factory=list)
    detected_pii: bool = False


class DatasetProfile(BaseModel):
    id: str
    name: str
    columns: list[ColumnProfile]
    row_count_estimate: int | None = None
    domain_hint: str | None = None  # finance / sales / ops / support / marketing / hr / product


# ---------- Output ----------

class KpiCandidate(BaseModel):
    id: str
    proposed_name: str
    score: float = Field(ge=0.0, le=1.0)
    rationale: str
    source_dataset_id: str
    proposed_sql: str
    suggested_unit: str
    suggested_granularity: str
    suggested_direction: str
    suggested_domain: str
    template_id: str


@dataclass
class DiscoveryResult:
    candidates: list[KpiCandidate] = field(default_factory=list)
    profiled_datasets: int = 0
    skipped_datasets: list[str] = field(default_factory=list)


# ---------- Templates ----------

NUMERIC = {"int", "decimal", "float", "double", "numeric", "bigint", "smallint", "integer"}
DATE_LIKE = {"date", "timestamp", "datetime", "timestamptz"}


def _word_pattern(*words: str) -> re.Pattern[str]:
    """Match any of `words` with alphanumeric boundaries (treats `_` and `-` as separators)."""
    alt = "|".join(re.escape(w) for w in words)
    return re.compile(rf"(?<![A-Za-z0-9])({alt})(?![A-Za-z0-9])", re.I)


@dataclass(frozen=True)
class Template:
    template_id: str
    proposed_name: str
    column_pattern: re.Pattern[str]
    domain: str
    unit: str
    granularity: str
    direction: str
    sql_template: str
    base_score: float
    requires_numeric: bool = True
    domain_hints: tuple[str, ...] = ()


_TEMPLATES: tuple[Template, ...] = (
    Template(
        template_id="finance.mrr",
        proposed_name="monthly_recurring_revenue",
        column_pattern=_word_pattern("mrr", "monthly_recurring_revenue", "monthly_revenue"),
        domain="finance",
        unit="EUR",
        granularity="month",
        direction="up_is_favorable",
        sql_template="SUM({col})",
        base_score=0.95,
        domain_hints=("finance", "subscription", "billing"),
    ),
    Template(
        template_id="finance.arr",
        proposed_name="annual_recurring_revenue",
        column_pattern=_word_pattern("arr", "annual_recurring_revenue"),
        domain="finance",
        unit="EUR",
        granularity="month",
        direction="up_is_favorable",
        sql_template="SUM({col})",
        base_score=0.95,
        domain_hints=("finance", "subscription"),
    ),
    Template(
        template_id="finance.revenue",
        proposed_name="revenue",
        column_pattern=_word_pattern("revenue", "net_revenue", "gross_revenue", "amount", "invoice_amount", "total_amount"),
        domain="finance",
        unit="EUR",
        granularity="month",
        direction="up_is_favorable",
        sql_template="SUM({col})",
        base_score=0.85,
        domain_hints=("finance", "billing", "invoice", "sales"),
    ),
    Template(
        template_id="finance.cogs",
        proposed_name="cost_of_goods_sold",
        column_pattern=_word_pattern("cogs", "cost_of_goods", "cost_of_sales", "cost_amount"),
        domain="finance",
        unit="EUR",
        granularity="month",
        direction="down_is_favorable",
        sql_template="SUM({col})",
        base_score=0.9,
        domain_hints=("finance", "billing"),
    ),
    Template(
        template_id="finance.cash_position",
        proposed_name="cash_position",
        column_pattern=_word_pattern("cash", "cash_balance", "cash_position", "bank_balance"),
        domain="finance",
        unit="EUR",
        granularity="day",
        direction="up_is_favorable",
        sql_template="MAX({col})",
        base_score=0.88,
        domain_hints=("finance", "cash", "treasury"),
    ),
    Template(
        template_id="sales.opportunity_count",
        proposed_name="opportunity_count",
        column_pattern=_word_pattern("opportunity_id", "opp_id", "deal_id"),
        domain="sales",
        unit="count",
        granularity="week",
        direction="up_is_favorable",
        sql_template="COUNT(DISTINCT {col})",
        base_score=0.82,
        requires_numeric=False,
        domain_hints=("sales", "crm", "opportunity", "pipeline"),
    ),
    Template(
        template_id="sales.win_rate",
        proposed_name="win_rate",
        column_pattern=_word_pattern("stage", "deal_stage", "status"),
        domain="sales",
        unit="ratio",
        granularity="month",
        direction="up_is_favorable",
        sql_template="SUM(CASE WHEN {col} = 'closed_won' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0)",
        base_score=0.78,
        requires_numeric=False,
        domain_hints=("sales", "crm", "pipeline"),
    ),
    Template(
        template_id="sales.cycle_days",
        proposed_name="sales_cycle_days",
        column_pattern=_word_pattern("closed_at", "won_at", "created_at"),
        domain="sales",
        unit="days",
        granularity="week",
        direction="down_is_favorable",
        sql_template="AVG(EXTRACT(EPOCH FROM (closed_at - created_at)) / 86400.0)",
        base_score=0.7,
        requires_numeric=False,
        domain_hints=("sales", "crm", "opportunity"),
    ),
    Template(
        template_id="ops.order_backlog",
        proposed_name="order_backlog_eur",
        column_pattern=_word_pattern("open_amount", "backlog_amount", "outstanding_amount"),
        domain="operations",
        unit="EUR",
        granularity="day",
        direction="neutral",
        sql_template="SUM({col})",
        base_score=0.85,
        domain_hints=("ops", "fulfillment", "supply"),
    ),
    Template(
        template_id="ops.order_count",
        proposed_name="order_count",
        column_pattern=_word_pattern("order_id", "order_number", "sales_order_id"),
        domain="operations",
        unit="count",
        granularity="day",
        direction="up_is_favorable",
        sql_template="COUNT(DISTINCT {col})",
        base_score=0.78,
        requires_numeric=False,
        domain_hints=("ops", "orders"),
    ),
    Template(
        template_id="support.ticket_count",
        proposed_name="open_ticket_count",
        column_pattern=_word_pattern("ticket_id", "case_id"),
        domain="support",
        unit="count",
        granularity="day",
        direction="down_is_favorable",
        sql_template="COUNT(DISTINCT {col})",
        base_score=0.75,
        requires_numeric=False,
        domain_hints=("support", "ticket", "service_desk"),
    ),
    Template(
        template_id="support.nps",
        proposed_name="net_promoter_score",
        column_pattern=_word_pattern("nps_score", "nps", "promoter_score"),
        domain="support",
        unit="score",
        granularity="month",
        direction="up_is_favorable",
        sql_template=(
            "100.0 * (SUM(CASE WHEN {col} >= 9 THEN 1 ELSE 0 END) "
            "- SUM(CASE WHEN {col} <= 6 THEN 1 ELSE 0 END)) / NULLIF(COUNT(*), 0)"
        ),
        base_score=0.92,
        domain_hints=("support", "survey", "csat"),
    ),
    Template(
        template_id="hr.headcount",
        proposed_name="headcount",
        column_pattern=_word_pattern("employee_id", "emp_id", "staff_id"),
        domain="hr",
        unit="count",
        granularity="month",
        direction="neutral",
        sql_template="COUNT(DISTINCT {col})",
        base_score=0.72,
        requires_numeric=False,
        domain_hints=("hr", "people", "workforce"),
    ),
    Template(
        template_id="marketing.lead_count",
        proposed_name="lead_count",
        column_pattern=_word_pattern("lead_id", "lead"),
        domain="marketing",
        unit="count",
        granularity="week",
        direction="up_is_favorable",
        sql_template="COUNT(DISTINCT {col})",
        base_score=0.7,
        requires_numeric=False,
        domain_hints=("marketing", "lead", "campaign"),
    ),
)


# ---------- Engine ----------

def _is_numeric(col: ColumnProfile) -> bool:
    return col.type.lower() in NUMERIC


def _domain_bonus(template: Template, dataset: DatasetProfile) -> float:
    if not template.domain_hints:
        return 0.0
    needle = f"{dataset.name} {dataset.domain_hint or ''}".lower()
    for hint in template.domain_hints:
        if hint in needle:
            return 0.05
    return 0.0


def _quality_penalty(col: ColumnProfile) -> float:
    penalty = 0.0
    if col.null_ratio >= 0.5:
        penalty += 0.1
    elif col.null_ratio >= 0.2:
        penalty += 0.05
    if col.distinct_count <= 1:
        penalty += 0.2
    return penalty


def _candidate_id(dataset_id: str, template_id: str, column_name: str) -> str:
    safe = f"{dataset_id}.{template_id}.{column_name}".lower()
    safe = re.sub(r"[^a-z0-9]+", "_", safe).strip("_")
    return f"cand_{safe[:64]}"


def _evaluate(template: Template, dataset: DatasetProfile, col: ColumnProfile) -> KpiCandidate | None:
    if not template.column_pattern.search(col.name):
        return None
    if template.requires_numeric and not _is_numeric(col):
        return None
    if col.detected_pii and template.domain not in {"hr", "support", "marketing"}:
        # PII-bearing columns are not appropriate for finance/ops aggregates.
        return None

    score = template.base_score + _domain_bonus(template, dataset) - _quality_penalty(col)
    score = max(0.0, min(1.0, score))
    sql = template.sql_template.format(col=col.name)
    rationale = (
        f"Column '{col.name}' on dataset '{dataset.name}' matches "
        f"template {template.template_id} (base score {template.base_score:.2f}, "
        f"adjusted {score:.2f})."
    )
    return KpiCandidate(
        id=_candidate_id(dataset.id, template.template_id, col.name),
        proposed_name=template.proposed_name,
        score=round(score, 4),
        rationale=rationale,
        source_dataset_id=dataset.id,
        proposed_sql=sql,
        suggested_unit=template.unit,
        suggested_granularity=template.granularity,
        suggested_direction=template.direction,
        suggested_domain=template.domain,
        template_id=template.template_id,
    )


def discover(
    datasets: Iterable[DatasetProfile],
    *,
    min_score: float = 0.5,
    max_per_template: int = 1,
    templates: Iterable[Template] = _TEMPLATES,
) -> DiscoveryResult:
    """Run the heuristic discovery over the given dataset profiles.

    `max_per_template` keeps the result list short and useful: if revenue
    columns appear in several datasets, the highest-scored wins per dataset.
    """
    result = DiscoveryResult()
    seen_ids: set[str] = set()
    for dataset in datasets:
        if not dataset.columns:
            result.skipped_datasets.append(dataset.id)
            continue
        result.profiled_datasets += 1

        per_template: dict[str, list[KpiCandidate]] = {}
        for template in templates:
            for col in dataset.columns:
                cand = _evaluate(template, dataset, col)
                if cand is None or cand.score < min_score or cand.id in seen_ids:
                    continue
                per_template.setdefault(template.template_id, []).append(cand)

        for template_id, cands in per_template.items():
            cands.sort(key=lambda c: c.score, reverse=True)
            for cand in cands[:max_per_template]:
                if cand.id in seen_ids:
                    continue
                seen_ids.add(cand.id)
                result.candidates.append(cand)

    result.candidates.sort(key=lambda c: c.score, reverse=True)
    return result


__all__ = [
    "ColumnProfile",
    "DatasetProfile",
    "KpiCandidate",
    "DiscoveryResult",
    "Template",
    "discover",
]
