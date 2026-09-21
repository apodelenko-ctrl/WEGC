# MIRA Cloudflare research import — checkpoint CF001

This package prepares an additive import for the **existing** MIRA Worker/D1 application.
Owner screenshot21Sep23:40 confirms `mira-pilot-api`, domain `pilot.wegc.fund`,
binding `MIRA_DB` → database `mira-pilot`, and static asset binding `MIRA_ASSETS`.
Do not create another production database or mistake static Assets for an R2 bucket.
No authenticated Cloudflare connector/token is available in this execution session.
Remote schema inspection/import and Worker deployment remain NOT_RUN.

## Implemented

- Reproducible snapshot of405 agency candidates,43 developer groups and618 project mappings.
- Original JSON preserved exactly in meaning: IDs, nulls, classifications, source lineage,
  all field-level evidence and contact observations.19 agency fields are additionally indexed;
  developer contacts are indexed individually.7742 field rows include missing values and are
  **not7742 verified contacts**.47 developer contact observations are not47 unique people.
- Optional **private** crosswalk import preserves165 native research identities.78 agency
  references resolve to current canonical IDs.87 developer source-lineage rows remain separate:
  domain candidates never become automatic legal/entity matches.
- New tables contain research snapshots only. Existing13 operational tables and their
  data are untouched. No membership, application, contract, project activation or send approval
  is created. This is not the full native167Account/Email/Task/mail restore.
- Deterministic snapshot identity, immutable rows, conflict detection, replay without duplicate
  rows, and final commit marker. Interrupted snapshots are absent from published views until
  all expected rows are present. Resume by replaying the same SQL; no deletion/reset required.
- Snapshot-scoped summary: never sum different snapshots or add native lineage to research
  entity counts. A future operator integration must choose an explicit accepted snapshot ID.

## Prepare against a verified research checkout

Python3 standard library only. Read current HEAD and preserve local edits. `--source-commit`
records provenance; the operator must supply the actual checkout commit. File semantic hashes
are calculated from parsed canonical JSON, not confused with raw source byte hashes.

```sh
python import_registry.py prepare --repo /path/to/WEGC --source-commit ACTUAL_40_HEX_SHA --out /private/new-public-import
```

For private native source lineage, also pass `--native-crosswalk /private/crosswalk.json
--private-output`. Never put that output in the public repository or static site. All output
files are0600 in a new0700 directory with `*` gitignore. Existing output is never overwritten.
The existing separate recovery key is not needed to read the transferred crosswalk. It remains
needed for the encrypted native database/mail archive or use an authorized portable export.

Outputs: complete `0004_research_import.sql` including immutability/sealing triggers,
`import.sql`, and aggregate `summary.json`. **Do not apply `schema.base.sql` directly:** it is
the generator input and lacks generated guards. Generated SQL is staged data, not published API.

## Local verification

```sh
MIRA_SCHEMA_ROOT=/path/to/WEGC/cloudflare-worker/mira/migrations python -m unittest discover -s . -p test_import_registry.py -v
```

16 tests passed using exact main migrations0001–0003. Separately, both full factual source
variants were imported into isolated SQLite databases and replayed.405/43/618 original JSON
records round-trip;165 private lineage rows also round-trip; all13 operational tables retain
their prior data. The synthetic sentinel used to prove preservation is excluded from counts.
See `TEST-REPORT.json`. This is SQLite compatibility evidence, not remote D1/workerd acceptance.

## Next live action — existing database

1. In `mira-pilot` Console run **read-only** `live-inventory.sql`, or equivalent authorized API
   queries. Capture current table definitions, migration names, counts and resource identity.
   The screenshot proves resources exist; it does not reveal database UUID or table contents.
2. Compare with main source schema. If migration0004 already exists under another name or any
   `mira_import_*`/`mira_research_*` table exists, inspect it first; do not replace it. Keep a
   current D1 export/bookmark. Actual D1 schema and backup gate must pass before remote writes.
3. Apply the generated additive migration and import through authorized tooling, first in an
   isolated D1 test target or accepted controlled migration flow. Replaying existing migrations
   0001–0003 in production is not part of this package. No blind whole-research-branch merge.
4. Confirm per-snapshot summary, expected table counts, record hashes and all previous
   operational counts/receipts. `mira_research_summary` contains only completed snapshots.
   For an exported/local DB: `python import_registry.py verify --database /private/db.sqlite
   --snapshot MIRA-IMPORT-...`. This read-only verifier is not a Cloudflare API client.
5. Integrate a read-only **operator-only** research view into the existing auth/membership
   boundary. No new public endpoint is included here; private lineage must never be returned
   to ordinary applicants, other agencies or the static catalogue.
6. Move remaining native CRM operations/history only after separate schema mapping and
   evidence-backed import. Candidate developer crosswalk, native Email/Task, journal, drafts,
   attachments, contract evidence and suppression state are not reconstructed from counts.

The screenshot shows Worker logs/traces disabled and zero queue bindings on this Worker.
This does not prove absence of account-wide queues or other runtimes. Logging configuration,
dispatch and full launch acceptance remain separate work; no settings were changed here.

## Sources

- Source main `9a5f4c89168aa9e7995ceebf6db8dbaaf9a61137`.
- Source research `a2248f860580107dad82c94e5f864646c4538ecc`.
- [D1 import/export](https://developers.cloudflare.com/d1/best-practices/import-export-data/).
- [D1 limits](https://developers.cloudflare.com/d1/platform/limits/): generated statements
  max19919 bytes, below documented100000-byte limit. Full source test does not prove live quota.
- [D1 query API](https://developers.cloudflare.com/api/resources/d1/subresources/database/methods/query/).
