SELECT
  (SELECT COUNT(*) FROM mira_agencies) AS mira_agencies,
  (SELECT COUNT(*) FROM mira_agency_projects) AS mira_agency_projects,
  (SELECT COUNT(*) FROM mira_applications) AS mira_applications,
  (SELECT COUNT(*) FROM mira_deal_events) AS mira_deal_events,
  (SELECT COUNT(*) FROM mira_events) AS mira_events,
  (SELECT COUNT(*) FROM mira_evidence) AS mira_evidence,
  (SELECT COUNT(*) FROM mira_leads) AS mira_leads,
  (SELECT COUNT(*) FROM mira_material_access) AS mira_material_access,
  (SELECT COUNT(*) FROM mira_materials) AS mira_materials,
  (SELECT COUNT(*) FROM mira_memberships) AS mira_memberships,
  (SELECT COUNT(*) FROM mira_payment_requests) AS mira_payment_requests,
  (SELECT COUNT(*) FROM mira_projects) AS mira_projects,
  (SELECT COUNT(*) FROM mira_rate_limits) AS mira_rate_limits,
  (SELECT json_group_array(json_object('type', type, 'name', name, 'sql', sql))
   FROM sqlite_master
   WHERE type IN ('index', 'trigger', 'view')
     AND (tbl_name LIKE 'mira_%' OR name LIKE 'mira_%')) AS schema_objects,
  (SELECT json_group_array(json_object('name', name, 'applied_at', applied_at))
   FROM d1_migrations) AS migrations;
