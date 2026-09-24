# Public intake release — 24 September 2026

This release prepares the operator inbox behind the existing Access + active-operator checks. Deploy with public intake disabled. An enquiry never verifies an email, creates a membership, activates an agency, or registers a buyer with a developer.

## Configuration

Keep invitation settings `PRIVACY_VERSION`, `PRIVACY_NOTICE_URL` and `APPLICATIONS_ENABLED` unchanged. Public intake requires its own `PUBLIC_INTAKE_PRIVACY_VERSION` and same-origin `PUBLIC_INTAKE_PRIVACY_NOTICE_URL`; there is deliberately no fallback to the invitation policy.

- `PUBLIC_INTAKE_ENABLED=false`: complete public-route shutdown; operator inbox remains available.
- `PUBLIC_INTAKE_SUBMISSIONS_PAUSED=true`: when public intake is enabled, stop new submissions but keep receipt lookup, published replies and exact idempotent replay available. An offline assignee does not block the paused receipt page.
- `PUBLIC_INTAKE_PRIVACY_APPROVED=false`: keep false until the actual public enquiry notice and data handling are approved; a deployment switch is not approval evidence.
- `INTAKE_OPERATOR_SUBJECT`: existing active operator subject only. No membership provisioning.
- `TURNSTILE_SITE_KEY`: widget restricted to the deployment hostname; server checks hostname and `mira_intake` action. `TURNSTILE_SECRET_KEY` and a random `INTAKE_RATE_SECRET` of at least 32 characters are Worker secrets.

The operator view is `/mira/api/admin/intake/view`. Queue pagination uses newest timestamp first, then UUID as a stable tie-breaker. The summary refreshes every 30 seconds while the tab is visible; it does not replace an unsaved reply. This is an in-tab indicator, not an email/push service or an operator-shift guarantee.

## Database and deployment

Export the current D1 database privately, restore it to local D1, then apply migrations 0005–0007. Compare all existing table contents and schema objects and run integrity/foreign-key checks before applying the same additive migrations remotely. Do not recreate the database or reimport research migration 0004. Migration 0007 adds only the queue ordering index.

Build the explicit pilot asset allowlist. Run the API, site, research, public intake and client tests. Dry-run the Worker bundle. Deploy the known configuration with `--keep-vars` and explicit disabled/paused/unapproved public flags so existing invitation and Access variables survive. Verify actual settings, migration history, protected browser view and anonymous rejection after deployment.

Previous live Worker version: `09782ef9-f0a0-445a-b3ea-2d173af2c0eb`. A Worker rollback retains additive intake tables. Do not roll back or overwrite the database merely to roll back code. Recheck privacy/invitation switches and Access policy after any rollback.

## Outstanding public launch evidence

Public intake cannot be called ready until there is an approved notice specifically covering unverified contact data, a retention/deletion procedure covering immutable events and backups, real Turnstile acceptance, an actual operator response rehearsal, and the printed QR/mobile test. Current immutable event triggers intentionally reject deletion and are not a finished erasure workflow. No retention period, deletion policy, availability, commission, media rights, lead protection or operator SLA is invented by this release.
