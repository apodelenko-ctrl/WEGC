# MIRA durable checkpoint — 2026-09-16

This checkpoint restores a durable continuation state on GitHub after the previous scratch workspace was cleared.

## Remote counts verified

- Mega discovery: 417 rows.
- Mega source-level verified: 401 rows.
- Russia pilot: 324 rows.
- CIS pilot: 88 rows.
- Phuket developer master: 40 rows.

## Important integrity note

A previous local run produced live-QA and dedupe artifacts in scratch, but they were not present on remote `main` and are therefore not counted here. This checkpoint deliberately records only remotely verified facts.

## Next batch

Recreate `MIRA-RU-LIVE-QA-001` for mega discovery rows 1–100, publish it through the connected GitHub API, re-read it from `main`, then process rows 101–200 in a separate shard.

No outreach is authorized or sent.
