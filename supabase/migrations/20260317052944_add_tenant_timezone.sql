-- Add timezone column to tenants table
-- Defaults to UTC so existing tenants aren't broken
ALTER TABLE tenants ADD COLUMN timezone text NOT NULL DEFAULT 'UTC';
