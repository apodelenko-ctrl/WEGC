# CP13 — full public Phuket research catalogue

2026-09-17. Source coverage is not commercial supply readiness.

Implemented `/mira/catalog/`, a searchable 618-record catalogue, every static project detail URL, alphabetical no-JS fallback, 24-card pagination, filters, and a local project-ID-only shortlist/download. Exact source and master identity sets are checked. Source hash is published. Prices, FX, delivery dates, areas, private contacts and inferred inventory are excluded. Five existing exact project-image associations remain labelled archived visualizations; other records do not receive misleading generic project photos.

Original45-record demo, illustrated marketplace and all earlier designs are untouched. Real client registration remains disabled; private evidence and approved localized data architecture are still needed. `/mira/go/` is a stable own entry prepared for the next design checkpoint.

Local QA:74Node/87Python tests passed. Offline DOM tests cover618load, filter/search/empty/reset, shortlist/download and7widths320–1440. Actual browser navigation is blocked by the execution environment; these are NOT live-domain or deployed registration tests. GitHub CI and Pages must be inspected next. Bounded load and actual-CSP browser release testing remain the next independent work.
