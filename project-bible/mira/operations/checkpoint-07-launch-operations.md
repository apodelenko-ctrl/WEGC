# Checkpoint 07 — canonical launch operations

2026-09-16. This checkpoint adds code and a tested private export path, not operating results or live deployment.

## Changes

The canonical dashboard now enumerates all19 mission capabilities, identifies partial developer/material delivery, and separates implementation from deployment. Existing source-backed research counters remain intact. Business counts are unknown without a complete operational dataset; stage observations count organizations, not buyers, bookings or payments.

The source builder is retained byte-for-byte at `scripts/mira-launch-source.py`. The standard `mira-launch-build.py` wrapper checks a hash manifest before regeneration and refuses to erase manual developer-register edits. CI persists `operations/launch-build-manifest.json`. The first migration also refuses obvious human stages or private evidence instead of overwriting them.

`mira-launch-operations.py` accepts an optional private operator journal outside the repository. It checks known entity IDs, opaque references, time zones, past timestamps, ordered per-entity chains, explicit historical observations, holds/resumes and approval references on external-action observations. It sends nothing and never grants deployment, collection or outreach authority. Private outputs and journal snapshots remain outside GitHub; previous events must be an unchanged prefix.

`operations/OPERATOR-JOURNAL.md` defines fields, agency/developer stage rules, command use, evidence responsibilities and limitations. `operator-journal.example.json` is intentionally empty. The public dashboard and private export use the same canonical view code, not separate competing KPI definitions.

## Verification

Local40 Node tests and50 Python tests passed. The15 new operator tests cover unknown/empty data, no historical backfill, transition guards, duplicate/chain validation, timestamp and raw-field rejection, approval references, hold/resume, append-only snapshots, generated-register conflict refusal, private path boundaries and preservation of public files during private exports.

Four offline DOM checks covered desktop/mobile programme and dashboard; no horizontal overflow or network calls observed. These are offline render checks, not deployed E2E tests. CP06 QA35083105777 and Pages35083105611 are already confirmed successful. Check the CP07 run before asserting remote results for this code.

## Remaining independent work

Current decision routes and wave-aligned drafts; first-party Phuket mappings and P0 owner-review evidence; remaining protected developer/material delivery. The real launch still requires owner approvals, configured deployment, privacy/evidence infrastructure and at least one current project-specific commercial/registration path. No external contact, private contract content, fabricated conversion or financial figure is included.
