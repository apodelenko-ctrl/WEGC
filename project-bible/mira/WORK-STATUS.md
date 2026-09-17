# MIRA WORK-STATUS — isolated parallel server branch

2026-09-17. Branch `mira/parallel-server-20260917`, based on main `13360ee8e9b74f22b6e474f128bbd3ac5b5cd513`. This file describes this lane, not a new production release. Main's prior status remains in Git history and `operations/2026-09-17-first-partner-handoff.md`.

## Checkpoint PAR-SERVER-01

Added transactional administrative audit and operator-only history, a production-Worker signed-identity journey suite, read-only deployment preflight and local integration runbook. Three missing-audit cases were reproduced on the old code and fixed. Local15new journey/audit cases and10preflight tests passed; final full restored-source run98Node/112Python passed. Actual branch CI is still pending until `operations/parallel-server-result.json` is generated and read.

The Worker integration consists of9 bounded literal edits with exact source/target hashes. Dedicated branch CI validates/materializes them, runs regression tests and saves ordinary source only to this branch. Never merge an unapplied transport or treat a passing local test as a Cloudflare rollout.

## Parallel ownership

Local Codex: public catalogue photos, cards, copy, click-through/browser review, authorized local deployment. Web lane: server audit, lifecycle/regression tests, preflight. No `mira/` public route modified, no main push, no Cloudflare resources or emails touched. Public data statements and commercial gates are not changed.

## Still required

Actual Cloudflare account/zone/newDB/Access configuration and email delivery; verified first administrator; real deployed signup and cross-agency isolation; data-handling/privacy review; backup/restore; private documents/material permissions and one current developer registration path. Public legal documents remain drafts. Company and intended onboarding choices are already confirmed; do not ask them again. No receipt/protection/commission or live registration is invented.

Next: inspect isolated branch CI, verify ordinary Worker bytes, open a reviewable PR for local Codex, integrate without overwriting its working tree, then perform real deployment acceptance. Do not recollect the618catalogue or restart design.
