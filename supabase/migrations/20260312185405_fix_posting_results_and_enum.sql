-- CRIT-1: Add 'partial' to posting_job_status enum
ALTER TYPE posting_job_status ADD VALUE IF NOT EXISTS 'partial';

-- MED-5: Fix posting_results table — add missing columns to match code expectations
-- The table has job_id but code uses posting_job_id — add alias column
ALTER TABLE posting_results
  ADD COLUMN IF NOT EXISTS posting_job_id uuid REFERENCES posting_jobs(id) ON DELETE CASCADE,
  ADD COLUMN IF NOT EXISTS tenant_id uuid REFERENCES tenants(id) ON DELETE CASCADE,
  ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();

-- Backfill posting_job_id from job_id for any existing rows
UPDATE posting_results SET posting_job_id = job_id WHERE posting_job_id IS NULL AND job_id IS NOT NULL;

-- Add RLS policy for tenant isolation on posting_results
ALTER TABLE posting_results ENABLE ROW LEVEL SECURITY;

-- Notify PostgREST to reload schema cache
NOTIFY pgrst, 'reload schema';
