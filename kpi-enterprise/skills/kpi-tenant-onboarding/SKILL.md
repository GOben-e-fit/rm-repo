---
name: kpi-tenant-onboarding
description: Use for onboarding KPI Enterprise Mining tenants, Keycloak roles, storage namespaces, index separation, LiteLLM virtual keys, source setup, policy defaults and isolation tests.
---

# KPI Tenant Onboarding

Use this skill when adding or auditing a tenant for KPI Enterprise Mining.

## Tenant Bootstrap Checklist

- Create tenant record and canonical `tenant_id`.
- Configure Keycloak roles: executive, analyst, operator, auditor, admin.
- Create tenant-scoped MinIO prefixes or buckets.
- Create ClickHouse schema/table policy or tenant partition.
- Create OpenSearch and Qdrant namespace/index policy.
- Create LiteLLM virtual keys and model routing policy.
- Configure Langfuse/trace namespace.
- Register source connectors and data sensitivity.
- Add negative cross-tenant read tests.

## Guardrails

- Every event, metric, source, trace and evidence artifact must include `tenant_id`.
- Sensitive tenant data is denied to external models by default.
- Tenant onboarding is not complete until cross-tenant deny fixtures pass.
- Customer uploads and evidence artifacts must never be shared across tenants unless policy explicitly allows a sanitized aggregate.
