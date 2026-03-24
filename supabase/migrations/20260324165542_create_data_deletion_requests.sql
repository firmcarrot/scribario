CREATE TABLE data_deletion_requests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  platform text NOT NULL DEFAULT 'meta',
  platform_user_id text NOT NULL,
  confirmation_code text NOT NULL,
  status text NOT NULL DEFAULT 'pending',
  processed_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE data_deletion_requests ENABLE ROW LEVEL SECURITY;
CREATE POLICY service_only ON data_deletion_requests FOR ALL USING (false);

CREATE INDEX idx_data_deletion_confirmation ON data_deletion_requests(confirmation_code);
