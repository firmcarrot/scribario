-- Phase 1B: Usage Events Enrichment

ALTER TABLE usage_events
  ADD COLUMN request_id uuid,
  ADD COLUMN input_tokens integer,
  ADD COLUMN output_tokens integer,
  ADD COLUMN model text;

CREATE INDEX idx_usage_events_request ON usage_events(request_id)
  WHERE request_id IS NOT NULL;
CREATE INDEX idx_usage_events_provider_month ON usage_events(provider, created_at DESC);
