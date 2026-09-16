-- Dedicated MIRA database only. Never run against the existing wegc-leads DB.
PRAGMA foreign_keys = ON;
CREATE TABLE mira_agencies (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, city TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','active','suspended')),
 agreement_ref TEXT, created_at TEXT NOT NULL
);
CREATE TABLE mira_memberships (
 subject TEXT PRIMARY KEY, agency_id TEXT REFERENCES mira_agencies(id),
 role TEXT NOT NULL CHECK(role IN ('agency_owner','broker','operator')),
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
 CHECK((role='operator' AND agency_id IS NULL) OR (role!='operator' AND agency_id IS NOT NULL))
);
CREATE TABLE mira_projects (
 id TEXT PRIMARY KEY,name TEXT NOT NULL,market TEXT NOT NULL,developer_family TEXT,
 legal_seller TEXT,enabled INTEGER NOT NULL DEFAULT 0 CHECK(enabled IN (0,1)),
 agreement_ref TEXT,inventory_ref TEXT,registration_rules_ref TEXT,commission_schedule_ref TEXT,
 materials_rights_ref TEXT,updated_at TEXT NOT NULL
);
CREATE TABLE mira_agency_projects (
 agency_id TEXT NOT NULL REFERENCES mira_agencies(id),project_id TEXT NOT NULL REFERENCES mira_projects(id),
 PRIMARY KEY(agency_id,project_id)
);
CREATE TABLE mira_evidence (
 id TEXT PRIMARY KEY,kind TEXT NOT NULL,project_id TEXT REFERENCES mira_projects(id),
 agency_id TEXT REFERENCES mira_agencies(id),entity_id TEXT,storage_ref TEXT NOT NULL,
 facts_json TEXT NOT NULL DEFAULT '{}',
 verified INTEGER NOT NULL DEFAULT 0 CHECK(verified IN (0,1)),
 verified_by TEXT NOT NULL,verified_at TEXT NOT NULL,expires_at TEXT,revoked_at TEXT,
 CHECK(expires_at IS NULL OR expires_at>verified_at)
);
CREATE TABLE mira_applications (
 id TEXT PRIMARY KEY,subject TEXT NOT NULL,email TEXT NOT NULL,company TEXT NOT NULL,city TEXT NOT NULL,
 name TEXT NOT NULL,format TEXT NOT NULL,demand TEXT NOT NULL,markets_json TEXT NOT NULL,
 consent_version TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'received',created_at TEXT NOT NULL,
 idempotency_key TEXT NOT NULL,request_hash TEXT NOT NULL,UNIQUE(subject,idempotency_key)
);
CREATE TABLE mira_leads (
 id TEXT PRIMARY KEY,agency_id TEXT NOT NULL REFERENCES mira_agencies(id),
 project_id TEXT NOT NULL REFERENCES mira_projects(id),client_ref TEXT NOT NULL,consent_ref TEXT NOT NULL,
 created_by TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'submitted' CHECK(status IN ('submitted','review','needs_information','developer_submitted','developer_confirmed','duplicate','conflict','rejected','expired','closed')),
 version INTEGER NOT NULL DEFAULT 0,protection_ref TEXT,protection_until TEXT,last_event_id TEXT NOT NULL,
 UNIQUE(agency_id,project_id,client_ref)
);
CREATE TABLE mira_events (
 id TEXT PRIMARY KEY,entity_type TEXT NOT NULL,entity_id TEXT NOT NULL,agency_id TEXT,
 actor TEXT NOT NULL,status TEXT NOT NULL,version INTEGER NOT NULL,evidence_ref TEXT,reason TEXT NOT NULL,
 created_at TEXT NOT NULL,UNIQUE(entity_type,entity_id,version)
);
CREATE TRIGGER mira_events_no_update BEFORE UPDATE ON mira_events BEGIN SELECT RAISE(ABORT,'audit_events_are_immutable'); END;
CREATE TRIGGER mira_events_no_delete BEFORE DELETE ON mira_events BEGIN SELECT RAISE(ABORT,'audit_events_are_immutable'); END;
CREATE TABLE mira_payment_requests (
 id TEXT PRIMARY KEY,lead_id TEXT NOT NULL REFERENCES mira_leads(id),agency_id TEXT NOT NULL REFERENCES mira_agencies(id),
 created_by TEXT NOT NULL,created_at TEXT NOT NULL,invoice_currency TEXT NOT NULL,
 consent_ref TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'package_review',version INTEGER NOT NULL DEFAULT 0,
 UNIQUE(lead_id)
);
CREATE TABLE mira_deal_events (
 id TEXT PRIMARY KEY,lead_id TEXT NOT NULL REFERENCES mira_leads(id),agency_id TEXT NOT NULL REFERENCES mira_agencies(id),
 sequence INTEGER NOT NULL,stage TEXT NOT NULL,evidence_ref TEXT NOT NULL,
 amount_decimal TEXT,currency TEXT,actor TEXT NOT NULL,created_at TEXT NOT NULL,
 UNIQUE(lead_id,sequence),UNIQUE(lead_id,stage),
 CHECK((amount_decimal IS NULL AND currency IS NULL) OR (amount_decimal IS NOT NULL AND currency IS NOT NULL))
);
CREATE TRIGGER mira_deals_no_update BEFORE UPDATE ON mira_deal_events BEGIN SELECT RAISE(ABORT,'deal_events_are_immutable'); END;
CREATE TRIGGER mira_deals_no_delete BEFORE DELETE ON mira_deal_events BEGIN SELECT RAISE(ABORT,'deal_events_are_immutable'); END;
CREATE INDEX mira_leads_agency_cursor ON mira_leads(agency_id,id);
CREATE INDEX mira_events_entity ON mira_events(entity_type,entity_id,version);
CREATE INDEX mira_applications_subject ON mira_applications(subject,id);

CREATE TABLE mira_rate_limits (subject TEXT NOT NULL,bucket INTEGER NOT NULL,uses INTEGER NOT NULL,PRIMARY KEY(subject,bucket));
CREATE TRIGGER mira_evidence_immutable BEFORE UPDATE ON mira_evidence
WHEN NEW.id IS NOT OLD.id OR NEW.kind IS NOT OLD.kind OR NEW.project_id IS NOT OLD.project_id OR NEW.agency_id IS NOT OLD.agency_id OR NEW.entity_id IS NOT OLD.entity_id OR NEW.storage_ref IS NOT OLD.storage_ref OR NEW.facts_json IS NOT OLD.facts_json OR NEW.verified IS NOT OLD.verified OR NEW.verified_by IS NOT OLD.verified_by OR NEW.verified_at IS NOT OLD.verified_at OR NEW.expires_at IS NOT OLD.expires_at OR (OLD.revoked_at IS NOT NULL AND NEW.revoked_at IS NOT OLD.revoked_at)
BEGIN SELECT RAISE(ABORT,'evidence_immutable_except_first_revocation'); END;
CREATE TRIGGER mira_evidence_no_delete BEFORE DELETE ON mira_evidence BEGIN SELECT RAISE(ABORT,'evidence_is_immutable'); END;
