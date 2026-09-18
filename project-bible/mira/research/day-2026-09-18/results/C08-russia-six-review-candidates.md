# C08 — Russia: six owner-review candidates rechecked

**Checked:** 2026-09-18, Asia/Bangkok. **Start checkpoint:** 11:57 +07:00.  
**Scope:** the six records already marked `owner_review=yes` in the night compact index. No broad recollection, no private contacts, no outreach, no commercial activation.

## Method and proof boundary

- Reused the stable IDs from `night-2026-09-18/russia-agencies.csv` and detail rows from `03-russia-a.csv` / `04-russia-b.csv`.
- Reopened current first-party corporate sites on 18.09.2026 to check that the corporate route and stated business segment still exist.
- Re-ran exact-domain search against the repository's current default branch (`main` still `1b5e6cc053bd4b20a47c3f4231c56bb1f05d850b`). All six exact domains returned no repository search hit. This is only an exact-text/main check: it **does not** establish legal-entity uniqueness, rebrand uniqueness or absence from an unpublished local CRM.
- Public contact routes are recorded as corporate pages/sites only. Personal employee contacts are intentionally excluded.
- `owner_review` means internal review candidate only. `outreach_status` remains `not_authorized`; `commercial_status=research_only`; `commerciallyEnabled=false`.

## Rechecked candidates

| Stable ID | Brand / city | Current first-party evidence | Segment recommendation for owner review | Corporate route | Current unknown / hold | Main exact-domain search |
|---|---|---|---|---|---|---|
| `RU-NIGHT-A-005` | **AFLAT**, Vladivostok | https://aflat.online/ — current site explicitly exposes `Таиланд` as a service alongside new-build/residential services; checked 18.09.2026 | **international-experience / new-build**. Strongest direct foreign-market signal in this six; it proves the agency publicly markets Thailand, not that it has a MIRA agreement or the same developer supply | https://aflat.online/ (current corporate site with Contacts route) | Exact decision-maker, foreign-partner model, current Thailand supply/agreements and buyer demand volume unknown | `aflat.online` → no hit |
| `RU-NIGHT-B-003` | **Welcome**, Stavropol | https://www.welcome26.ru/ — current new-build catalogue; site states official developer partnerships and publishes developer sales/marketing project cases; checked 18.09.2026 | **new-build / developer-sales B2B adjacency**. Useful for proposition around adding an overseas direction to an already developer-facing sales organisation | https://www.welcome26.ru/ (corporate site / Contacts navigation) | No verified foreign desk or Phuket demand; site marketing-case claims are not independent performance verification | `welcome26.ru` → no hit |
| `RU-NIGHT-B-005` | **Агентство на Ярославской / HOUSE GROUP**, Cheboksary | https://housegroup21.ru/ — active first-party catalogue; public request feed still includes a 10.11.2025 request for property in Spain; checked 18.09.2026 | **regional residential + inbound foreign-demand signal**. Treat Spain line only as evidence that a foreign-property enquiry appeared in the agency's own feed | https://housegroup21.ru/ and the existing `/contacts/` corporate route from the source record | Agency scale and ability/intent to service foreign property are not established; one enquiry is not a foreign desk or recurring demand | `housegroup21.ru` → no hit |
| `RU-NIGHT-B-009` | **РИЭЛ-МАКС**, Bryansk | https://riel-max.ru/ — current site explicitly offers new-build selection; https://riel-max.ru/kontakty remains a central corporate contact page; checked 18.09.2026 | **regional new-build / full-service**. Suitable for the core MIRA message rather than an "already international" angle | https://riel-max.ru/kontakty | No verified international desk, overseas enquiry or named partnership decision-maker | `riel-max.ru` → no hit |
| `RU-NIGHT-B-011` | **БСН Недвижимость**, Bryansk | https://bsnnedvizhimost.ru/ — current site says company works since 2014 and specialises in secondary housing, new-build sales and commercial property; checked 18.09.2026 | **regional established new-build / full-service** | https://bsnnedvizhimost.ru/ (current central corporate route) | No verified foreign desk/demand; exact partnership owner not identified | `bsnnedvizhimost.ru` → no hit |
| `RU-NIGHT-B-012` | **Формула**, Tyumen | https://formula-agency.ru/ — current dedicated new-build portal, current news dated 14.09.2026, and current footer identifies operator `ООО "НЕОЛИТИКА"`; checked 18.09.2026 | **new-build specialist / structured developer catalogue**. Strong product-fit for an agency that already sells developer inventory | https://formula-agency.ru/ (Contacts & requisites navigation on current site) | Brand-to-legal-operator relationship is first-party stated, but no MIRA relationship or foreign desk is established; partnership decision-maker unknown | `formula-agency.ru` → no hit |

## What changed versus the night handoff

1. **AFLAT foreign-market signal is now freshly revalidated** from the current site: Thailand remains a visible service on 18.09.2026.
2. **Welcome B2B adjacency is stronger than a generic new-build label**: the current site includes developer sales/marketing cases and states developer-partner positioning. This still does not prove foreign-market demand.
3. **HOUSE GROUP keeps an evidence-backed but deliberately narrow international signal**: one Spain request in its own public request feed. Do not promote this to `foreign_desk=confirmed`.
4. **RIEL-MAX, BSN and Formula remain clean new-build/full-service targets** with current corporate routes; no foreign-market claim was added.
5. The six exact domains still have **zero exact text hits in current main repository search**. The earlier 52-CSV exact-domain result is therefore not contradicted by the current default branch, but unpublished local CRM/legal/rebrand dedupe remains for LOCAL.

## C10 handoff fields

Recommended internal grouping for the 12-candidate owner pack (not an outreach order):

- `international_signal`: AFLAT.
- `inbound_foreign_demand_signal_only`: HOUSE GROUP.
- `newbuild_b2b_fit`: Welcome, RIEL-MAX, BSN Недвижимость, Формула.

For each, retain `sendApproved=false`, `outreach_status=not_authorized`, `commercial_status=research_only`, and a single factual personalization hook from the table. Do not use current listing prices, client names, private employee details, claimed conversion results or developer agreements as outreach facts.

## Sources checked 18.09.2026

- Night compact index: `project-bible/mira/research/night-2026-09-18/russia-agencies.csv`.
- Night detailed evidence: `03-russia-a.csv`, `04-russia-b.csv`.
- AFLAT: https://aflat.online/
- Welcome: https://www.welcome26.ru/
- HOUSE GROUP: https://housegroup21.ru/
- RIEL-MAX: https://riel-max.ru/ and https://riel-max.ru/kontakty
- БСН Недвижимость: https://bsnnedvizhimost.ru/
- Формула: https://formula-agency.ru/
- GitHub exact-domain searches on current default branch for: `aflat.online`, `welcome26.ru`, `housegroup21.ru`, `riel-max.ru`, `bsnnedvizhimost.ru`, `formula-agency.ru` → zero hits in this run.

**Result:** C08 complete as route/segment/repository-dedupe recheck. No external action performed.