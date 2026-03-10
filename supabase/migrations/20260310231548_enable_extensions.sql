-- Enable pgmq for durable job queuing
CREATE EXTENSION IF NOT EXISTS pgmq;

-- Enable pg_cron for scheduled content generation
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Enable pg_net for async HTTP from postgres (useful for webhooks)
CREATE EXTENSION IF NOT EXISTS pg_net;
