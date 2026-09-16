# MIRA WORK-STATUS

Updated UTC: 2026-09-16 06:55

## Canonical current state

Current operating priorities: **Russia agency activation + Phuket supply normalization + launch funnel execution**.

## Brand

- **МИРА — Международная инфраструктура риэлторских агентств** is the accepted public product brand.
- Naming generation is closed.
- IP / trademark / domain clearance remains a separate task and does not reopen naming.

## Russia agency funnel

### Source-backed launch cohort

- `sales/russia-launch-50-seed.csv`: ranks 1–50.
- `sales/russia-launch-50-batch-02.csv`: ranks 51–100.
- Current launch cohort: **100 unique source-backed agency organizations**.
- This is not the same as 100 outreach-ready partnership contacts.

### Live contact / role QA

Published batches 01–07 now cover **50 unique strategic agencies** with a fresh contact / role / entity review.

New batch 07 added 11 organizations, including:

- Городской Риэлторский Центр — named partner/development leadership route;
- Центр недвижимости, Тюмень — named leadership route;
- Квартирант Плюс — named CEO/sales leadership + existing Phuket direction;
- Панорама недвижимости — existing Turkey foreign-property signal;
- Рост Недвижимость — current partner/sales route;
- Ракурс — current new-build/company route;
- СОТА — strong regional/developer-cooperation signal;
- Вектор-Недвижимость — current multi-city central route;
- plus three hold/manual rows where first-party/entity certainty is insufficient.

General phone/email is not promoted to partnership-contact verification.

### Segmentation

Created `sales/russia-live-50-segmentation.csv` for the first **50 live-reviewed accounts**.

Current working segments include:

- `newbuild_regional`
- `premium_investment`
- `regional_large`
- `resort_regional`
- `far_east_regional`
- `existing_foreign_property_desk`
- `existing_phuket_direction`
- `network_platform`
- `hold_entity_resolution`
- `hold_first_party_verification`
- `segment_pending_fit`

This means one generic agency pitch is no longer acceptable.

Evidence-backed examples:

- `Диал` — existing foreign-property desk and named foreign-property director;
- `Квартирант Плюс` — existing Phuket direction + named CEO/sales/executive leadership;
- `Панорама недвижимости` — existing Turkey direction;
- `Самолет Плюс` / `МИЭЛЬ` / `АЯКС` — HQ/network-level accounts rather than branch outreach.

### Owner-review queue

- `sales/russia-priority-30-review.csv`: 30 unique priority organizations.
- `sales/russia-wave-01-owner-review.csv`: first **12 segmented accounts** for owner review.
- `sales/russia-wave-01-personalized-drafts.md`: personalized drafts for first high-fit accounts.
- **No external messages have been sent.** All send actions remain unapproved.

## Phuket supply

### Existing WEGC backbone

The repository already contains approximately **618 Phuket project rows** in the generated internal catalog. These are project rows, not unique developers.

### Normalization completed so far

- `data/phuket-developer-master.csv`: **40 deduplicated developer / counterparty / branded-residence groups**.
- `data/phuket-developer-alias-map-v1.csv`: recurring developer aliases.
- `data/phuket-project-master-seed-45.csv`: first **45 normalized project rows**.
- `research/phuket-normalization-rules.md`: project → developer family → legal seller rules.
- `sales/phuket-developer-outreach-queue.csv`: **20 unique developer groups**.
- `sales/phuket-p0-commercial-verification.csv`: first-party commercial/B2B evidence for **8 P0 groups**.

P0 commercial verification now separately records current public evidence for Botanica Agent Club, Origin Agent Club, Sansiri international agent registration, Phuket9 B2B Agency Network, Ozone multilingual sales route, Anchan current sales route, Laguna/Banyan pending entity mapping, and Rhom Bho/THE TITLE internal-relationship follow-up.

Public promotional commission language is stored only as a source claim and must not be treated as a universal project term.

### Phuket next gate

Continue:

`project → developer family → legal contracting seller → active inventory → agency/broker route → lead registration → commission → payout timing`.

Do not create fake developer counts from project names.

## CIS

- `data/agencies-cis-pilot.csv`: 88-row pilot layer.
- Packages 05–06 add 21 source-backed rows that still require canonical merge/dedupe before a net-new count is claimed.

## Bali / Vietnam / Dubai

First-party developer contact QA batch: **32 records** total — Indonesia 8, Vietnam 12, UAE 12. Dedicated broker/channel routes exist for part of the pool; contracting entity and commercial terms remain separate gates.

## Launch assets available

- `/mira/` — rebuilt acquisition landing.
- `sales/AGENCY-SALES-PLAYBOOK.md`.
- `sales/agency-crm-template.csv`.
- `sales/MIRA-PILOT-PACK.md`.
- `sales/MIRA-ONE-PAGER.md`.
- `research/mira-first-webinar.md`.
- `sales/developer-acquisition-pack.md`.
- onboarding, payment-copy and 90-day Telegram assets.

## Current priorities

### P0 — Russia

1. Convert the best 15–20 of the first 50 reviewed accounts to truly `ready_for_owner_review`.
2. Expand segmentation from the reviewed 50 to the remaining Launch-100 without guessing foreign-property status.
3. Resolve all domain/entity holds before promotion.
4. Keep Wave 01 prepared but unsent until owner approval.
5. Expand toward Launch-200 only after direct-contact conversion assumptions are testable.

### P0 — Phuket

1. Continue 45 normalized projects toward the full ~618 internal backbone.
2. Resolve developer family / legal seller rather than inferring from brands.
3. Deepen P0 commercial evidence: named channel owner, agreement entity, eligible projects, commission schedule, lead rule, payout trigger/timing, inventory feed.
4. Separate signed/current terms from public promotional claims.

## Hard controls

- **No mass external outreach without owner approval.**
- Generic company contact ≠ partnership contact.
- Source-backed ≠ contact-verified ≠ partnership-verified.
- Project brand ≠ legal developer / contracting seller.
- Payment route/cost/timing are deal-specific and cannot be guaranteed publicly.
- Internal payment routes are not public marketing copy.

## Next exact actions

1. Continue segmentation / decision-route QA through Launch-100.
2. Promote only 15–20 strongest accounts to final owner-review queue.
3. Continue Phuket project master beyond 45 using internal WEGC data first.
4. Expand P0 developer commercial verification beyond the current 8 groups.
5. Refresh `RESUME-STATE.md` at the next material checkpoint.
