-- Additive, deliberately independent of optional research migration 0004.
-- Apply only to existing MIRA_DB after backup and isolated D1 acceptance.
CREATE TABLE mira_intake_requests (
 id TEXT PRIMARY KEY,
 idempotency_key TEXT NOT NULL UNIQUE,
 request_hash TEXT NOT NULL,
 token_hash TEXT NOT NULL,
 company TEXT NOT NULL, city TEXT NOT NULL, name TEXT NOT NULL, email TEXT NOT NULL,
 consent_version TEXT NOT NULL,
 email_verified INTEGER NOT NULL DEFAULT 0 CHECK(email_verified=0),
 assigned_subject TEXT NOT NULL REFERENCES mira_memberships(subject),
 status TEXT NOT NULL DEFAULT 'received' CHECK(status IN ('received','review','needs_information','responded','closed')),
 public_response TEXT,
 version INTEGER NOT NULL DEFAULT 0,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL, last_event_id TEXT NOT NULL
);
CREATE INDEX mira_intake_queue ON mira_intake_requests(assigned_subject,status,id);
CREATE TABLE mira_intake_events (
 id TEXT PRIMARY KEY, request_id TEXT NOT NULL REFERENCES mira_intake_requests(id),
 actor TEXT NOT NULL, status TEXT NOT NULL, version INTEGER NOT NULL,
 public_response TEXT, created_at TEXT NOT NULL,
 UNIQUE(request_id,version)
);
CREATE TABLE mira_intake_limits (
 subject_hash TEXT NOT NULL, bucket INTEGER NOT NULL, uses INTEGER NOT NULL,
 PRIMARY KEY(subject_hash,bucket)
);
CREATE TRIGGER mira_intake_operator_required BEFORE INSERT ON mira_intake_requests
WHEN NOT EXISTS(SELECT 1 FROM mira_memberships WHERE subject=NEW.assigned_subject AND role='operator' AND active=1)
BEGIN SELECT RAISE(ABORT,'active_intake_operator_required'); END;
CREATE TRIGGER mira_intake_payload_immutable BEFORE UPDATE ON mira_intake_requests
WHEN NEW.id IS NOT OLD.id OR NEW.idempotency_key IS NOT OLD.idempotency_key
 OR NEW.request_hash IS NOT OLD.request_hash OR NEW.token_hash IS NOT OLD.token_hash
 OR NEW.company IS NOT OLD.company OR NEW.city IS NOT OLD.city OR NEW.name IS NOT OLD.name
 OR NEW.email IS NOT OLD.email OR NEW.consent_version IS NOT OLD.consent_version
 OR NEW.email_verified IS NOT OLD.email_verified OR NEW.created_at IS NOT OLD.created_at
 OR NEW.assigned_subject IS NOT OLD.assigned_subject
BEGIN SELECT RAISE(ABORT,'intake_payload_immutable'); END;
CREATE TRIGGER mira_intake_events_no_update BEFORE UPDATE ON mira_intake_events
BEGIN SELECT RAISE(ABORT,'intake_events_immutable'); END;
CREATE TRIGGER mira_intake_events_no_delete BEFORE DELETE ON mira_intake_events
BEGIN SELECT RAISE(ABORT,'intake_events_immutable'); END;
