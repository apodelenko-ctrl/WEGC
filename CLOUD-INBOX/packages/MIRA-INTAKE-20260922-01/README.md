# EXPO22-A — public connection request + durable operator response

Prepared for selective LOCAL integration, **not deployed or enabled**. This supplements the existing EXPO task and CF004 baseline; no competing product or CRM is created. Source main `9a5f4c89168aa9e7995ceebf6db8dbaaf9a61137`; research `8a76199e7a54bc6a3e01f3763004892edc7e19d5`.

## Implemented

- Same existing Worker/D1. New isolated `/mira/request/` HTML/client and submit/status routes. Existing `/mira/api/*`, pilot, Access verification, applicant identity and operational tables remain unchanged in meaning.
- Three additive tables in `0005_public_intake.sql`: requests, immutable events and bounded rate buckets. Number0004 is reserved by the separately prepared research import; no dependency on0004.
- Company/city/name/business email and versioned consent only. Email remains explicitly unverified. No buyer/client data, membership provisioning, agency activation, commercial promise or automated invitation.
- Exact idempotency key + canonical payload hash + hashed 256-bit client receipt secret. Request and audit event stored in a D1 batch. Concurrent review uses version compare-and-swap. Response readable only with receipt ID and bearer secret, never a token in URL. Raw IP and challenge tokens not stored.
- Active configured operator required before intake. Protected operator queue API and explicit text response publication to receipt holder. This is a durable pollable queue, **not an email notification system**. No actual response sent in this checkpoint.
- Server-side Turnstile success + exact hostname + `mira_intake` action; conservative hardcoded abuse ceilings (engineering defaults, not traffic forecasts): submit10/IP/hour and300 globally/hour; status60/IP/hour and3000 globally/hour. HMAC quota identity rotates hourly, buckets expire after48h. No X-Forwarded-For trust fallback.
- Origin check, 8KiB streamed body ceiling, field allowlist, bound SQL, strict transitions, no-store/no-referrer, DOM textContent, default disabled.

## Apply to an isolated copy of current main

Do not replace the older research root Worker or merge the research branch. This package is based on current **main**, including the newer operator directory and notice routes. Keep unrelated LOCAL changes.

```sh
python /path/to/package/apply_package.py --repo /path/to/isolated-main
python /path/to/package/apply_package.py --repo /path/to/isolated-main --apply
node --test tests/mira-api.test.mjs tests/mira-site.test.mjs tests/mira-public-intake.test.mjs tests/mira-intake-client.test.mjs
```

Run Node command from the isolated repository. Hash mismatch stops the package before writes; inspect/merge changed inputs rather than forcing replacement. Default command validates only. Replay preserves identical applied files. No Wrangler/deploy/API calls are in this script.

## Activation prerequisites — do not skip

1. CF004 already accepted live schema/migrations/counts. Obtain a **current** pre-change backup/bookmark; the last screenshot ran `/bookmark` in Studio without returned bookmark, so recovery point is still unconfirmed. Do not run `/restore` to inspect. No new general inventory requested.
2. Authorized operator must test migration and batch rollback/replay on isolated D1, including coexistence with optional0004. Then controlled additive migration in existing `mira-pilot`, preserving all original tables and existing application/membership/events. No replacement production database.
3. Actual privacy owner must approve notice for this **public unverified-contact intake**, its fields, retention/deletion process and service provider; existing invited-intake notice is not automatically accepted for this new purpose. No invented policy/contact/SLA. Current event retention is immutable; implement approved erasure/anonymization procedure before enabling.
4. Configure `PUBLIC_INTAKE_ENABLED=true` only after acceptance; `PUBLIC_INTAKE_PRIVACY_APPROVED=true`, existing `APP_ORIGIN`, `PRIVACY_VERSION`, `PRIVACY_NOTICE_URL` (same origin), actual `INTAKE_OPERATOR_SUBJECT` with active operator membership, `TURNSTILE_SITE_KEY`, secret `TURNSTILE_SECRET_KEY`, secret `INTAKE_RATE_SECRET` (>=32 chars). Keep secrets/actual subject out of public Git. Configuration approval flags are a deployment gate, not legal evidence by themselves.
5. Existing Access policy is not known to permit public paths. LOCAL must authorize an **exact narrow exception** for `/mira/request/*` and the approved public notice only, never `/mira/api/*`, pilot or admin. Do not disable Access on the hostname. Real Turnstile/Russia network behavior requires browser test. No Access change made here.
6. Bind operator UI/notification into existing cabinet. API is ready, but this package does not add an operator screen or send email. Assign actual shift and response handling before enabling. Bearer receipt response is plain text, not marketing/outreach. Do not enter private internal notes into a published response.
7. After live acceptance only, connect `/mira/access/` CTA to `https://pilot.wegc.fund/mira/request/`. Preserve the printed `https://wegc.fund/mira/start/` QR URL and the earlier CTA package. No dead public link added by this package.

## API contract

Public submit `POST /mira/request/submit`: JSON `company,city,name,email,consent_version,challenge`; same-origin request, UUIDv4 `Idempotency-Key`, `Authorization: Bearer <64 lowercase hex>` generated with browser crypto. Secret remains in sessionStorage in this tab; not recoverable by email, no emailed receipt. Page reload retains it; closing the tab may lose it. Storage failure warned. Network retry uses same key/secret/payload; changed payload gets409, no duplicate.

Status `POST /mira/request/status`: JSON `id`, same bearer secret. Only status/timestamps/operator public response, no submitted contact fields. Initial intake kill switch closes public status too; do not turn it off as a routine submission-only pause while responses need to remain readable. Separate pause-only control is a follow-up improvement.

Operator queue `GET /mira/api/admin/intake?limit=25&cursor=<id>` (max100), protected by existing JWT+active operator membership; returns unverified fields and assigned subject, no hashes/tokens. UUID ordering pagination is not arrival ordering; operators must refresh first page for new arrivals. Operator update `POST /mira/api/admin/intake/<id>/review`: `version,status,response`; statuses review/needs_information/responded/closed, closed terminal. Public response required for needs_information/responded; no agency activation state. Stale version409 requires refresh, no blind retries.

## Verification boundaries

Node SQLite tests exercise real SQL, transactions, concurrent attempts, induced write failure, restart from disk, field privacy, operator denial, request replay, status/response and UI event logic. Existing invited intake/Access/API tests are rerun unchanged. DOM harness is **not** a rendered mobile/browser test. Siteverify is mocked, no real form submissions or external messages.

NOT_RUN: remote D1 migration/import, actual Turnstile, Cloudflare policy changes, public deploy, browser/mobile/Russia run, operator UI/notification, real applicant cycle, native CRM decryption/restore. No claim that EXPO-03/05/06 is live-passed. Account source counts remain405/43 and private78/87+2 separately. Botanica signed/stamped-and-sent preserved.

Official contracts checked22Sep2026: [Turnstile server validation](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/), [D1 batch API](https://developers.cloudflare.com/d1/worker-api/d1-database/). New preparation does not require VPS or SSH.
