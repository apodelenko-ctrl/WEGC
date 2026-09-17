# 02:00 — Vietnam / Montenegro validation and media-source pass

Checked: 18 September 2026, Asia/Bangkok.

## Result

Reviewed all **30** saved project records from the 00:00 Vietnam and 01:00 Montenegro slots against current public sources and current main context.

- Vietnam: **14 complete for the discovery layer / 1 partial** after validation.
- Montenegro: **10 complete for the discovery layer / 5 partial** after validation.
- 30 exact project media source pages/documents are now recorded as candidates.
- 0 direct third-party image files were downloaded.
- 0 new media assets were visually reviewed in this cloud slot.
- 0 publication permissions were inferred; every new media candidate remains `publication_approved=false`.
- all 30 projects remain `commercial_status=research_only`, `commerciallyEnabled=false`.

`02-project-validation.json` contains the project-by-project evidence and cautions. `02-project-validation.csv` is the flat status/media-source table.

## Vietnam closures

Three of the four prior partials were materially improved:

1. **Aqua City — Phoenix Island** — phase-level first-party evidence is now strong enough for the discovery layer. Novaland's 2023 annual report explicitly lists `Aqua City Phoenix Island`, identifies project entities and product types; 2024 AGM material again names the Phoenix Island phases. Older Novaland investor decks contain a clearly labelled Phoenix Island visual. Historical handover/sales figures were not treated as current.
2. **Empire City** — Keppel Real Estate maintains an exact Empire City project page, closing the prior absence of a first-party consortium-partner source. Legal seller and current inventory remain unverified.
3. **Urban Green** — Kusto Group corporate material explicitly identifies Urban Green as a Kusto Home residential complex, closing the corporate-developer gap.

**Waterpoint** remains partial only because this pass did not establish a concrete Russian-language/Russian-speaking *agency/property-channel* observation for the exact Waterpoint project. Strong Nam Long primary evidence remains. Russian-language editorial material about Solaria Rise / Waterpoint exists, but it is not converted into agency evidence.

## Montenegro closures and holds

Upgraded after current-source checks:

- **Mountain Retreat by Dukley** — exact Dukley project page plus a current independent agent project page were found. Agent availability claims are not copied into MIRA facts.
- **Bellemond Residence** — exact project site plus current independent brokerage/development-catalogue observations establish project identity; legal seller remains unknown.
- **Montis Mountain Resort by Splendid** — current resort site plus independent 2025–2026 coverage establish an active project/resort context. Old citizenship-by-investment language remains quarantined and must not be reused.

Still partial:

- **Heights / Luštica Bay** — a current exact independent listing exists, but a project-specific first-party page was not established in this pass.
- **Merit Starlit** — primary site is live and still markets residences, but contains stale historical schedule/immigration language and no current independent agency observation was established.
- **Porto Budva** — current investor/developer site is live; sufficiently current independent project observation remains missing.
- **Poljana Olive Homes** — exact project and Montenegrimmo corporate pages are live; independent agency observation remains missing.
- **Kotor Bayview Residence** — exact current site identifies ARS Intertrade and shows a pre-sale context; independent Russian-language agency observation remains missing.

## Repository-level duplicate context

Current main reports the published catalogue at 648 records for Phuket plus Bali/Dubai; Vietnam and Montenegro are not published catalogue markets. Main already has **developer-level Vietnam supply/actionable records** (for example Vinhomes, Novaland, Sun Group, Nam Long and Masterise Homes). Those are expected provenance overlaps, not duplicate project cards. Exact-name searches for the four previously partial Vietnam rows returned no main project rows. Repository search returned no Montenegro research/catalogue layer on main, and exact-name checks for previously partial Montenegro rows returned no main project rows.

No row was removed as a project-level duplicate in this pass. The 07:00 consolidation slot still owns full schema/link validation and final import mapping.

## Media discipline

Each project now has an exact project source page/document suitable for *media review sourcing*. This is deliberately not the same as a usable public image. `image_url` stays null unless a direct asset URL is reliably captured; `downloaded=false`, `visual_reviewed=false`, `publication_approved=false` for every row. Public accessibility alone is not a rights basis.

Especially useful exact media sources found during validation include:

- Novaland investor documents with an explicitly labelled Phoenix Island image;
- Keppel's exact Empire City project page;
- Kusto Group's Urban Green corporate/project article;
- current exact project/resort pages for Kotor Bayview, Merit Starlit, Bellemond, Porto Budva, Poljana Olive Homes and Montis.

## Next

03:00 priority is Russia expansion pass A. Do not replay Vietnam/Montenegro discovery. At 06:00 revisit remaining quality/media gaps if time permits; at 07:00 consolidate validated country datasets and map them to the current catalogue import contract without deployment.
