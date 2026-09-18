# LOCAL-AGENT-HANDOFF — MIRA night research 17–18 Sep 2026

## Purpose

Research/data handoff only. **Do not merge/deploy this branch as-is.** Local Codex remains the sole production integrator/deployer. Current `main` already reports 648 public research records (618 Phuket + 15 Bali + 15 Dubai), PR #10 merged, live owner/operator browser checks, and a later release-verification run that still requires follow-up. This night package does not alter that state.

## Deliverables

- `vietnam-projects.json` — 15 normalized Vietnam research rows; 14 complete-for-discovery, 1 partial (`Waterpoint`).
- `montenegro-projects.json` — 15 normalized Montenegro research rows; 10 complete-for-discovery, 5 partial.
- `russia-agencies.csv` — compact canonical index of 50 night Russia candidates. Full contact/segment/source detail remains in `03-russia-a.csv` and `04-russia-b.csv`.
- `belarus-agencies.csv` — compact canonical index of 30 night Belarus candidates. Full legal/source/contact detail remains in `05-belarus-agencies.csv`.
- `source-observations.json` — fresh public retrieval checks plus provenance pointers.
- `MEDIA-GAPS.md` — delta for five Bali/Dubai media gaps; baseline main file remains authoritative for the other 25 rows.
- `VALIDATION.json` — machine parse/count/uniqueness/gate checks for the consolidated package.
- Existing detailed source files `00-*` through `06-*` remain part of the evidence chain.

## Project integration rule

The normalized country JSON files intentionally stay **research-only**:
- `commercialStatus=research_only`
- `commerciallyEnabled=false`
- `publicationApproved=false`
- no prices, current inventory, yield/return, commissions, foreign-buyer eligibility, seller appointment or MIRA partnership were inferred.

Current public catalogue schema (`mira/catalog/data.json`) uses at least `id`, `name`, `district`, `kind`, `family`, `image`, `imageStatus`, `commerciallyEnabled`. Suggested mapping:

| research field | public field | rule |
|---|---|---|
| `id` | `id` | preserve stable night ID unless local namespace rules require a deterministic prefix migration |
| `name` | `name` | exact researched project name |
| `district` | `district` | preserve as research location; normalize administratively only where evidence exists |
| `developerBrand` | `family` | safe brand-level mapping; do not treat as verified legal seller |
| `propertyTypes` | `kind` | **manual deterministic mapping required**; mixed/hotel/branded-residence types must not be flattened blindly |
| `imageCandidate` | `image` | currently null; use only labelled cover or separately publication-approved asset |
| `commerciallyEnabled` | `commerciallyEnabled` | keep false |

Do not present the country JSON files as already tested against the catalogue generator. `VALIDATION.json` covers package parsing/counts, not live catalogue build/browser acceptance.

## Vietnam holds

`Waterpoint` remains the only partial row. Nam Long first-party identity is strong and a current developer publication names 17 strategic distribution agencies, but the night research did not establish a concrete Russian-language/Russian-speaking agency observation for the exact project. Do not invent one.

All other 14 rows are complete for the discovery stage only, not seller/inventory verified.

## Montenegro holds

Five rows remain partial:
1. `Heights` — exact independent listing found, but project-specific first-party closure is weaker than the other rows.
2. `Merit Starlit Hotel & Residence` — live current site, but stale 2023 opening language and residence/investment claims remain on-site; do not reuse them.
3. `Porto Budva` — current first-party/investor site remains live; independent current agency observation/status closure remains incomplete. Site return/discount/payment claims are not MIRA facts.
4. `Poljana Olive Homes Pool Residence` — current exact project/developer routes exist; independent agency observation/legal seller remain open.
5. `Kotor Bayview Residence` — current site identifies ARS INTERTRADE and project context; independent Russian-language agency observation/legal seller remain open.

Old Montenegro citizenship-by-investment copy remains quarantined.

## Agency use

### Russia
50 compact-index rows are present and unique by night ID and non-empty official domain. Six are flagged `owner_review=yes`: AFLAT, Welcome, Формула, HOUSE GROUP, БСН Недвижимость, РИЭЛ-МАКС. This is **not** outreach authorization.

Quality holds preserved:
- Аурум — entity-metadata hold.
- Виктори — content-quality hold.
- Good House — secondary-confirmed; first-party recovery incomplete.

### Belarus
30 compact-index rows are present; six are flagged `owner_review=yes`: Абсолют Недвижимость, Центр недвижимости 24 на 7, Сектор недвижимости Основа, Гарант успеха, Агентство Уют и К, ПАКОДАН ЭСТЕЙТ.

Rows with empty `official_domain` are not errors: those entries are intentionally retained as Chamber/marketplace-backed research candidates whose corporate route still needs closure. Five organisations named in current official licence-suspension notices were **excluded** from the 30 and must stay excluded until authoritative status changes.

No outreach was sent. `outreach_status=not_authorized` remains the gate.

## Bali / Dubai media delta

Use the night `MEDIA-GAPS.md` only as a delta over main:
- ERA by OXO — exact current OXO page and exact-project asset URL found; no rights approval.
- Secana Beachtown — exact gallery candidate visually checked; Mirah terms require permission for commercial/public reuse.
- Mudon Al Ranim — two exact first-party gallery routes found; Dubai Properties terms require licence/written permission.
- One River Point — current Ellington project-source re-match closed; no replacement direct asset approved.
- DAMAC Riverside — Riverside Views images are quarantined as a different development.

**Publication-approved new media remains 0.**

## Recommended local integration sequence

1. Do not interrupt the current admin/release follow-up. Finish the local agent's existing CI/live acceptance first.
2. Import Vietnam/Montenegro only on a new isolated data branch after mapping `propertyTypes -> kind`.
3. Generate labelled country/project covers if exact licensed imagery is unavailable; never imply a cover is a project photograph.
4. Run the same catalogue build, route generation, shortlist/filter/back-navigation and desktop/mobile browser suites used for Bali/Dubai.
5. Keep funnel messaging Phuket-only unless the owner separately changes that strategy.
6. Keep all new project rows research-only and commercially disabled.
7. Ingest Russia/Belarus into the agency research/CRM layer only after comparing against the local agent's newest post-night CRM state; this branch deduped against the repository state available during the night, not any unpublished local work.
8. Do not send agency messages/forms until separate owner approval.

## Acceptance boundary

This package is ready for **local integration review**, not production publication. Machine validation proves file parse/count/uniqueness/gates for the consolidated package. It does not prove legal seller status, image rights, every external URL, production browser behavior or a successful deployment.
