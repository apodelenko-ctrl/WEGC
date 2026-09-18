# C09 — Belarus: six owner-review candidates rechecked

**Checked:** 2026-09-18, Asia/Bangkok.  
**Scope:** the six records already marked `owner_review=yes` in the corrected 30-record Belarus dataset. The malformed historical detailed CSV is not used for facts. No private contacts, no outreach, no legal-clearance claim.

## Regulatory proof rule used in this block

Belarus licensing status is treated as a separate mutable fact, not inferred from a corporate website, a marketplace listing or Chamber presence.

Current professional/regulatory context rechecked on 18.09.2026:

- Law of the Republic of Belarus dated 08.05.2025 No. 71-Z on real-estate brokerage activity is the current sector framework with its core provisions in force from 16.05.2026; Ministry of Justice remains the licensing/control authority under the new regime.
- The current Chamber of Realtors site reports recent Ministry of Justice licence suspensions on 21.08.2026 and 01.09.2026, demonstrating that historical licence numbers or current market activity do not prove an organisation's present licence status.
- The Chamber's current realtor register can corroborate that an attested realtor currently lists an organisation as workplace, but this is not a substitute for organisation-level active-licence verification.

**Important:** this run did **not** retrieve an authoritative Ministry organisation-level active-licence lookup for these six legal entities. Therefore every organisation below keeps `licensing_status=not_independently_verified_current`. First-party licence numbers are recorded only as self-published evidence, not converted to a legal-clearance conclusion.

Regulatory references checked 18.09.2026:
- https://www.prrb.by/
- https://www.prrb.by/realtors
- https://www.prrb.by/articles/priostanovleny-licenzii-rielterskih-organizacij (02.09.2026; Ministry decision dated 01.09.2026)
- https://www.prrb.by/articles/priostanovleny-licenzii-treh-rielterskih-organizacij (24.08.2026; Ministry decision dated 21.08.2026)

## Repository dedupe boundary

Re-ran exact-domain searches against the repository's current default branch; `main` is still `1b5e6cc053bd4b20a47c3f4231c56bb1f05d850b`. All six exact domains returned zero hits. This does **not** prove legal-entity/rebrand uniqueness or absence from unpublished LOCAL CRM.

## Rechecked candidates

| Stable ID | Brand / city | Current first-party evidence | Owner-review segment | Regulatory evidence state | Corporate route | Main exact-domain search |
|---|---|---|---|---|---|---|
| `by-centr-nedvizhimosti-24-na-7` | **Центр недвижимости 24 на 7**, Borisov / Minsk region | https://central-borisov.by/ — current site says it works across Minsk region and offers residential/new-build purchase services; footer self-publishes UNP and licence `02240/507` dated 29.05.2025 | **Minsk-region residential/new-build** | Licence number is **first-party self-published only**; current active organisation licence not independently verified in Ministry source | https://central-borisov.by/ | `central-borisov.by` → no hit |
| `by-osnova` | **Сектор недвижимости Основа**, Gomel | https://osnova.by/ — current reachable site identifies ODO, full-service sale/purchase/exchange/rental and self-states Ministry licence `02240/128` from 03.08.2006; current Chamber register also shows an attested realtor with workplace ODO `Сектор недвижимости "Основа"` | **Gomel full-service regional** | Historical/first-party licence statement + current professional-presence corroboration; **not** organisation-level active-licence clearance | https://osnova.by/ | `osnova.by` → no hit |
| `by-absolut-nedvizhimost` | **Абсолют Недвижимость**, Minsk | https://aan.by/ and https://aan.by/contacts/ — current site identifies ООО `Абсолют Недвижимость`, UNP 193547698, broad sale/purchase/rent/exchange services and a central corporate route | **Minsk broad-service / transaction-support** | No current organisation-level Ministry licence verification retrieved; do not infer from active site or team labels | https://aan.by/contacts/ | `aan.by` → no hit |
| `by-garant-uspeha` | **Гарант успеха**, Brest | https://garantus.by/ — current site is active with 2026 reviews and current catalogue pages; exact night record already maps the corporate route | **Brest established regional full-service** | Active site/current listings do not establish current licence status. No Ministry organisation-level verification retrieved | https://garantus.by/ | `garantus.by` → no hit |
| `by-uyut-i-k` | **Агентство Уют и К**, Vitebsk | https://n-v.by/ plus https://n-v.by/kontakty/ — current site shows broad residential/commercial/transaction-support services; 29.01.2026 news records office relocation to Mark Shagal 7A and current contact route | **Vitebsk full-service / transaction-support** | Site says it operates under Belarus law; this is not a current licence lookup. No organisation-level Ministry verification retrieved | https://n-v.by/kontakty/ | `n-v.by` → no hit |
| `by-pakodan-estate` | **ПАКОДАН ЭСТЕЙТ**, Grodno | https://pakodangrodno.by/ — current site identifies ООО `Агентство недвижимости ПАКОДАН ЭСТЕЙТ`, calls itself part of an international brand/network and says it works with partners in Russia; current Chamber register includes an attested realtor whose workplace is this legal entity | **Grodno regional + international-network signal** | International-brand wording and current realtor workplace evidence do not prove foreign desk, partner rights or current organisation licence status. No Ministry organisation-level active licence verification retrieved | https://pakodangrodno.by/ | `pakodangrodno.by` → no hit |

## What changed versus the night handoff

1. The six candidates remain **owner-review worthy**, but C09 now adds an explicit regulatory proof state instead of leaving Chamber presence adjacent to an implied licensing conclusion.
2. `Центр недвижимости 24 на 7` and `Основа` publish licence numbers on their own current sites. These are stored as `first_party_self_stated`, **not** `current_licence_verified`.
3. `Основа` and `ПАКОДАН ЭСТЕЙТ` have current Chamber realtor-register evidence tying at least one attested realtor to the organisation. This proves current professional-register presence, not active company licence status or MIRA clearance.
4. `ПАКОДАН ЭСТЕЙТ` retains an international-network signal from its own site, but no foreign agency programme, Phuket capability or MIRA relationship is inferred.
5. Exact-domain search in current main remains zero for all six; unpublished local CRM/legal/rebrand dedupe is still a LOCAL acceptance step.

## C10 handoff fields

Keep all six in the 12-candidate owner-review package with:

- `sendApproved=false`;
- `outreach_status=not_authorized`;
- `commercial_status=research_only`;
- `licensing_status=not_independently_verified_current` unless LOCAL later attaches authoritative current regulator evidence;
- one factual segment hook only from the table;
- `international_signal` only for `by-pakodan-estate`, qualified as **self-described network/partner signal**, not a verified overseas desk.

Do not use personal realtor names/phones from the Chamber or corporate staff pages in the public owner-review pack. Corporate routes are sufficient at this stage.

## Source provenance

- Correct structured source: `project-bible/mira/research/night-2026-09-18/05-belarus-agencies.json` (30 records).
- Compact owner-review selector: `project-bible/mira/research/night-2026-09-18/belarus-agencies.csv`.
- **Do not use** the malformed historical detailed `05-belarus-agencies.csv` for import/facts.
- Current corporate sources: https://central-borisov.by/ ; https://osnova.by/ ; https://aan.by/ ; https://aan.by/contacts/ ; https://garantus.by/ ; https://n-v.by/ ; https://n-v.by/kontakty/ ; https://pakodangrodno.by/.
- Current Chamber/regulatory context URLs listed above.
- GitHub exact-domain searches on current default branch for the six domains → zero hits in this run.

**Result:** C09 complete as route/segment/current-evidence review. No licence clearance, external contact or commercial activation was performed.