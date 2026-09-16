# MIRA protected pilot API

**Code and offline tests, not a deployment claim.** Dedicated Worker + D1. No external outreach, Telegram, email, payment execution or third-party form submissions. The only outbound network call in this Worker is the pinned Cloudflare Access public-key endpoint for identity verification.

## Architecture and boundary

Public `/mira/marketplace.html` remains a separate demo. `/mira/pilot.html` uses same-origin protected endpoints and never substitutes demo data when the API is unavailable. No browser bearer-token storage or invented login.

JWT identity is verified against the configured issuer, audience and RS256 signature; user identity comes from signed subject/email claims, not plain email headers. Active server-side membership controls agency-owner, broker and operator scope. Brokers only see their own lead records; other agencies receive no record. Operator provisioning is bootstrap-only.

Real applications are disabled by default and require verified Access, approved same-origin privacy notice/version, JSON plus exact Origin, bounded payload, per-identity quota and idempotency key. A durable receipt means received, never contracted or activated.

Lead registration requires an active agency agreement, explicit project assignment, seller matching project-agreement evidence, current project agreement, expiring inventory evidence, registration rules, commission schedule and client-consent evidence scoped to agency/project/client reference. Client identity remains in the agency CRM; this API uses internal IDs and opaque evidence references, not passports, buyer contacts, invoices or banking credentials.

Versioned operator transitions append audit records. Developer submission requires a separately recorded owner-approval reference; the API itself sends nothing. Developer acknowledgement and lead protection are distinct. Protection dates must exactly match current evidence. Metadata and lead/deal events are immutable; evidence can be revoked with an audit event. Human review is still necessary: the registry is not an automated document-authenticity certification.

Payment-support requests are separate, not quotes or execution. Financial events accept exact decimal strings and require matching amount/currency in reviewed evidence. No price, FX, income forecast or default 90/10 split is inferred. The MVP ledger is ordered and same-currency, not a full accounting system.

## Owner-controlled deployment gate — not performed

1. Connect the correct Cloudflare account/zone and approve configuration. Do not guess account ID, team domain, audience or database ID.
2. Create a **new MIRA D1 database**. Copy `wrangler.example.toml` to ignored `wrangler.toml`; populate actual binding and top-level route values. Never migrate `wegc-leads` or change its Telegram relay.
3. Apply the ordered SQL migrations (`0001`, then `0002`) to the new database using authorized migration tooling. Review schema first.
4. Protect BOTH `/mira/pilot.html` and `/mira/api/*` with the same Access application and explicit allowlist. Configure exact HTTPS team domain and actual audience tag.
5. Bootstrap the first operator via owner-controlled database administration using the verified Access subject, `agency_id=NULL`, `role='operator'`. No guessed subject or email-header identity.
6. Approve actual privacy information: controller/contact, purpose, collected fields, processors/location, access, retention/deletion and international-data arrangements as applicable. Populate privacy version/URL only after review. Keep `APPLICATIONS_ENABLED=false` until then.
7. Create the real agency as pending, record reviewed agreement, activate it and bind verified user subjects. Create the project disabled, record current evidence, then enable and assign it. Never put test fixtures into production.
8. Test live authorization, cross-tenant rejection, receipt/retry, broker isolation, evidence expiry/revocation, version conflict, audit trail and API-unavailable fallback. Only then mark deployment verified.
9. Configure approved edge rate limits, session policy, backups and retention operations. The example application quota is a configurable abuse-control policy, not a business forecast. Plan cleanup of quota buckets.
10. Keep raw agreements, client documents, secrets and signed storage URLs in a protected vault. **WEGC is a public repository**; website exclusions do not make GitHub private.

## API surface

Prefix `/mira/api`. All except read-only health require verified Access; business records additionally require active membership.

| Method/path | Role | Result |
|---|---|---|
| GET `/health` | Read-only | Configuration signal, not readiness |
| GET `/session` | Verified Access | Own identity/membership |
| GET/POST `/applications` | Verified Access | Own queue / durable audited intake receipt |
| GET `/applications/:id` | Applicant | Own status history even before agency access |
| GET `/admin/applications/:id` | Operator | Review context and allowed next stages |
| POST `/admin/applications/:id/status` | Operator | Versioned, audited qualification/onboarding |
| GET `/profile` | Active member | Own agency/role and assigned markets, not activation |
| GET `/projects` | Active member | Assigned metadata |
| GET `/projects/:id` | Scoped member | Live evidence checks and timestamps; no raw vault references |
| GET/POST `/leads` | Active member | Scoped list / evidence-gated intake |
| GET `/leads/:id` | Scoped member | Lead, history, separate deal/payment records |
| POST `/payment-requests` | Scoped member | Package-review request, no execution |
| GET `/admin/applications` | Operator | Paginated intake queue |
| GET `/admin/dashboard` | Operator | Observed database counts, not mixed-currency totals |
| POST `/admin/agencies` | Operator | Pending/active/suspended with agreement gate |
| POST `/admin/projects` | Operator | Disabled creation / evidence-gated enablement |
| POST `/admin/memberships` | Operator | Owner/broker binding, no operator promotion/demotion |
| POST `/admin/agency-projects` | Operator | Explicit assignment |
| POST `/admin/evidence` | Operator | Reviewed opaque vault-reference metadata |
| POST `/admin/evidence/:id/revoke` | Operator | Audited revocation |
| POST `/admin/leads/:id/status` | Operator | Valid transition, evidence and version check |
| POST `/admin/leads/:id/deal-events` | Operator | Ordered evidence-backed deal/commission event |

Paginated lists expose `next_cursor`. Own application list is bounded to latest 100; operator intake is paginated. The operator UI supports queue pagination, application history and stage changes. Qualification requires reviewed evidence; onboarding additionally requires the active agency agreement, scoped onboarding evidence and a verified owner membership. Neither stage records activation. No asynchronous sender exists.

## Tests

From repository root:

```sh
node --test tests/mira-*.test.mjs
python -m unittest discover -s tests -p 'test_mira*.py' -v
```

The API suite uses the actual SQLite migration with a D1-compatible test adapter and signed synthetic RSA JWTs. It covers tenant isolation, durable receipts, idempotency, quotas, evidence/role gates, optimistic concurrency and immutable audit/financial records. All test names/IDs/amounts are explicitly synthetic. These tests do not replace deployed Cloudflare QA.

Optional `python tests/mira-offline-ui.py` requires Playwright and Chromium (`CHROMIUM_PATH` override supported). It uses mocked location/history/fetch with external network blocked. Browser navigation in the execution environment was blocked; offline DOM testing is NOT deployed E2E QA.

## Scope limits

Infrastructure provisioning, private document vault, privacy review, backups/retention and actual deployment remain owner-controlled. No file upload, external messages, payment execution, mixed-currency accounting, partial commission receipts, refunds/reversals or automatic developer integration. Do not infer them from a button or a recorded request.

## Primary implementation references

Cloudflare Access JWT validation: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json/

Cloudflare D1 Worker API: https://developers.cloudflare.com/d1/worker-api/d1-database/

Cloudflare D1 migrations: https://developers.cloudflare.com/d1/reference/migrations/

## Checkpoint 04 — operational experience (2026-09-16)

An additive migration preserves existing intake records without backdating approvals. New applications have an atomic immutable receipt event. Lead intake accepts an optional `Idempotency-Key`; the pilot UI always supplies one and reuses it on an unchanged in-page retry. Payment requests replay the same scoped payload, rather than create a second request. Changed payloads fail explicitly. Receipts are historical acknowledgements, not guarantees that supply evidence remains current. The UI preserves successful receipts when a later list refresh fails. A full page reload does not persist in-memory lead retry keys; check the existing client list before creating a new attempt.

The project detail endpoint separates project metadata, current project-agreement/seller checks, expiring inventory, registration rules and commission schedule. It exposes verification/expiry dates, not document contents, vault IDs, prices or assumed commission. `materials_available=false` is intentional until controlled delivery of materials is implemented; rights evidence alone does not prove a working document-delivery route.

Agency profile and manual application review are implemented; real deployment is still not performed. No external message/form submission, owner approval or operating activity is created by these screens. All reference test data remain explicitly synthetic.

## Checkpoint09 — assigned developers and approved material delivery

See [MATERIALS-README.md](./MATERIALS-README.md) for the read-only library, additive migration0003, per-file rights/release evidence and private R2 binding. Protect `/mira/library.html` with the pilot/API Access application. Material delivery remains disabled until separately configured and tested; no assets or real client data were uploaded. Internal-use downloads do not authorize client redistribution.
