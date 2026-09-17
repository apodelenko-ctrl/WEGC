# 01:00 — Montenegro discovery and classification

Checked: 18 September 2026, Asia/Bangkok.

## Result

Saved **15 real Montenegro project records** for the research lane. This is a targeted, non-random catalogue sample, not a sales ranking, not evidence of MIRA contracts, and not current inventory.

Discovery quality at this checkpoint:

- **15** records saved;
- **7** marked `complete_for_discovery` for this stage;
- **8** deliberately retained as `partial_for_validation` rather than overclaimed;
- **0** media files downloaded;
- **0** new media files visually reviewed;
- **0** media items publication-approved;
- every row remains `commercial_status=research_only` and `commerciallyEnabled=false`.

The sample covers **11 developer/project families** across Tivat/Porto Montenegro, the Luštica peninsula, Portonovi/Kumbor, Budva/Bečići/Zavala, Muo/Kotor Bay and Kolašin. Repeated master developments are explicit: Vero & Versa and Boka Place both belong to Porto Montenegro; The Peaks and Heights belong to Luštica Bay; Portonovi Residences and One&Only Private Homes are within Portonovi; Dukley Gardens and Mountain Retreat belong to Dukley. They are not counted as independent developers merely to inflate variety.

## Stronger discovery rows

The seven rows currently considered complete for the discovery stage are Boka Place, Vero & Versa, The Peaks, Portonovi Residences, One&Only Private Homes Portonovi, Dukley Gardens and Meliá Private Residences Budva. Each has a project/developer source and an external project observation; several also have a concrete Russian-language channel observation (Prian or MD Realty). An English-language brokerage page is recorded as English, not relabelled Russian.

## Rows held for 02:00 validation

- **Heights / Luštica Bay** — current Luštica Bay sales source confirms the collection, but a project-specific first-party page and an exact Russian-language agency observation still need closing.
- **Mountain Retreat by Dukley** — developer page is strong; current independent Russian-language agency observation and current sales status remain open.
- **Merit Starlit Hotel & Residence** — first-party residence page is strong; current independent Russian-language agency observation and current sales status remain open.
- **Bellemond Residence** — exact project site and Russian Realting observation exist, but the developer legal entity is not established from the project site.
- **Porto Budva** — Budva Investment Montenegro directly markets the project in English and Russian; an independent agency observation and current construction/delivery status are still open.
- **Poljana Olive Homes** — Montenegrimmo corporate/project sources and a Russian project page exist; independent agency observation is still open.
- **Kotor Bayview Residence** — project site names ARS Intertrade as developer; independent Russian-language agency observation is still open.
- **Montis Mountain Resort by Splendid** — Golden Group sources confirm the project, but the current Russian/CIS marketing page still promotes Montenegro's expired citizenship-by-investment program. Those stale claims are explicitly quarantined and must not enter MIRA copy. Current project/sales status needs re-verification.

## Source discipline

Primary facts were taken from current project/developer sources including Porto Montenegro, Luštica Bay, Portonovi, Dukley, SUNRAF/Meliá Budva, Merit Starlit, Bellemond, Budva Investment Montenegro, Montenegrimmo, Kotor Bayview/ARS Intertrade and Golden Group. Russian-language observations include Prian, MD Realty, Realting and direct Russian project/developer pages where applicable. A publisher page proves that the publisher presents a project; it does not prove title, legal seller, available units, commission or seller appointment.

No price, availability, return, commission, completion promise, foreign-ownership eligibility, residence/citizenship entitlement or MIRA partnership was copied into the research layer. In particular, stale Montis citizenship claims and promotional return claims on project/developer sites are not treated as current facts.

## Files

The detailed JSON is split into three bounded files to avoid large single-write conflicts during the scheduled run:

- `01-montenegro-projects-part1.json`
- `01-montenegro-projects-part2.json`
- `01-montenegro-projects-part3.json`
- `01-montenegro-projects.csv` — flat review table
- `01-montenegro.md` — this checkpoint

The 07:00 consolidation slot should merge validated rows into the planned `montenegro-projects.json` after factual closure and deduplication.

## Next

02:00 should validate both Vietnam and Montenegro collections, close or replace partial rows, perform broader repository-level duplicate checks, and add exact media source-page/image candidates where available. Public accessibility is not publication permission: image URLs may be recorded, but no third-party bytes should be committed to public GitHub without an evidenced rights basis.
