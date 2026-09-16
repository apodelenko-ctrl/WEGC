-- Public source schema only. Assets stay in a NEW private R2 bucket.
-- Material delivery is internal agency use; it never grants buyer redistribution.
CREATE TABLE mira_materials (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES mira_projects(id),
  title TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('brochure','floor_plan','field_report','training')),
  language TEXT NOT NULL CHECK (language IN ('ru','en','th')),
  mime_type TEXT NOT NULL CHECK (mime_type IN ('application/pdf','image/png','image/jpeg','image/webp')),
  size_bytes INTEGER NOT NULL CHECK (size_bytes > 0 AND size_bytes <= 8388608),
  sha256 TEXT NOT NULL CHECK (length(sha256)=64),
  rights_ref TEXT NOT NULL REFERENCES mira_evidence(id),
  release_ref TEXT NOT NULL REFERENCES mira_evidence(id),
  expires_at TEXT NOT NULL,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  revoked_at TEXT
);
CREATE INDEX mira_materials_project ON mira_materials(project_id,id);
CREATE TRIGGER mira_materials_version_immutable BEFORE UPDATE ON mira_materials
WHEN OLD.id IS NOT NEW.id OR OLD.project_id IS NOT NEW.project_id
 OR OLD.title IS NOT NEW.title OR OLD.kind IS NOT NEW.kind
 OR OLD.language IS NOT NEW.language OR OLD.mime_type IS NOT NEW.mime_type
 OR OLD.size_bytes IS NOT NEW.size_bytes OR OLD.sha256 IS NOT NEW.sha256
 OR OLD.rights_ref IS NOT NEW.rights_ref OR OLD.release_ref IS NOT NEW.release_ref
 OR OLD.expires_at IS NOT NEW.expires_at OR OLD.created_by IS NOT NEW.created_by
 OR OLD.created_at IS NOT NEW.created_at
 OR (OLD.revoked_at IS NOT NULL AND OLD.revoked_at IS NOT NEW.revoked_at)
BEGIN SELECT RAISE(ABORT,'immutable material version'); END;
CREATE TRIGGER mira_materials_no_delete BEFORE DELETE ON mira_materials
BEGIN SELECT RAISE(ABORT,'material must be revoked'); END;
CREATE TABLE mira_material_access (
  id TEXT PRIMARY KEY,
  material_id TEXT NOT NULL REFERENCES mira_materials(id),
  agency_id TEXT REFERENCES mira_agencies(id),
  actor TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  served_at TEXT NOT NULL
);
CREATE TRIGGER mira_material_access_no_update BEFORE UPDATE ON mira_material_access
BEGIN SELECT RAISE(ABORT,'immutable material access event'); END;
CREATE TRIGGER mira_material_access_no_delete BEFORE DELETE ON mira_material_access
BEGIN SELECT RAISE(ABORT,'immutable material access event'); END;
