"""Heuristic KPI discovery agent (no LLM, deterministic)."""

from .profiler import (
    ColumnProfile,
    DatasetProfile,
    DiscoveryResult,
    KpiCandidate,
    discover,
)

__all__ = [
    "ColumnProfile",
    "DatasetProfile",
    "DiscoveryResult",
    "KpiCandidate",
    "discover",
]

__version__ = "0.1.0"
