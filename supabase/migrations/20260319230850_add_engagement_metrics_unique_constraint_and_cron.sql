-- Unique constraint on result_id so upsert works
ALTER TABLE engagement_metrics ADD CONSTRAINT engagement_metrics_result_id_key UNIQUE (result_id);

-- Schedule engagement polling every 6 hours via pg_cron
-- Inserts a fetch_engagement job into job_queue
SELECT cron.schedule(
  'fetch_engagement',
  '0 */6 * * *',
  $$INSERT INTO job_queue (queue_name, job_type, payload, status)
    VALUES ('content_generation', 'fetch_engagement', '{}'::jsonb, 'queued')$$
);
