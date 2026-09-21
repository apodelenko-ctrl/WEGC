-- READ ONLY. Execute in existing mira-pilot Console or through authorized D1 tools.
-- Return schema and counts only; do not export application/contact payloads to public Git.
SELECT name,type,sql FROM sqlite_master
 WHERE name LIKE 'mira_%' OR name='d1_migrations' ORDER BY type,name;
SELECT 'mira_agencies' AS entity,count(*) AS rows FROM mira_agencies
 UNION ALL SELECT 'mira_projects',count(*) FROM mira_projects
 UNION ALL SELECT 'mira_applications',count(*) FROM mira_applications
 UNION ALL SELECT 'mira_memberships',count(*) FROM mira_memberships
 UNION ALL SELECT 'mira_leads',count(*) FROM mira_leads;
