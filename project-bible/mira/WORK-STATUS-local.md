# WORK-STATUS-local.md

Updated UTC: 2026-09-15T19:14:11Z

## Mega pipeline

- Discovery: 417 unique records written to `data/mega-discovered.csv`.
- Classification: 417 records written to `data/mega-classified.csv`.
- Source-level verification: 401 records written to `data/mega-verified.csv`. These are **not** claimed as live verified contacts; official source presence only.
- Outreach queue: 245 contact-bearing records written to `sales/mega-outreach-queue.csv`; no messages sent.
- Dedupe key: entity type + normalized name + website.
- Blocker: existing corpus contains duplicates, seed records, and unverified contact claims. Live HTTP/contact QA requires a separate pass; unknown fields remain unknown.

Next: run live domain/contact checks in batches of 100, then promote only rows with evidence and date.
