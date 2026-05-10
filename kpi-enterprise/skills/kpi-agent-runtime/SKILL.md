---
name: kpi-agent-runtime
description: Use for KPI Enterprise Mining agents, LiteLLM/OpenRouter/local Qwen routing, Langfuse traces, HITL approvals, agent replay, prompt versions and audit-safe automation.
---

# KPI Agent Runtime

Use this skill for KPI agent design, execution, model routing, traceability and
approval workflows.

## Agent Set

- KPI Miner
- Data Profiler
- Semantic Mapper
- Benchmark Agent
- Driver-Tree Agent
- Anomaly/RCA Agent
- C-Level Briefing Agent
- ROI/Monte-Carlo Agent
- Compliance/Audit Agent
- Action-Orchestrator

## Runtime Requirements

- Every run carries `tenant_id`, `agent`, `model_route`, `prompt_version`, `evalset_id`, `trace_id` and `audit_namespace`.
- Sensitive data defaults to local model aliases through LiteLLM, especially Qwen/Qwen3.x aliases.
- OpenRouter or external models require policy approval and anonymized/public payloads.
- Actions that affect external systems require HITL approval unless explicitly configured otherwise.
- Runs must be replayable from persisted inputs, prompts, model route and evidence references.

## Done Criteria

- Langfuse or equivalent trace exists.
- Evidence artifacts are tenant-scoped.
- Approval/reject state is stored.
- Model fallback behavior is defined.
- Agent output cites source evidence or is marked as draft.
