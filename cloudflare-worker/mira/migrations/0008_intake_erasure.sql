-- No contact fields or reply text in the short-lived erasure ledger.
CREATE TABLE mira_intake_erasure (
 request_id TEXT PRIMARY KEY,
 idempotency_key TEXT NOT NULL UNIQUE,
 token_hash TEXT NOT NULL,
 actor TEXT NOT NULL,
 reason TEXT NOT NULL CHECK(reason IN ('request','retention')),
 erased_at TEXT NOT NULL,
 expires_at TEXT NOT NULL
);
CREATE INDEX mira_intake_erasure_expiry ON mira_intake_erasure(expires_at);
DROP TRIGGER mira_intake_events_no_delete;
CREATE TRIGGER mira_intake_events_no_delete BEFORE DELETE ON mira_intake_events
WHEN NOT EXISTS(SELECT 1 FROM mira_intake_erasure WHERE request_id=OLD.request_id)
BEGIN SELECT RAISE(ABORT,'intake_events_immutable'); END;
CREATE TRIGGER mira_intake_request_no_delete BEFORE DELETE ON mira_intake_requests
WHEN NOT EXISTS(SELECT 1 FROM mira_intake_erasure WHERE request_id=OLD.id)
BEGIN SELECT RAISE(ABORT,'intake_erasure_record_required'); END;
CREATE TRIGGER mira_intake_erasure_no_update BEFORE UPDATE ON mira_intake_erasure
BEGIN SELECT RAISE(ABORT,'intake_erasure_immutable'); END;
CREATE TRIGGER mira_intake_erasure_no_early_delete BEFORE DELETE ON mira_intake_erasure
WHEN julianday(OLD.expires_at)>julianday('now')
BEGIN SELECT RAISE(ABORT,'intake_erasure_retention'); END;
CREATE TRIGGER mira_intake_erased_key_no_reuse BEFORE INSERT ON mira_intake_requests
WHEN EXISTS(SELECT 1 FROM mira_intake_erasure WHERE request_id=NEW.id OR idempotency_key=NEW.idempotency_key)
BEGIN SELECT RAISE(ABORT,'intake_erased_key'); END;
