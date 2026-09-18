# Private reconciliation / AUT-04 preparation — B002

Status: prepared; no transfer, import, deployment or outbound message performed.
Owner: LOCAL remains product/deploy integrator until actual cloud restore and acceptance.

## Sources and storage boundaries

- Public research: agency master-agencies.json/CSV and contacts.json (348 provisional groups); developer master CSV (41 groups), public-contact-observations.json, generated developers/project-links JSON (618 Phuket IDs).
- Private operational source: LOCAL CRM snapshot 78 agency research / 87 developer research / 2 synthetic Accounts; 20 inactive templates. Counts overlap research and MUST NOT be summed.
- Private mail, people, contracts, business correspondence, credentials and execution history belong in private CRM/secure storage, never public Git. Public observations are not a replacement for this operational source.
- The 13 corporate PDFs in the owner-only vault are a separate asset set, not the CRM code/restore package or encrypted backup.

## Exact deliverable still needed from LOCAL

1. Secure code/restore package reference + immutable SHA256 + revision + dependency lockfile + restore instructions; redact all secrets from source package.
2. Secure encrypted-backup reference with SHA256 `48945a6b0ebee8d52bb9b4b32198119cdd78afb55a4578e6a62778de93a25140` from accepted closeout, or an explicitly versioned replacement with receipt. Key through a separate private channel, never Git. No need for another ACK or repeat of accepted local tests.
3. Private external-ID crosswalk, one row per actual native Account, with columns: entity_kind, native_account_id, native_external_id, public_research_id, legacy_source_ids, match_status, match_evidence_ref, operational_stage, stage_evidence_ref, latest_contact_at, first_contact_suppression, synthetic_flag, reconciliation_note. Use exact matches only; ambiguous/unmatched rows remain explicit. One-to-many relationships need explicit parent/group vs legal-entity distinction.
4. Botanica/The Title: reconcile actual private thread and agreement progress before outreach. Historical not_sent is not authoritative; suppress duplicate first contact until reconciled. Unknown contract states remain null, never signed=false by assumption.

## Cloud acceptance gate and next implementation step

Actual runtime access and transfer are absent. Do not buy/reinstall a VPS, change mail providers, deploy, or claim migration accepted. Once authorized private transfer and runtime exist, perform isolated restore, match native IDs through the private crosswalk, and return a sanitized restore receipt with revision/checksums/counts and live acceptance evidence. T14 remains prepared_not_migrated until that occurs.

Prepare idempotent imports as upserts keyed by stable research ID plus native external ID; reject collisions and preserve private operational stages. Test with synthetic rows before real import. Dashboard must expose separate counters for public candidates, native Accounts, unresolved mappings, unknown contracts, sent/replied events and catalog coverage; do not infer sent/replied from contact availability.

Public research may proceed independently. Future authenticated mail/DSN/complaint ingestion and inquiry dispatcher remain pending live acceptance; all generated inquiry plans in this branch are non-sending projections.
