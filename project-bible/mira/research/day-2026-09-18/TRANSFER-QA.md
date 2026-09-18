# Transfer QA — 18 September 2026

Reviewed export source: night research `beb9707c8561c138c896b122c6776a217ee4b3f0`, main reference `1b5e6cc053bd4b20a47c3f4231c56bb1f05d850b`. Export run 35294630054 / artifact 10527386378 succeeded; archive SHA256 5de4497f3238da892f0cd870cbc61b14a2e94f22b1ba0a796562003228d49a08 matches. All 230 declared exported file hashes were checked in the cloud container.

## Real defects found before handoff

The historic detailed `night-2026-09-18/05-belarus-agencies.csv` contains **29 rows**, not 30. **14 rows** contain 19 fields under an 18-field header. Do not import this CSV or silently truncate fields. `05-belarus-agencies.json` contains all 30 correctly structured records; the compact `belarus-agencies.csv` also contains the 30 expected IDs. The missing detailed CSV record is `by-eksklyuziv-group`.

Delivered `import/belarus-agencies.csv` and JSON were rebuilt from source JSON keyed by ID and compact-index status/order; 30 rows, rectangular columns, no inferred contacts. Originals are retained as evidence. RU 29+21 detailed rows were joined to the 50-row compact index. Combined 80 IDs are unique. All remain research candidates and unapproved for outreach.

Exact-domain comparison scanned **52 main data/sales CSV files**, with no malformed baseline rows skipped and zero exact-domain matches for candidate domains. Fifteen Belarus entries have no official domain. This is not legal-entity/rebrand deduplication, a current licensing opinion, or comparison against unpublished local CRM. Do not claim 80 independently verified new companies.

Lumi Hanoi's group was incorrectly named CapitaLand Investment. Corrected delivery value: **CapitaLand Group**, source https://www.capitaland.com/vn/en/about-capitaland/who-we-are.html (read 18 September). Developer remains CapitaLand Development, legalSeller=null.

A complete **30-row explicit taxonomy** was added to the owner package, with condo/villa/mixed/hotel display groupings and original propertyTypes preserved. Hotel units and mixed masterplans must not be flattened into condominium ownership claims. Local code integration is still required.

## Delivered counts

Vietnam 15; Montenegro 15; 24 complete-for-discovery and 6 partial. Russia 50; Belarus 30 research candidates. No new media publication permission. No main, server, D1, Access, DNS, registration or deployment change.

The delivery validation covers hashes, parse, column alignment, IDs, exact-domain scan, taxonomy and closed commercial/send gates. It is NOT browser QA, a live-site release, exhaustive external-source revalidation or acceptance of an ordinary real applicant.

Owner package: MIRA-LOCAL-TRANSFER-2026-09-18.zip. START-HERE.md defines selective integration; full ROADMAP-2026-09-18-25.md and a read-only VERIFY-PACKAGE.py are included. Do not merge the entire earlier research branch into the new main.
