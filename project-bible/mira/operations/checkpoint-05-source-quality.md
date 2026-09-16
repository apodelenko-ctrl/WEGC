# Checkpoint 05 — source joins and CSV integrity

Date: 2026-09-16. No external outreach, messages or form submissions.

## Actual delta

CP04 was restored to SHA256 `9e658486a0182328d9bf28ea1fe30d22b4ff10f512a8eabe2c90948b636bca4b`; QA run `35080168741` passed. The API remains undeployed. The successful static Pages run is not proof that the API is live, nor proof that this later generated source commit was published.

Three explicit, first-party-reviewed joins now bind the inherited reviews to the intended cohort accounts. The register has 100 accounts and matches all 50 inherited live reviews instead of 47; join exceptions fall from 3 to 0. This does NOT claim 50 new reviews. The inherited ready-for-owner-review count changes from 12 to 13 because the existing Avesta review is no longer dropped. The existing owner-review wave remains 12 accounts; none is approved to send.

`russia-reviewed-aliases.csv` deliberately scopes Avesta and Don-MT to the same city. The Samolet Plus mapping is limited to the existing HQ/network prospect, not franchise legal entities. Duplicate mappings, source/target absence, cross-domain evidence and unapproved cross-city joins fail validation. Source-review timestamps are not replaced by extraction timestamps.

CSV corruption corrected: unquoted commas split three developer aliases (Zero Developments, Modern 79, Pearl Island Property); an extra Ozone cell displaced its source URL, date and next action. Intended alias wording is reconstructed from the original row, not promoted to new legal evidence. Strict headers and row widths now fail before outputs are written. P0 source URL/date checks prevent recurrence of the observed displacement.

## Focused first-party observations

The official Avesta CEO card publishes a direct named route. Don-MT confirms its company identity but still needs a partnership owner. The Samolet Plus route is explicitly franchise-opening intake, not a supply decision owner. Ozone publishes ANIL and its sales email; agency-relations authority, unit stock and project seller remain unverified. Source URLs and limitations: `focused-source-review-2026-09-16.csv`.

## QA

Local: 40 Node tests (existing API/domain suite) and 31 Python tests passed, including 13 new source-quality regressions. Full-source build covers 618 project rows; 45 seed mappings and 66 generator candidates remain, with 507 family-unresolved rows. Legal seller and registration readiness are not inferred from these counts.

## Next independent block

Preserve operator-owned stages/evidence across rebuilds; align dashboard product status with CP04; produce actual-product acquisition assets and complete segmented content. A separate private review of owner-held supply documents is in progress; confidential scans, clauses, contacts and financial schedules are not copied into this public repository.
