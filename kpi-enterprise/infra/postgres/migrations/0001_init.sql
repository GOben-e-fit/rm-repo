-- KPI Enterprise Mining — Postgres bootstrap migration
--
-- Creates the canonical tenant-scoped schema with hard Row-Level-Security.
-- Every shared table has a `tenant_id` column and an RLS policy that
-- compares it to the session-local `app.tenant` setting which is injected
-- by the api-gateway / orchestrator after JWT verification.
--
-- Apply order:
--   psql -f 0001_init.sql
-- The migration is idempotent (CREATE IF NOT EXISTS / DROP POLICY IF EXISTS).
--
-- Verifying RLS:
--   SET app.tenant = 'tnt_demo';
--   SELECT * FROM metric_definitions;            -- only tnt_demo rows
--   SET app.tenant = 'tnt_other';
--   SELECT * FROM metric_definitions;            -- empty / different rows
--
-- Cross-tenant deny tests against this schema live under
-- agents/orchestrator/tests/test_tenant_deny.py and
-- contracts/sql-tests/ (added in CP-104+).

BEGIN;

-- Application role + ownership ---------------------------------------------

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'kpi_app') THEN
    CREATE ROLE kpi_app NOLOGIN;
  END IF;
END
$$;

CREATE SCHEMA IF NOT EXISTS kpi AUTHORIZATION kpi_app;
SET search_path = kpi, public;

-- Helper: extract current tenant from session setting ----------------------

CREATE OR REPLACE FUNCTION kpi.current_tenant() RETURNS text
LANGUAGE sql STABLE AS $$
  SELECT current_setting('app.tenant', true)
$$;

COMMENT ON FUNCTION kpi.current_tenant() IS
  'Returns the tenant_id active for the current session. The api-gateway is responsible for SET app.tenant = ''<id>'' after JWT verification.';

-- Tenants registry (platform-level, no RLS) --------------------------------

CREATE TABLE IF NOT EXISTS kpi.tenants (
  id                            text PRIMARY KEY
                                  CHECK (id ~ '^tnt_[a-z0-9]{4,32}$'),
  slug                          text NOT NULL UNIQUE,
  display_name                  text NOT NULL,
  brand                         text NOT NULL
                                  CHECK (brand IN ('ben-e-fit','medialine','ki-guru','custom')),
  keycloak_realm                text NOT NULL,
  data_classification_default   text NOT NULL DEFAULT 'internal'
                                  CHECK (data_classification_default IN
                                         ('public','internal','confidential','pii')),
  external_llm_allowed          boolean NOT NULL DEFAULT false,
  status                        text NOT NULL DEFAULT 'active'
                                  CHECK (status IN ('active','suspended','offboarded')),
  created_at                    timestamptz NOT NULL DEFAULT now()
);

-- Sources, Datasets ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS kpi.sources (
  id            text PRIMARY KEY,
  tenant_id     text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  type          text NOT NULL CHECK (type IN ('airbyte','upload','rest','crawl4ai','nimble')),
  name          text NOT NULL,
  config        jsonb NOT NULL DEFAULT '{}'::jsonb,
  last_sync     timestamptz,
  status        text NOT NULL DEFAULT 'unknown'
                  CHECK (status IN ('healthy','degraded','failed','unknown')),
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS sources_tenant_idx ON kpi.sources(tenant_id);

CREATE TABLE IF NOT EXISTS kpi.datasets (
  id                  text PRIMARY KEY,
  tenant_id           text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  name                text NOT NULL,
  catalog_uri         text NOT NULL,
  owner               text,
  row_count_estimate  bigint,
  sensitivity         text NOT NULL DEFAULT 'internal'
                        CHECK (sensitivity IN ('public','internal','confidential','pii')),
  created_at          timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS datasets_tenant_idx ON kpi.datasets(tenant_id);

-- Metric Definitions (versioned) -------------------------------------------

CREATE TABLE IF NOT EXISTS kpi.metric_definitions (
  id                    text NOT NULL,
  version               int NOT NULL DEFAULT 1,
  tenant_id             text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  name                  text NOT NULL,
  display_name          text NOT NULL,
  description           text,
  owner                 text NOT NULL,
  domain                text NOT NULL,
  unit                  text NOT NULL,
  granularity           text NOT NULL CHECK (granularity IN
                          ('minute','hour','day','week','month','quarter','year')),
  direction             text NOT NULL CHECK (direction IN
                          ('up_is_favorable','down_is_favorable','neutral')),
  dbt_model             text,
  expression            text NOT NULL,
  filter                text,
  target                jsonb,
  data_classification   text NOT NULL DEFAULT 'internal'
                          CHECK (data_classification IN
                                 ('public','internal','confidential','pii')),
  compliance_tags       text[] NOT NULL DEFAULT '{}',
  refresh_cron          text,
  anomaly               jsonb,
  external_llm_allowed  boolean NOT NULL DEFAULT false,
  git_ref               text,
  created_at            timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (id, version),
  UNIQUE (tenant_id, name, version)
);
CREATE INDEX IF NOT EXISTS metric_definitions_tenant_idx ON kpi.metric_definitions(tenant_id);

-- KPI Candidates / Observations --------------------------------------------

CREATE TABLE IF NOT EXISTS kpi.kpi_candidates (
  id                      text PRIMARY KEY,
  tenant_id               text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  proposed_name           text NOT NULL,
  score                   numeric(4,3) NOT NULL CHECK (score >= 0 AND score <= 1),
  rationale               text,
  source_dataset_id       text,
  proposed_sql            text,
  suggested_unit          text,
  suggested_granularity   text,
  suggested_direction     text,
  suggested_domain        text,
  template_id             text,
  status                  text NOT NULL DEFAULT 'new'
                            CHECK (status IN ('new','in_review','accepted','rejected')),
  created_at              timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS kpi_candidates_tenant_idx ON kpi.kpi_candidates(tenant_id);

CREATE TABLE IF NOT EXISTS kpi.kpi_observations (
  tenant_id        text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  metric_id        text NOT NULL,
  metric_version   int NOT NULL,
  ts               timestamptz NOT NULL,
  value            double precision NOT NULL,
  confidence       numeric(4,3),
  PRIMARY KEY (tenant_id, metric_id, metric_version, ts),
  FOREIGN KEY (metric_id, metric_version)
    REFERENCES kpi.metric_definitions(id, version) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS kpi_observations_tenant_metric_ts_idx
  ON kpi.kpi_observations(tenant_id, metric_id, ts DESC);

-- Driver Trees + Nodes + Edges (mirror of Neo4j for read-fallback) ---------

CREATE TABLE IF NOT EXISTS kpi.driver_trees (
  id           text PRIMARY KEY,
  tenant_id    text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  name         text NOT NULL,
  owner        text NOT NULL,
  node_count   int NOT NULL DEFAULT 0,
  edge_count   int NOT NULL DEFAULT 0,
  updated_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS kpi.driver_nodes (
  id           text PRIMARY KEY,
  tenant_id    text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  tree_id      text NOT NULL REFERENCES kpi.driver_trees(id) ON DELETE CASCADE,
  metric_id    text,
  label        text NOT NULL,
  position     jsonb
);
CREATE INDEX IF NOT EXISTS driver_nodes_tenant_tree_idx ON kpi.driver_nodes(tenant_id, tree_id);

CREATE TABLE IF NOT EXISTS kpi.driver_edges (
  id           text PRIMARY KEY,
  tenant_id    text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  tree_id      text NOT NULL REFERENCES kpi.driver_trees(id) ON DELETE CASCADE,
  from_node    text NOT NULL REFERENCES kpi.driver_nodes(id) ON DELETE CASCADE,
  to_node      text NOT NULL REFERENCES kpi.driver_nodes(id) ON DELETE CASCADE,
  weight       numeric,
  confidence   numeric(4,3),
  rationale    text
);
CREATE INDEX IF NOT EXISTS driver_edges_tenant_tree_idx ON kpi.driver_edges(tenant_id, tree_id);

-- OKR + Insights + Briefings -----------------------------------------------

CREATE TABLE IF NOT EXISTS kpi.okr_links (
  id                    text PRIMARY KEY,
  tenant_id             text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  objective             text NOT NULL,
  key_result            text NOT NULL,
  metric_id             text NOT NULL,
  action_template_id    text
);
CREATE INDEX IF NOT EXISTS okr_links_tenant_idx ON kpi.okr_links(tenant_id);

CREATE TABLE IF NOT EXISTS kpi.insights (
  id                text PRIMARY KEY,
  tenant_id         text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  type              text NOT NULL CHECK (type IN ('anomaly','trend_break','threshold','rca')),
  metric_id         text NOT NULL,
  severity          text NOT NULL CHECK (severity IN ('info','warn','critical')),
  what_happened     text NOT NULL,
  why_hypothesis    text,
  what_to_do        jsonb NOT NULL DEFAULT '[]'::jsonb,
  owner             text,
  evidence_id       text,
  created_at        timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS insights_tenant_created_idx ON kpi.insights(tenant_id, created_at DESC);

CREATE TABLE IF NOT EXISTS kpi.briefings (
  id                text PRIMARY KEY,
  tenant_id         text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  type              text NOT NULL CHECK (type IN ('daily','weekly','monthly','ad_hoc')),
  audience          text NOT NULL CHECK (audience IN ('cfo','ceo','coo','controller','all')),
  status            text NOT NULL DEFAULT 'queued'
                      CHECK (status IN ('queued','generating','ready','delivered','failed')),
  markdown_url      text,
  pdf_url           text,
  signed_pdf_url    text,
  delivered_to      text[] NOT NULL DEFAULT '{}',
  created_at        timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS briefings_tenant_created_idx ON kpi.briefings(tenant_id, created_at DESC);

-- Agent runs (immutable audit) ---------------------------------------------

CREATE TABLE IF NOT EXISTS kpi.agent_runs (
  run_id              text PRIMARY KEY,
  tenant_id           text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  agent               text NOT NULL,
  status              text NOT NULL CHECK (status IN ('queued','running','succeeded','failed','blocked')),
  started_at          timestamptz NOT NULL DEFAULT now(),
  ended_at            timestamptz,
  tools_used          text[] NOT NULL DEFAULT '{}',
  llm_calls           jsonb NOT NULL DEFAULT '[]'::jsonb,
  evidence_bundle     text,
  approval            jsonb NOT NULL DEFAULT '{"required":false}'::jsonb,
  rollback_snapshot   text,
  outputs             jsonb,
  trace_url           text
);
CREATE INDEX IF NOT EXISTS agent_runs_tenant_started_idx ON kpi.agent_runs(tenant_id, started_at DESC);
CREATE INDEX IF NOT EXISTS agent_runs_agent_status_idx ON kpi.agent_runs(agent, status);

-- Benchmarks (external reference values) -----------------------------------

CREATE TABLE IF NOT EXISTS kpi.benchmarks (
  id                 text PRIMARY KEY,
  tenant_id          text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  metric_name        text NOT NULL,
  source             text NOT NULL,
  license            text,
  reference_value    double precision,
  reference_period   text,
  last_fetched_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS benchmarks_tenant_metric_idx ON kpi.benchmarks(tenant_id, metric_name);

-- Webhooks ------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS kpi.webhooks (
  id           text PRIMARY KEY,
  tenant_id    text NOT NULL REFERENCES kpi.tenants(id) ON DELETE CASCADE,
  url          text NOT NULL,
  events       text[] NOT NULL,
  secret_ref   text,
  active       boolean NOT NULL DEFAULT true,
  created_at   timestamptz NOT NULL DEFAULT now()
);

-- Row-Level Security policies ---------------------------------------------

DO $$
DECLARE
  tbl text;
  tenant_tables text[] := ARRAY[
    'sources','datasets','metric_definitions','kpi_candidates','kpi_observations',
    'driver_trees','driver_nodes','driver_edges','okr_links','insights',
    'briefings','agent_runs','benchmarks','webhooks'
  ];
BEGIN
  FOREACH tbl IN ARRAY tenant_tables LOOP
    EXECUTE format('ALTER TABLE kpi.%I ENABLE ROW LEVEL SECURITY', tbl);
    EXECUTE format('ALTER TABLE kpi.%I FORCE ROW LEVEL SECURITY', tbl);
    EXECUTE format('DROP POLICY IF EXISTS tenant_isolation ON kpi.%I', tbl);
    EXECUTE format(
      'CREATE POLICY tenant_isolation ON kpi.%I '
      'USING (tenant_id = kpi.current_tenant()) '
      'WITH CHECK (tenant_id = kpi.current_tenant())',
      tbl
    );
    EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON kpi.%I TO kpi_app', tbl);
  END LOOP;
END
$$;

GRANT USAGE ON SCHEMA kpi TO kpi_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON kpi.tenants TO kpi_app;

COMMIT;
