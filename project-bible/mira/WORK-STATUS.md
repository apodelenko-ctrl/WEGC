# MIRA WORK-STATUS

Updated UTC: 2026-09-16 06:41

## Canonical current state

This file replaces the stale top-level status from the earlier x3 / naming phase. Historical details remain available in Git history and supporting research files. Current operating priorities are **Russia agency activation + Phuket supply normalization + launch funnel execution**.

## Brand

- **МИРА — Международная инфраструктура риэлторских агентств** is the accepted public product brand.
- Naming generation is closed.
- IP / trademark / domain clearance remains a separate legal-brand task and does not reopen naming.

## Russia agency funnel

### Source-backed launch cohort

- `sales/russia-launch-50-seed.csv`: ranks 1–50.
- `sales/russia-launch-50-batch-02.csv`: ranks 51–100.
- Current launch cohort: **100 unique source-backed agency organizations**.
- This is not the same as 100 outreach-ready partnership contacts.

### Live contact / role QA

Published batches now cover **39 unique strategic agencies** with a fresh public-route / named-role review:

- `russia-contact-qa-batch-01.csv`
- `russia-contact-qa-batch-02.csv`
- `russia-contact-qa-batch-03.csv`
- `russia-contact-qa-batch-04.csv`
- `russia-contact-qa-batch-05.csv`
- `russia-contact-qa-batch-06.csv`

Strong verified role signals currently include director / CEO / commercial / new-build / foreign-property leadership routes. General phone/email is not promoted to partnership-contact verification.

### Owner-review queue

- `sales/russia-priority-30-review.csv`: 30 unique priority organizations.
- `sales/russia-wave-01-owner-review.csv`: first **12 segmented accounts** for owner review.
- `sales/russia-wave-01-personalized-drafts.md`: personalized drafts prepared for the earliest high-fit accounts.
- **No external messages have been sent.** `send_status = not_approved` remains the rule.

### Important new segmentation finding

`Диал` has a current official **foreign-property director** and a public overseas partner model. It is therefore not a greenfield “teach you overseas property” prospect. It belongs to `existing_foreign_property_desk` and needs an upgrade/infrastructure pitch. A dedicated benchmark card is saved at `research/competitors/dial-regional-overseas-model.md`.

This segmentation must be applied to the rest of Launch-100: greenfield agency, existing foreign desk, network/franchise, premium/investment, regional new-build, or hold/entity-resolution.

## Phuket supply

### Existing WEGC backbone

The repository already contains approximately **618 Phuket project rows** in the generated internal catalog. These are project rows, not unique developers.

### Normalization completed so far

- `data/phuket-developer-master.csv`: **40 deduplicated developer / counterparty / branded-residence groups** from the first normalized layer.
- `data/phuket-developer-alias-map-v1.csv`: alias map for recurring developer families.
- `data/phuket-project-master-seed-45.csv`: first **45 normalized project rows**.
- `research/phuket-normalization-rules.md`: project → developer family → legal seller rules.
- `sales/phuket-developer-outreach-queue.csv`: **20 unique developer groups**, not project duplicates.

Known families already recognized in the internal generator include Rhom Bho / The Title, Botanica, Laguna / Banyan, Origin, Sansiri, The Zero, Mouana, Wyndham, VIP, Ozone, Mono, Unique, Aileen, Anchan, AssetWise and Naturale. This is not yet the complete developer map for all ~618 rows.

### Phuket next gate

Do not grow a fake “TOP-N developers” list from project names. Continue the full internal catalog normalization and resolve:

`project → developer family → legal contracting seller → active inventory → agency/broker route → lead registration → commission → payout timing`.

## CIS

- `data/agencies-cis-pilot.csv`: 88-row pilot layer from earlier work.
- Additional published source-backed increments: packages 05 and 06, **21 rows total**, not yet to be counted as 21 net-new canonical organizations until merge/deduplication.
- Direct partnership contacts and current overseas activity remain the main QA gap.

## Bali / Vietnam / Dubai

Published first-party developer contact QA batch contains **32 records**:

- Indonesia/Bali: 8
- Vietnam: 12
- UAE/Dubai: 12

Dedicated agent / broker / channel-partner routes exist for part of the batch. Commission, lead protection and contracting entity remain `unknown` unless explicitly evidenced.

## Launch assets already available

- `/mira/` — rebuilt agency acquisition landing prototype.
- `sales/AGENCY-SALES-PLAYBOOK.md` — agency sales manager playbook.
- `sales/agency-crm-template.csv` — CRM pipeline template.
- `sales/MIRA-PILOT-PACK.md` — pilot pack.
- `sales/MIRA-ONE-PAGER.md` — one-page agency proposition.
- `research/mira-first-webinar.md` — first B2B webinar structure.
- `product/onboarding-scenarios-3.md` — onboarding scenarios.
- `research/payment-copy-pack-3-variants.md` — payment messaging.
- `research/telegram-content-calendar-90d.md` — 90-day content plan.
- `sales/developer-acquisition-pack.md` — developer-side pitch.

## Current priorities

### P0 — Russia

1. Expand fresh contact/role QA from 39 to **50 priority organizations**.
2. Segment Launch-100 by actual sales situation, not one generic pitch.
3. Resolve domain/entity conflicts before promotion.
4. Prepare Wave 01 for owner approval; do not send.
5. After direct-contact conversion is understood, expand curated cohort toward Launch-200.

### P0 — Phuket

1. Continue 45 normalized project rows toward the full ~618-project backbone.
2. Expand alias/entity resolution without guessing legal sellers.
3. For P0 developer groups, identify named agency-relations / broker manager where public or obtainable through existing relationship.
4. Record current commission, lead protection, payout and active inventory only when first-party / contractual evidence exists.

### P1

- Merge/dedupe CIS increments into a canonical queue.
- Deepen Bali/Vietnam/Dubai contracting-entity and channel-owner verification.
- Keep competitor research focused on acquisition mechanics and operational gaps relevant to MIRA.

## Hard blockers / controls

- **No mass external outreach without owner approval.**
- Generic company contact ≠ partnership contact.
- Source-backed ≠ contact-verified ≠ partnership-verified.
- Project brand ≠ legal developer / contracting seller.
- Payment availability, route, cost and timing are deal-specific and cannot be guaranteed publicly.
- Do not expose internal payment routes publicly.
- Do not claim trademark registration / exclusivity before clearance.

## Next exact actions

1. Russia contact QA batch 07: fill 11 more priority accounts to reach 50 live-reviewed organizations.
2. Create a canonical segmentation register for Launch-100.
3. Continue Phuket project master from seed 45 using internal WEGC sources before external discovery.
4. Build P0 Phuket developer commercial-terms checklist.
5. Refresh `RESUME-STATE.md` after these checkpoints.
