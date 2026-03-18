-- Single dispatcher: runs every 5 minutes, checks which tenants are due
SELECT cron.schedule(
  'autopilot_dispatch',
  '*/5 * * * *',
  $$INSERT INTO job_queue (queue_name, job_type, payload, status)
    VALUES ('content_generation', 'autopilot_dispatch', '{}'::jsonb, 'queued')$$
);

-- Smart Queue timeout sweep: runs every 5 minutes
SELECT cron.schedule(
  'autopilot_timeout_sweep',
  '*/5 * * * *',
  $$INSERT INTO job_queue (queue_name, job_type, payload, status)
    VALUES ('content_generation', 'autopilot_timeout', '{}'::jsonb, 'queued')$$
);

-- Weekly digest: Sundays at 9am UTC
SELECT cron.schedule(
  'autopilot_weekly_digest',
  '0 9 * * 0',
  $$INSERT INTO job_queue (queue_name, job_type, payload, status)
    VALUES ('content_generation', 'autopilot_digest', '{}'::jsonb, 'queued')$$
);
