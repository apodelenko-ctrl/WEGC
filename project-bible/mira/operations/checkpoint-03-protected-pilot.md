# Checkpoint 03 — protected pilot implementation

Date: 2026-09-16. Parent source checkpoint: `ff269e8dacc8bde2367a746c94fdfcb641bff7ee`.

## Delivered code

Dedicated `cloudflare-worker/mira/`: Worker, Access JWT verifier, domain rules, actual SQLite/D1 schema, example fail-closed configuration, deployment/operations runbook. Server-scoped agency membership, broker isolation, durable application receipts with idempotency/quota, evidence-gated project/client intake, versioned lead transitions, immutable audit/evidence/deal events, separate payment-support requests, exact-evidence financial entries and operator queue/counts.

`mira/pilot.html` and `pilot.mjs`: same-origin UI for protected application, assigned projects, lead intake, history, payment-support request and operator status/queue. It refuses non-API/static responses and does not replace server data with demo fixtures. Real application collection remains disabled until privacy and Access configuration are approved.

`scripts/mira-wire-landing.py`: narrowly replaces legacy mailto intake with actual demo and closed-pilot entry. Accepted hero/positioning/marketing sections remain intact. Transformation is idempotent and fails on an unexpected source structure. CI and Pages both apply it; CI saves the changed landing back to GitHub.

## Verified locally

- 28 Node tests passed: 8 existing demo domain + 20 API/security/SQLite/JWT tests.
- 13 Python tests passed: 9 existing normalization + 4 landing integration tests.
- Offline DOM flow passed: catalog/search/detail/local client draft/payment draft/duplicate guard/profile/mobile overflow; protected UI with a strictly local mock receipt; non-API fallback fails closed. All external browser network requests were blocked in that test.
- Simultaneous valid status updates yield one saved transition and one conflict, with no extra audit event.
- Synthetic financial fixtures are test data only; no real prices, amounts, rates or split assumptions were added.

## Not claimed

No Cloudflare deployment, real Access session, production database, signed agency/project agreement, live receipt or developer confirmation was created. No real client data or external messages/forms were submitted. Browser navigation in the execution environment remains blocked; offline DOM checks do not establish deployed E2E QA.

Checkpoint 02 generation was independently verified successful in GitHub Actions run 35071062219. Its source-backed outputs cover 618/618 project rows and all 100 launch accounts, with 47 of 50 inherited reviews joined and 3 explicit exceptions. This checkpoint does not relabel those as fresh live verification.

## Next independent work

Resolve the three explicit Russia entity/city aliases from evidence; improve remaining decision routes and owner-review readiness; complete incremental segmented acquisition/activation assets based on the actual product; deepen Phuket entity/commercial mapping; make dashboard stage projections consume durable event/evidence inputs rather than resetting human progress. Cloudflare setup and any external sending remain owner-gated.
