SELECT type AS kind, name, COALESCE(sql, '') AS detail
FROM sqlite_master
WHERE type IN ('index', 'trigger', 'view')
  AND (tbl_name LIKE 'mira_%' OR name LIKE 'mira_%')
UNION ALL
SELECT 'migration', name, CAST(applied_at AS TEXT) FROM d1_migrations
UNION ALL SELECT 'count','mira_agencies',CAST(COUNT(*) AS TEXT) FROM mira_agencies
UNION ALL SELECT 'count','mira_agency_projects',CAST(COUNT(*) AS TEXT) FROM mira_agency_projects
UNION ALL SELECT 'count','mira_applications',CAST(COUNT(*) AS TEXT) FROM mira_applications
UNION ALL SELECT 'count','mira_deal_events',CAST(COUNT(*) AS TEXT) FROM mira_deal_events
UNION ALL SELECT 'count','mira_events',CAST(COUNT(*) AS TEXT) FROM mira_events
UNION ALL SELECT 'count','mira_evidence',CAST(COUNT(*) AS TEXT) FROM mira_evidence
UNION ALL SELECT 'count','mira_leads',CAST(COUNT(*) AS TEXT) FROM mira_leads
UNION ALL SELECT 'count','mira_material_access',CAST(COUNT(*) AS TEXT) FROM mira_material_access
UNION ALL SELECT 'count','mira_materials',CAST(COUNT(*) AS TEXT) FROM mira_materials
UNION ALL SELECT 'count','mira_memberships',CAST(COUNT(*) AS TEXT) FROM mira_memberships
UNION ALL SELECT 'count','mira_payment_requests',CAST(COUNT(*) AS TEXT) FROM mira_payment_requests
UNION ALL SELECT 'count','mira_projects',CAST(COUNT(*) AS TEXT) FROM mira_projects
UNION ALL SELECT 'count','mira_rate_limits',CAST(COUNT(*) AS TEXT) FROM mira_rate_limits
ORDER BY kind, name;
