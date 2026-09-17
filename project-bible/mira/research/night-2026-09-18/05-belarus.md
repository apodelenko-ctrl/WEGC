# 05:00 — Belarus agency expansion

Checked: 18 September 2026, Asia/Bangkok.

## Result

Saved **30 net-new Belarus agency candidates** for the research layer after checking the current Belarus/CIS seed and related mega/outreach datasets. This is a source-backed discovery layer, not an outreach-approved list and not proof that every row is a fully verified independent legal entity.

All rows remain:

- `commercial_status=research_only`;
- `commerciallyEnabled=false`;
- `outreach_status=not_authorized`.

No email, call, message, form or partnership request was sent.

## Dedupe scope

Before counting a row as new, the run inspected current repository sources including:

- `data/agencies-cis-pilot.csv`;
- `data/agencies-cis-verified.csv`;
- `data/agencies-cis-candidates.csv`;
- `data/agencies-cis-package-05.csv`;
- `data/agencies-cis-package-06.csv`;
- `data/mega-discovered.csv`;
- `data/mega-classified.csv`;
- `data/mega-verified.csv`;
- `sales/outreach-queue-template.csv`;
- `sales/mega-outreach-queue.csv`.

Already-known brands/routes such as Твоя столица, Этажи, Квадратный метр, Моя 7Я, Авангард, Мариэлт, Фаттория, Мегаполис, РиэлтКафе, Магазин недвижимости and Центр жилья were not padded into the new count. Regional branches of a known network were not counted as independent agencies merely because they have another city page.

Exact-domain/brand absence from these repository layers is a research dedupe result, not a legal-ownership conclusion.

## Source quality

The 30 rows deliberately retain different evidence grades rather than flattening them into “verified”:

- 8 — current professional-market evidence from the Belarus Chamber of Realtors directory, with the corporate route still to close;
- 6 — current first-party corporate source plus Chamber evidence;
- 6 — Chamber evidence plus a current marketplace/company observation;
- 4 — current first-party corporate sources outside the first two reviewed Chamber directory pages;
- 1 — Chamber plus an official route whose page returned an access/interstitial issue during this run;
- 1 — Chamber plus a corporate route that timed out;
- 1 — Chamber plus current marketplace evidence with an entity/rebrand hold;
- 1 — Chamber plus a directory-confirmed official route not directly retrieved in this run;
- 1 — Chamber plus a candidate corporate site with only medium site-to-entity match confidence;
- 1 — current first-party source with the legal entity/licensing metadata still unclosed.

The Chamber directory is used as current professional-market evidence. A company appearing there as an attested realtor's current employer does **not**, by itself, prove every licensing, corporate or commercial condition needed for MIRA onboarding. Personal realtor contact details from the directory were intentionally not copied.

## Useful owner-review candidates

For later owner review — **not authorization to contact** — the strongest current combinations of source quality and geographic/segment diversity include:

- Абсолют Недвижимость — Minsk, first-party contact route + Chamber;
- Центр недвижимости 24 на 7 — Borisov/Minsk region, first-party + Chamber;
- Сектор недвижимости Основа — Gomel, first-party + Chamber;
- Гарант успеха — Brest, first-party + Chamber;
- Агентство Уют и К — Vitebsk, current first-party activity;
- ПАКОДАН ЭСТЕЙТ — Grodno, first-party route and self-described international-brand positioning.

The last signal does not establish a foreign-property desk, an agency program, permission to contact or any MIRA relationship.

## Explicit holds

Five companies were **not counted** because current official Chamber notices report Ministry of Justice licence suspensions:

- Агентство недвижимости Эксперт;
- Агентство недвижимости Твой Дом;
- ЭРА-Недвижимости;
- БелЦТН;
- ВСП недвижимость-Инвест.

Sources:

- https://www.prrb.by/articles/priostanovleny-licenzii-rielterskih-organizacij
- https://www.prrb.by/articles/priostanovleny-licenzii-treh-rielterskih-organizacij

Other explicit quality holds remain in the saved dataset: `Группа компаний Эксклюзив` needs entity/rebrand closure; `ВАРИАНТ` needs exact site-to-entity closure; `RealtElite` needs legal-entity/licensing closure; several Chamber-only rows still need corporate general routes.

## Files

- `05-belarus-agencies.json` — structured 30-row dataset with source status, dedupe group, commercial gate and unresolved issues.
- `05-belarus-agencies.csv` — flat review/export form of the same candidate layer.
- `05-belarus.md` — this checkpoint.

## Next

06:00 should perform cross-lane quality/deduplication, inspect the existing Bali/Dubai `MEDIA-GAPS.md`, and improve only genuine media/source gaps without recollecting those 30 projects or treating public images as publication-approved assets.
