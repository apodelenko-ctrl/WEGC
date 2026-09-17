# Parallel server lane — 2026-09-17

Base read from GitHub: `13360ee8e9b74f22b6e474f128bbd3ac5b5cd513`.
Branch: `mira/parallel-server-20260917`. No main/public deployment or operator provisioning performed by this lane.

## Actual gap reproduced and fixed

On the unchanged server source, three new tests failed: administrative agency changes, membership grants/revocations and project assignments had no immutable application audit events. The new batch helper makes each mutation and its event atomic; audit failure rolls back the write. Scoped operator-only history is exposed at `/mira/api/admin/audit`. No past history is invented. SQL changes outside the application and lost-update protection for existing admin upserts remain outside this fix.

## Acceptance

15 new server lifecycle/audit tests passed locally. They use the actual exported Worker, signed synthetic RSA claims and the real migration schema on temporary file-backed SQLite. Only the Access certificates response is mocked. Nine baseline journey tests passed before the new audit cases; the three audit regressions first failed on the old implementation, then passed after the fix. Further concurrency/operator-history cases also passed.

10 new read-only preflight tests passed. The utility rejects unrelated resource names, broad routes, incorrect expected IDs, secret/unknown vars, ambiguous extra bindings, public preview hosts and an enabled intake in closed mode. It does not deploy or certify actual permissions/legal readiness.

Local full-snapshot regression: 98 Node / 112 Python tests passed. Do not treat snapshot counts as current-branch CI counts: the restored source snapshot predates later CP16 Python test additions. The branch workflow reruns tests on its exact parent and records measured counts in `parallel-server-result.json`.

## Delivery discipline

The Worker update is transported as nine bounded literal edits with exact before/after SHA256, validated by the existing reviewed-source applier. Dedicated branch CI materializes it as ordinary `worker.mjs`, runs regression tests and only then saves source on this branch. It never touches main or deploys a Worker. Other new files are plain readable source. A source hash mismatch stops materialization instead of discarding concurrent changes.

Local Codex can review/merge this branch once CI and ordinary Worker source are confirmed. `cloudflare-worker/mira/SERVER-START.md` contains the integration and acceptance scope.

## Still not ready

Public image completeness and old editorial browser route remain with the local interface lane. Actual Cloudflare configuration, email delivery/login, first operator provisioning and deployment browser tests remain unverified. Contract approval/current project admission, rights to materials, backup/restore and data-handling review remain separate launch requirements. No new business numbers, screenshots, supply approvals or successful live registrations are claimed.
