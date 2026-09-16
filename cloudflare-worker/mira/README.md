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
3. Apply the SQL migration to the new database using authorized migration tooling. Review schema first.
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
| GET/POST `/applications` | Verified Access | Own queue / durable intake receipt |
| GET `/projects` | Active member | Assigned metadata |
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

Paginated lists expose `next_cursor`. Own application list is bounded to latest 100; operator intake is paginated. The UI currently shows the first operator intake page and identifies further pages. No asynchronous sender exists.

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
