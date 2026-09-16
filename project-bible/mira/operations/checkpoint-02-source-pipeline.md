# Checkpoint 02 — complete-backbone coverage pipeline

Date: 2026-09-16. This checkpoint adds executable processing, not another discovery batch.

## Implementation

`python scripts/mira-launch-build.py` reads the actual generated `ru/wegc-catalog-data.js`, preserves every unique source slug, joins existing seed mappings and alias evidence, separates operator/brand-only signals, and generates `data/phuket-project-master.csv`. It does not execute the old generator with inaccessible developer-local source paths. Missing seed rows, conflicting aliases or duplicate slugs fail instead of silently dropping data.

The same offline run builds Launch-100 quality coverage from both original cohort files and the already-completed 50-row live segmentation. All joins are company+city; unresolved joins go to a separate exception register. Source-only classifications are candidates, never a new live review. Absence of overseas evidence never establishes greenfield status. Original research and send-approval files remain unchanged.

P0 developer stage register starts from observed public evidence, with separate blank commercial evidence gates. A public Agent Club signup does not prove MIRA has signed a contract or registered a buyer.

The canonical dashboard is generated as Markdown, JSON and internal HTML. It distinguishes source-backed counters from unknown real operating metrics. No invented conversion rates or zero-valued financial performance.

## QA

Nine local Python regression tests passed: source parsing, duplicate slug rejection, candidate vs seller separation, operator separation, missing-seed failure, alias-conflict failure, cross-city join isolation, no inferred greenfield, idempotent status updates. Eight existing Node tests also remain required in CI.

`.github/workflows/mira-launch-qa.yml` runs tests and actual full-source generation on repository infrastructure, then commits only explicitly listed generated outputs plus WORK-STATUS/RESUME-STATE. No messages/forms/provider calls occur. The run must be inspected before claiming generated row counts.

## Publication boundary

Pages output now excludes project-bible, tests, scripts and the dedicated future MIRA backend folder. Existing WEGC catalogue/covers assets remain available. This excludes internal files from the website build; it does NOT change GitHub repository visibility, remove historical deployments, or secure data already public elsewhere.

## Continue

Inspect workflow results; resolve real failures rather than changing target counts. Continue secure pilot backend, landing/demo integration, sales assets and live decision-route QA. No external sending is approved.
