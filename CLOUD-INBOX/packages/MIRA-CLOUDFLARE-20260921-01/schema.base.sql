-- Additive research staging only. Existing MIRA operational tables are not mutated.
-- Precondition: the dedicated MIRA schema exists (never apply to wegc-leads).
SELECT id, status FROM mira_applications LIMIT 0;
SELECT subject, role FROM mira_memberships LIMIT 0;
PRAGMA foreign_keys = ON;

CREATE TABLE mira_import_snapshots (
 id TEXT PRIMARY KEY, source_commit TEXT NOT NULL,
 source_manifest_json TEXT NOT NULL CHECK(json_valid(source_manifest_json)),
 expected_json TEXT NOT NULL CHECK(json_valid(expected_json)),
 contains_private INTEGER NOT NULL CHECK(contains_private IN (0,1))
);
CREATE TABLE mira_research_entities (
 snapshot_id TEXT NOT NULL REFERENCES mira_import_snapshots(id),
 kind TEXT NOT NULL CHECK(kind IN ('agency','developer')),
 source_id TEXT NOT NULL, name TEXT NOT NULL, city TEXT, market TEXT, segment TEXT,
 row_json TEXT NOT NULL CHECK(json_valid(row_json)), row_sha256 TEXT NOT NULL,
 PRIMARY KEY(snapshot_id,kind,source_id)
);
CREATE TABLE mira_research_aliases (
 snapshot_id TEXT NOT NULL, kind TEXT NOT NULL, alias_id TEXT NOT NULL, source_id TEXT NOT NULL,
 PRIMARY KEY(snapshot_id,kind,alias_id,source_id),
 FOREIGN KEY(snapshot_id,kind,source_id) REFERENCES mira_research_entities(snapshot_id,kind,source_id)
);
CREATE TABLE mira_research_fields (
 snapshot_id TEXT NOT NULL, kind TEXT NOT NULL, source_id TEXT NOT NULL,
 field_key TEXT NOT NULL, occurrence INTEGER NOT NULL,
 value_json TEXT NOT NULL CHECK(json_valid(value_json)),
 evidence_json TEXT NOT NULL CHECK(json_valid(evidence_json)),
 verification_status TEXT NOT NULL, conversation_scope TEXT NOT NULL,
 PRIMARY KEY(snapshot_id,kind,source_id,field_key,occurrence),
 FOREIGN KEY(snapshot_id,kind,source_id) REFERENCES mira_research_entities(snapshot_id,kind,source_id)
);
CREATE TABLE mira_research_project_links (
 snapshot_id TEXT NOT NULL REFERENCES mira_import_snapshots(id),
 market TEXT NOT NULL, project_id TEXT NOT NULL,
 developer_kind TEXT NOT NULL DEFAULT 'developer' CHECK(developer_kind='developer'),
 developer_id TEXT, mapping_status TEXT NOT NULL,
 row_json TEXT NOT NULL CHECK(json_valid(row_json)), row_sha256 TEXT NOT NULL,
 PRIMARY KEY(snapshot_id,market,project_id),
 FOREIGN KEY(snapshot_id,developer_kind,developer_id) REFERENCES mira_research_entities(snapshot_id,kind,source_id)
);
CREATE TABLE mira_native_lineage (
 snapshot_id TEXT NOT NULL REFERENCES mira_import_snapshots(id),
 crm_account_id TEXT NOT NULL, native_external_id TEXT NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN ('agency','developer')),
 mapping_status TEXT NOT NULL, resolved_source_id TEXT,
 row_json TEXT NOT NULL CHECK(json_valid(row_json)), row_sha256 TEXT NOT NULL,
 PRIMARY KEY(snapshot_id,crm_account_id), UNIQUE(snapshot_id,native_external_id),
 FOREIGN KEY(snapshot_id,kind,resolved_source_id) REFERENCES mira_research_entities(snapshot_id,kind,source_id)
);
CREATE TABLE mira_import_commits (
 snapshot_id TEXT PRIMARY KEY REFERENCES mira_import_snapshots(id)
);
CREATE TRIGGER mira_import_commit_complete BEFORE INSERT ON mira_import_commits
WHEN NOT EXISTS (
 SELECT 1 FROM mira_import_snapshots s WHERE s.id=NEW.snapshot_id
 AND json_extract(s.expected_json,'$.entities')=(SELECT count(*) FROM mira_research_entities WHERE snapshot_id=s.id)
 AND json_extract(s.expected_json,'$.aliases')=(SELECT count(*) FROM mira_research_aliases WHERE snapshot_id=s.id)
 AND json_extract(s.expected_json,'$.fields')=(SELECT count(*) FROM mira_research_fields WHERE snapshot_id=s.id)
 AND json_extract(s.expected_json,'$.project_links')=(SELECT count(*) FROM mira_research_project_links WHERE snapshot_id=s.id)
 AND json_extract(s.expected_json,'$.native_lineage')=(SELECT count(*) FROM mira_native_lineage WHERE snapshot_id=s.id)
) BEGIN SELECT RAISE(ABORT,'incomplete_import_snapshot'); END;

CREATE VIEW mira_research_summary AS
 SELECT s.id AS snapshot_id,s.source_commit,s.contains_private,
 (SELECT count(*) FROM mira_research_entities e WHERE e.snapshot_id=s.id AND e.kind='agency') AS agency_candidates,
 (SELECT count(*) FROM mira_research_entities e WHERE e.snapshot_id=s.id AND e.kind='developer') AS developer_groups,
 (SELECT count(*) FROM mira_research_project_links p WHERE p.snapshot_id=s.id) AS research_project_links,
 (SELECT count(*) FROM mira_native_lineage n WHERE n.snapshot_id=s.id) AS native_lineage_rows
 FROM mira_import_snapshots s JOIN mira_import_commits c ON c.snapshot_id=s.id;
CREATE VIEW mira_published_research_entities AS
 SELECT e.* FROM mira_research_entities e JOIN mira_import_commits c ON c.snapshot_id=e.snapshot_id;
CREATE INDEX mira_research_city ON mira_research_entities(snapshot_id,kind,city,source_id);
CREATE INDEX mira_research_field ON mira_research_fields(snapshot_id,kind,field_key,verification_status);
