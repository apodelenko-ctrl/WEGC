-- Newest requests first with stable timestamp/id pagination.
CREATE INDEX mira_intake_received_order ON mira_intake_requests(created_at DESC,id DESC);
