CREATE TYPE support_ticket_category AS ENUM ('bug', 'idea');
CREATE TYPE support_ticket_status AS ENUM ('open', 'in_progress', 'resolved');

CREATE SEQUENCE support_ticket_seq START 1;

-- Wrapper function for ticket number generation (Postgres DEFAULT requires a function, not an expression)
CREATE OR REPLACE FUNCTION next_ticket_number() RETURNS text AS $$
BEGIN
  RETURN 'SC-' || lpad(nextval('support_ticket_seq')::text, 5, '0');
END;
$$ LANGUAGE plpgsql;

CREATE TABLE support_tickets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  ticket_number text NOT NULL UNIQUE DEFAULT next_ticket_number(),
  category support_ticket_category NOT NULL,
  description text NOT NULL,
  status support_ticket_status NOT NULL DEFAULT 'open',
  creator_telegram_user_id bigint NOT NULL,
  creator_telegram_chat_id bigint NOT NULL,
  admin_response text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;
CREATE POLICY service_only ON support_tickets FOR ALL USING (false);

CREATE INDEX idx_support_tickets_number ON support_tickets(ticket_number);
CREATE INDEX idx_support_tickets_tenant ON support_tickets(tenant_id);

-- updated_at trigger (plain PL/pgSQL — moddatetime extension not available)
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER support_tickets_updated_at BEFORE UPDATE ON support_tickets
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
