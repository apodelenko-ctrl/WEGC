# MIRA — canonical launch dashboard

Source commit: `d40eb812857e8d0983958f676661b07619a56eb0`.

Repository evidence only; not a live CRM and not a claim that unobserved activity is zero. Focused route review is separate from the inherited 50 reviews; 100 source rows are not 100 currently verified agency identities.

**No launch-readiness assertion.** Implemented code, deployed behavior and commercial evidence are separate.

## Product

| Capability | Source implementation | Deployment |
|---|---|---|
| public_landing | implemented_code | not_verified |
| application | implemented_code_collection_closed | not_verified |
| authentication | implemented_code_not_deployed | not_verified |
| agency_profile | implemented_code | not_verified |
| markets_catalogue | implemented_code | not_verified |
| developer_catalogue | implemented_code | not_verified |
| project_catalogue | implemented_code | not_verified |
| filters | source_limited | not_verified |
| project_detail | implemented_code | not_verified |
| source_metadata | implemented_code | not_verified |
| client_registration | implemented_code_supply_gate_closed | not_verified |
| lead_status | implemented_code | not_verified |
| lead_protection | implemented_code | not_verified |
| deal_status | implemented_code | not_verified |
| commission_status | implemented_code | not_verified |
| payment_request | implemented_code | not_verified |
| documents_materials | implemented_code_storage_closed | not_verified |
| onboarding | implemented_code_and_runbook | not_verified |
| admin_workflow | implemented_code_partly_manual | not_verified |

## Research coverage

| Counter | Observed repository rows |
|---|---:|
| phuket_source_rows | 618 |
| phuket_normalized_coverage_rows | 618 |
| phuket_seed_mappings_preserved | 45 |
| phuket_generator_family_candidates | 66 |
| phuket_operator_only_rows | 1 |
| phuket_family_unresolved_rows | 507 |
| phuket_project_legal_sellers_verified | 0 |
| phuket_projects_enabled_for_registration | 0 |
| phuket_group_master_rows | 40 |
| phuket_p0_public_evidence_groups | 8 |
| russia_source_backed_accounts | 100 |
| russia_live_review_rows_inherited | 50 |
| russia_launch_cohort_live_review_matches | 50 |
| russia_live_review_join_exceptions | 0 |
| russia_explicit_alias_joins | 3 |
| russia_named_route_signals_in_cohort | 21 |
| russia_inherited_owner_review_ready | 13 |
| russia_owner_review_wave_accounts | 12 |
| russia_send_approved_in_source_wave | 0 |
| russia_classification_coverage | 100 |
| russia_needing_live_review | 50 |
| russia_segment_holds | 56 |
| focused_route_reviewed_accounts | 21 |
| focused_route_new_focused_reviews | 18 |
| focused_route_reused_cp05_reviews | 3 |
| focused_route_named_direct_routes | 10 |
| focused_route_accounts_with_named_direct_route | 7 |
| focused_route_ready_for_owner_review | 15 |
| focused_route_held_accounts | 6 |
| focused_route_entity_mismatch_holds | 1 |
| focused_route_wave12_draft_candidates | 10 |

## Business operations

Business KPI values remain unknown without a defined operational dataset. Stage-journal counts below count agency/developer entities with an explicit observation, NOT numbers of clients, transactions or payments. Missing stages are not backfilled. No conversion rates or financial totals are computed.

| Entity scope / observed stage | Entities evidenced in imported journal |
|---|---:|
| No private journal imported | unknown |

## Controls and next actions

- Owner approval required before any external outreach or forms.
- Secure backend deployment and live receipt/access QA remain unverified.
- Real operating events have not been imported; conversion rates cannot be calculated.
- Focused route review preserves one positive domain/entity mismatch (Monolit: inherited domain identifies a woodworking business). Do not release that account without identity correction.
- Ten named direct contacts cover seven accounts; shared offices and franchise-opening routes are not counted as direct decision routes. All draft contacts remain unapproved and untested.
- Primary private supply documents have been reviewed separately; a complete current seller/inventory/registration gate is not imported or enabled.
- Protected material delivery code requires a new private R2 bucket, reviewed per-asset rights/release evidence and explicit enablement.
- Owner-held operator events must remain outside this public repository.

Research register is generated. Operator events remain in a separate private journal. A changed generated register blocks rebuilding instead of losing manual updates. See `OPERATOR-JOURNAL.md`.
