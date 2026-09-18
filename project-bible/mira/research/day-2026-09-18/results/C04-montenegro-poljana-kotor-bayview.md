# C04 — Montenegro: Poljana Olive Homes + Kotor Bayview source/agency closure

Checked: **2026-09-18, Asia/Bangkok**. Scope: discovery/source validation only. No outreach, no seller/legal clearance, no availability/price/commission claim, no media permission, no deployment.

## Result

Both remaining records in this block now have a current exact-project primary route plus an independent exact-project real-estate observation. Recommendation: move both from `partial_for_validation` to **`complete_for_discovery_after_validation`** in the reviewed import, while keeping `legalSeller=null`, `commercialStatus=research_only`, `commerciallyEnabled=false`, and all media rights unresolved.

This changes the research-quality recommendation across the 30 Vietnam+Montenegro records from **25 complete / 5 partial** to **27 complete / 3 partial**. The remaining partials are Waterpoint, Merit Starlit and Porto Budva. This count is not a local import, publication, live inventory, seller authorization or contract.

## 1) Poljana Olive Homes Pool Residence — `me-poljana-olive-homes`

### Current first-party evidence

**Montenegrimmo project page:**  
https://montenegrimmo.com/poljana-olive-homes-pool-residence/  
Checked 2026-09-18. The current page identifies Poljana Olive Homes Pool Residence as a Montenegrimmo project and lists Montenegrimmo D.O.O. contact/office details. It describes the project as townhouses/pool residences on the Budva Riviera/Reževići route. This supports `developerBrand=Montenegrimmo` / `developerGroup=Montenegrimmo D.O.O.` at discovery level.

**Montenegrimmo portfolio page:**  
https://montenegrimmo.com/  
Checked 2026-09-18. Current portfolio navigation includes Poljana Olive Homes and the footer identifies Montenegrimmo D.O.O. The page also contains broad marketing statements about residence, tax and investment; those are **not** imported into MIRA facts.

**Exact project microsite:**  
https://poljana-olive-homes.com/  
Checked 2026-09-18. Current exact-project page is live and branded “Poljana Olive Homes by Montenegrimmo.” It contains changing price/down-payment/yield/residency-style marketing claims. These are quarantined from MIRA discovery data because this block does not verify commercial terms, legal/tax treatment or current buyer eligibility.

### Independent exact-project agency observation

**Astra Real Estate — Poljana Olive Homes – Luxury Townhouses for Sale:**  
https://astrarealestate.me/property/poljana-olive-homes-luxury-townhouses-for-sale/  
Checked 2026-09-18. This is an independent real-estate agency page naming Poljana Olive Homes in Reževići/Budva and describing the townhouse project. It is sufficient as an exact-project agency observation for discovery. Its price, residency and return/investment language is **not** adopted as a MIRA fact.

Additional marketplace observations exist, including Morizon/FazWaz/Booking, but they are not needed to inflate `agencyPublisherCount`; marketplace/hospitality syndication is weaker than the direct agency source above.

### Recommended record delta

- `validationStatus`: `partial_for_validation` → `complete_for_discovery_after_validation`
- `primarySource`: prefer `https://montenegrimmo.com/poljana-olive-homes-pool-residence/` (retain microsite as supporting first-party source)
- `agencySources`: add `https://astrarealestate.me/property/poljana-olive-homes-luxury-townhouses-for-sale/`
- `agencyPublisherCount`: 0 → 1
- `district`: keep conservative `Reževići / Budva Riviera near Sveti Stefan`; do not over-specify cadastral/legal address from marketing copy
- `legalSeller`: remain `null`
- `publicationApproved`: remain `false`

### Holds

- Exact legal seller/contracting entity for a purchase has **not** been established.
- Current sale availability, prices, taxes, residency eligibility, completion status and returns are **not** validated by this block.
- No media reuse permission was identified; project-page imagery is not publication-approved for MIRA.

## 2) Kotor Bayview Residence — `me-kotor-bayview`

### Current first-party evidence

**Exact project site:**  
https://www.kotorbayview.com/  
Checked 2026-09-18. The current page identifies **ARS INTERTRADE** under “PROPERTY DEVELOPER” and describes Kotor Bayview Residence in Muo, Montenegro. This supports the project/developer association at discovery level. It does **not** establish the legal seller for a buyer transaction.

The page currently describes one-, two- and three-bedroom suites/residences and a Muo/Kotor location. Commercial/pre-sale language is mutable and therefore not promoted into availability or price claims.

### Independent exact-project agency observation

**First Realty — Apartments in the new complex Kotor Bayview:**  
https://1realty.me/en/properties/apartments-in-the-new-complex-kotor-bayview/  
Checked 2026-09-18. First Realty identifies itself as a Montenegro real-estate agency and has an exact project listing titled Kotor Bayview in Muo/Bay of Kotor. This is a concrete independent agency observation of the exact project.

The listing contains a current asking price and sales language; those values are intentionally excluded from MIRA because this task does not verify inventory or current commercial terms.

### Recommended record delta

- `validationStatus`: `partial_for_validation` → `complete_for_discovery_after_validation`
- `primarySource`: keep `https://www.kotorbayview.com/`
- `developerBrand`: keep `ARS Intertrade`
- `agencySources`: add `https://1realty.me/en/properties/apartments-in-the-new-complex-kotor-bayview/`
- `agencyPublisherCount`: 0 → 1
- `district`: keep `Muo / Kotor Bay`; exact transaction address not inferred
- `legalSeller`: remain `null`
- `publicationApproved`: remain `false`

### Holds

- ARS Intertrade is identified as developer on the first-party site; legal seller/contracting entity remains unknown.
- Current unit availability, price, completion/construction state and buyer terms are not validated.
- First Realty images and project-site images are evidence of project observation, not publication permission for MIRA.

## Proof-level note

`exact current primary page + independent exact-project agency observation` is enough here only for **discovery confidence**. It is not evidence of a developer agreement, right to market, buyer registration, current inventory, legal seller, commission, title, residency/tax treatment or media licence.
