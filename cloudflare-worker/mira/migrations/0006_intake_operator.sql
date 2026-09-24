-- Additive companion to the prepared 0005; not applied to production by this release.
ALTER TABLE mira_intake_events ADD COLUMN event_kind TEXT NOT NULL DEFAULT 'review';
ALTER TABLE mira_intake_events ADD COLUMN assigned_subject TEXT;
ALTER TABLE mira_intake_events ADD COLUMN response_published INTEGER NOT NULL DEFAULT 0 CHECK(response_published IN (0,1));
DROP TRIGGER mira_intake_payload_immutable;
CREATE TRIGGER mira_intake_payload_immutable BEFORE UPDATE ON mira_intake_requests
WHEN NEW.id IS NOT OLD.id OR NEW.idempotency_key IS NOT OLD.idempotency_key
 OR NEW.request_hash IS NOT OLD.request_hash OR NEW.token_hash IS NOT OLD.token_hash
 OR NEW.company IS NOT OLD.company OR NEW.city IS NOT OLD.city OR NEW.name IS NOT OLD.name
 OR NEW.email IS NOT OLD.email OR NEW.consent_version IS NOT OLD.consent_version
 OR NEW.email_verified IS NOT OLD.email_verified OR NEW.created_at IS NOT OLD.created_at
BEGIN SELECT RAISE(ABORT,'intake_payload_immutable'); END;
CREATE TRIGGER mira_intake_assignment_operator_required BEFORE UPDATE OF assigned_subject ON mira_intake_requests
WHEN NEW.assigned_subject IS NOT OLD.assigned_subject AND NOT EXISTS
 (SELECT 1 FROM mira_memberships WHERE subject=NEW.assigned_subject AND role='operator' AND active=1)
BEGIN SELECT RAISE(ABORT,'active_intake_operator_required'); END;
CREATE TRIGGER mira_intake_version_progress BEFORE UPDATE ON mira_intake_requests
WHEN (NEW.assigned_subject IS NOT OLD.assigned_subject OR NEW.status IS NOT OLD.status
 OR NEW.public_response IS NOT OLD.public_response OR NEW.version IS NOT OLD.version
 OR NEW.updated_at IS NOT OLD.updated_at OR NEW.last_event_id IS NOT OLD.last_event_id)
 AND (NEW.version != OLD.version+1 OR NEW.last_event_id IS OLD.last_event_id)
BEGIN SELECT RAISE(ABORT,'intake_version_progress_required'); END;
