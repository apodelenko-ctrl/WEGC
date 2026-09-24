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

## Public activation continuation — 24 September 2026

The owner explicitly directed this task to enable public collection and continue the roadmap without repeated reports or questions. The public notice uses the already recorded controller/contact and 24-month contact retention, describes the actual unverified fields, and links to the separate public route. This supersedes the earlier pending activation instruction; it is not a claim of independent legal certification.

Migration 0008 adds atomic erasure of a request and all its replies/history. An operator must confirm the version and explicit erasure action; ordinary members cannot call it. A 31-day tombstone prevents receipt replay/recreation and backup resurrection. Existing immutable-event protections still reject unaudited deletes. Hourly retention removes cases inactive for two calendar years; the same erasure path is bounded at 1,000 records per run.

Before restoring any backup: keep public submissions paused; export the current erasure ledger separately, restore the selected backup, reapply all unexpired tombstones, run the erasure sweep and integrity checks, then restore service. Never restore a database while discarding the current tombstone ledger. Operational SQL exports containing public requests expire after 30 days and must be removed from the private backup store; earlier checkpoint exports in this task contain zero public request rows. Turnstile, Access and invitation settings must survive every deployment.


## Production activation, 2026-09-24

Explicit owner instruction to enable public intake was executed. Source f7e2a07, Worker version b5345fe9-ca05-479d-94f7-2f2bfd6498a8; migrations 0001–0008; public intake enabled and not paused, notice version mira-public-2026-09-24-v1; hourly retention enabled. A synthetic example.test enquiry passed the real managed Turnstile, was persisted and assigned to the existing operator, and received an operator reply visible in its private receipt. Reload and refresh preserved access. No real customer or buyer record was created. The operator and research routes remain protected.
