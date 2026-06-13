-- WEGC leads (mini-CRM) — one row per Telegram conversation.
CREATE TABLE IF NOT EXISTS leads (
  chat_id      TEXT PRIMARY KEY,
  created_at   TEXT,
  updated_at   TEXT,
  name         TEXT,
  username     TEXT,
  lang         TEXT,
  status       TEXT DEFAULT 'new',   -- new | handed_off
  goal         TEXT,
  budget       TEXT,
  district     TEXT,
  timeline     TEXT,
  property_type TEXT,
  interested_projects TEXT,
  summary      TEXT,
  msg_count    INTEGER DEFAULT 0,
  transcript   TEXT                   -- JSON array of {role, content}
);
CREATE INDEX IF NOT EXISTS idx_leads_updated ON leads(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
