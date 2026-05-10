"""Pydantic models matching api/openapi.v1.yaml.

Models are deliberately permissive on optional fields so the demo store can
hydrate them without schema friction. The OpenAPI document remains the
contract of record; this module is the in-process implementation of it.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# ---------- Enums ----------

class Brand(str, Enum):
    BENEFIT = "ben-e-fit"
    MEDIALINE = "medialine"
    KIGURU = "ki-guru"
    CUSTOM = "custom"


class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    PII = "pii"


class Granularity(str, Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class Direction(str, Enum):
    UP = "up_is_favorable"
    DOWN = "down_is_favorable"
    NEUTRAL = "neutral"


class AgentRunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"


class InsightSeverity(str, Enum):
    INFO = "info"
    WARN = "warn"
    CRITICAL = "critical"


class BriefingType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    AD_HOC = "ad_hoc"


class BriefingStatus(str, Enum):
    QUEUED = "queued"
    GENERATING = "generating"
    READY = "ready"
    DELIVERED = "delivered"
    FAILED = "failed"


# ---------- System ----------

class Health(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    uptime_seconds: int


# ---------- Tenants ----------

class TenantBase(BaseModel):
    slug: str
    display_name: str
    brand: Brand
    external_llm_allowed: bool = False


class TenantCreate(TenantBase):
    admin_email: str


class TenantUpdate(BaseModel):
    display_name: str | None = None
    brand: Brand | None = None
    external_llm_allowed: bool | None = None


class Tenant(TenantBase):
    id: str = Field(pattern=r"^tnt_[a-z0-9]{4,32}$")
    keycloak_realm: str
    data_classification_default: DataClassification = DataClassification.INTERNAL
    created_at: datetime


# ---------- Sources ----------

class SourceCreate(BaseModel):
    type: Literal["airbyte", "upload", "rest", "crawl4ai", "nimble"]
    name: str
    config: dict[str, Any] = Field(default_factory=dict)


class Source(SourceCreate):
    id: str
    last_sync: datetime | None = None
    status: Literal["healthy", "degraded", "failed", "unknown"] = "unknown"


# ---------- Datasets ----------

class Dataset(BaseModel):
    id: str
    name: str
    catalog_uri: str
    owner: str | None = None
    row_count_estimate: int | None = None
    sensitivity: DataClassification = DataClassification.INTERNAL


class DatasetColumn(BaseModel):
    name: str
    type: str
    null_ratio: float
    distinct_count: int
    sample_values: list[str] = Field(default_factory=list)
    detected_pii: bool = False


class DatasetProfile(BaseModel):
    dataset_id: str
    columns: list[DatasetColumn]


# ---------- Metric Definitions ----------

class MetricTarget(BaseModel):
    value: float
    tolerance_pct: float


class MetricAnomaly(BaseModel):
    method: Literal["stl_zscore", "robust_z", "prophet_residual", "isolation_forest"]
    threshold: float


class MetricDefinitionCreate(BaseModel):
    name: str
    display_name: str
    description: str | None = None
    owner: str
    domain: str
    unit: str
    granularity: Granularity
    direction: Direction
    dbt_model: str | None = None
    expression: str
    filter: str | None = None
    target: MetricTarget | None = None
    data_classification: DataClassification = DataClassification.INTERNAL
    compliance_tags: list[str] = Field(default_factory=list)
    refresh_cron: str | None = None
    anomaly: MetricAnomaly | None = None


class MetricDefinition(MetricDefinitionCreate):
    id: str
    version: int
    tenant_id: str
    created_at: datetime
    git_ref: str | None = None


# ---------- KPI Candidates ----------

class KpiCandidate(BaseModel):
    id: str
    proposed_name: str
    score: float = Field(ge=0.0, le=1.0)
    rationale: str | None = None
    source_dataset_id: str
    proposed_sql: str | None = None
    suggested_unit: str | None = None
    suggested_granularity: Granularity | None = None
    suggested_direction: Direction | None = None
    suggested_domain: str | None = None
    template_id: str | None = None
    status: Literal["new", "in_review", "accepted", "rejected"] = "new"


class DiscoveryRunRequest(BaseModel):
    dataset_ids: list[str]
    scope_hint: str | None = None


class PromoteRequest(BaseModel):
    approver: str
    approval_note: str | None = None
    target_metric_name: str | None = None


# ---------- KPI Observations ----------

class KpiObservation(BaseModel):
    metric_id: str
    metric_version: int | None = None
    ts: datetime
    value: float
    confidence: float | None = None


# ---------- Driver Trees ----------

class DriverTreeCreate(BaseModel):
    name: str
    owner: str


class DriverTree(DriverTreeCreate):
    id: str
    node_count: int = 0
    edge_count: int = 0
    updated_at: datetime


class DriverNode(BaseModel):
    id: str
    metric_id: str | None = None
    label: str
    position: dict[str, float] | None = None


class DriverEdge(BaseModel):
    id: str
    from_node: str
    to_node: str
    weight: float | None = None
    confidence: float | None = None
    rationale: str | None = None


# ---------- OKR ----------

class OkrLink(BaseModel):
    id: str
    objective: str
    key_result: str
    metric_id: str
    action_template_id: str | None = None


# ---------- Insights ----------

class InsightAction(BaseModel):
    action_template: str
    expected_impact: str | None = None


class Insight(BaseModel):
    id: str
    type: Literal["anomaly", "trend_break", "threshold", "rca"]
    metric_id: str
    severity: InsightSeverity
    what_happened: str
    why_hypothesis: str | None = None
    what_to_do: list[InsightAction] = Field(default_factory=list)
    owner: str | None = None
    evidence_id: str | None = None
    created_at: datetime


# ---------- Briefings ----------

class BriefingScope(BaseModel):
    kpi_ids: list[str] = Field(default_factory=list)
    include_benchmarks: bool = True


class BriefingCreate(BaseModel):
    type: BriefingType
    audience: Literal["cfo", "ceo", "coo", "controller", "all"]
    scope: BriefingScope | None = None
    delivery: list[Literal["email", "slack", "teams", "documenso"]] = Field(default_factory=list)


class Briefing(BaseModel):
    id: str
    type: BriefingType
    audience: Literal["cfo", "ceo", "coo", "controller", "all"]
    status: BriefingStatus
    markdown_url: str | None = None
    pdf_url: str | None = None
    signed_pdf_url: str | None = None
    delivered_to: list[str] = Field(default_factory=list)
    created_at: datetime


# ---------- Agent Runs ----------

class AgentRunRef(BaseModel):
    run_id: str
    status: AgentRunStatus
    trace_url: str | None = None


class LlmCall(BaseModel):
    model: str
    tokens_in: int
    tokens_out: int
    cost_eur: float
    external: bool = False


class AgentApproval(BaseModel):
    required: bool = False
    approvers: list[str] = Field(default_factory=list)
    granted: bool = False


class AgentRun(BaseModel):
    run_id: str
    tenant_id: str
    agent: str
    status: AgentRunStatus
    started_at: datetime
    ended_at: datetime | None = None
    tools_used: list[str] = Field(default_factory=list)
    llm_calls: list[LlmCall] = Field(default_factory=list)
    evidence_bundle: str | None = None
    approval: AgentApproval = Field(default_factory=AgentApproval)
    rollback_snapshot: str | None = None
    outputs: dict[str, Any] | None = None


class EvidenceBundle(BaseModel):
    id: str
    run_id: str
    signed_url: str
    expires_at: datetime
    sha256: str | None = None


# ---------- Benchmarks ----------

class Benchmark(BaseModel):
    id: str
    metric_name: str
    source: str
    license: str | None = None
    reference_value: float | None = None
    reference_period: str | None = None
    last_fetched_at: datetime | None = None


# ---------- Webhooks ----------

class Webhook(BaseModel):
    id: str
    url: str
    events: list[
        Literal["insight.created", "briefing.delivered", "agent_run.completed", "action.applied"]
    ]
    secret_ref: str | None = None
    active: bool = True


# ---------- Errors ----------

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    tenant_id: str | None = None
