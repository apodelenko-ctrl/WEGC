-- Additive migration; apply after 0001 to the dedicated MIRA database only.
-- Existing records retain their original receipt time; no historical approvals are fabricated.
ALTER TABLE mira_applications ADD COLUMN version INTEGER NOT NULL DEFAULT 0;
ALTER TABLE mira_applications ADD COLUMN agency_id TEXT REFERENCES mira_agencies(id);
ALTER TABLE mira_applications ADD COLUMN updated_at TEXT;
ALTER TABLE mira_applications ADD COLUMN last_event_id TEXT;
UPDATE mira_applications SET updated_at=created_at WHERE updated_at IS NULL;
ALTER TABLE mira_leads ADD COLUMN idempotency_key TEXT;
ALTER TABLE mira_leads ADD COLUMN request_hash TEXT;
CREATE UNIQUE INDEX mira_lead_attempt ON mira_leads(created_by,idempotency_key) WHERE idempotency_key IS NOT NULL;
ALTER TABLE mira_events ADD COLUMN owner_approval_ref TEXT;
CREATE INDEX mira_application_status ON mira_applications(status,created_at);
