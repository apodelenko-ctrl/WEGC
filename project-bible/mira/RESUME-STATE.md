# MIRA RESUME-STATE — isolated parallel server branch

2026-09-17. Read mission12, then `operations/parallel-server-2026-09-17.md` and `cloudflare-worker/mira/SERVER-START.md`. Branch `mira/parallel-server-20260917` is separate from the local public-interface work. Do not force-push, reset or overwrite local Codex work.

Completed locally: production Worker/RSA-verified synthetic onboarding path, durable receipt/reopen tests, administrative audit gap fix with rollback, scoped operator audit history, and a read-only single-environment config checker.15new Node cases /10new Python cases passed. Full restored snapshot98Node/112Python passed; branch CI counts may differ because later CP16 tests were not in that local snapshot.

Continue exactly here: inspect the dedicated `MIRA isolated server acceptance` run. Confirm `parallel-server-result.json` exists with passing measured counts and Worker SHA256 `85fe3edcee9326c6b24546e79cd02705457cbdf2da1025caf2c251d0ded6ed25`. Check that the Worker itself, not just literal-edit transport, is committed. Open/review the PR for integration by local Codex. No main merge or live deployment implied.

The source bundle `parallel-server-source.json` changes only cloudflare-worker/mira/worker.mjs using9 exact hashed literal edits and the existing applier. Other added files are ordinary source. Audit covers application-mediated administrative mutations from this release only. It does not reconstruct historical operations or track direct SQL administration.

Outstanding: real email/Access flow, authorized dedicated deployment and operator bootstrap, data-handling review, actual browser/server acceptance and recovery; project-specific supply admission separately. First company/admin/process decisions are confirmed in the first-partner handoff; do not repeat old questions. No external sends, no private original documents or credentials in GitHub. No new public-gallery changes in this lane.

## Isolated branch CI result

Passed source regression: 98 Node / 116 Python tests. Run 35219962533. See `operations/parallel-server-result.json`. No live login, main update or Cloudflare deployment.
