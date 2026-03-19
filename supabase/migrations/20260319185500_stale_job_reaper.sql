-- Stale job reaper: recovers orphaned "processing" jobs when worker crashes
-- Runs every 10 minutes, catches any job stuck for 15+ minutes

CREATE OR REPLACE FUNCTION reap_stale_jobs() RETURNS void AS $$
BEGIN
  UPDATE job_queue
  SET
    status = CASE WHEN retry_count < max_retries THEN 'queued' ELSE 'dead' END,
    retry_count = CASE WHEN retry_count < max_retries THEN retry_count + 1 ELSE retry_count END,
    locked_by = NULL,
    error_message = COALESCE(error_message || ' | ', '') || 'stale: restarted by reaper at ' || now()::text,
    failed_at = CASE WHEN retry_count >= max_retries THEN now() ELSE failed_at END
  WHERE status = 'processing'
    AND created_at < now() - interval '15 minutes';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

SELECT cron.schedule(
  'reap_stale_jobs',
  '*/10 * * * *',
  'SELECT reap_stale_jobs()'
);
