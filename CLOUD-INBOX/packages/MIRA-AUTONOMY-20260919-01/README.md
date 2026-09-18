# Autonomous MIRA: first executable checkpoint

Standard-library Python 3; no dependencies, credentials, network calls, CRM writes or sending.

From repository root:

```sh
python CLOUD-INBOX/packages/MIRA-AUTONOMY-20260919-01/registry.py
python -m unittest discover -s CLOUD-INBOX/packages/MIRA-AUTONOMY-20260919-01 -p 'test_*.py' -v
```

Inputs: existing developer master/aliases, current Phuket catalog, public field observations. Outputs: reproducible research projection under `project-bible/mira/research/developer-expansion-2026-09-19`. Do not hand-edit generated JSON. Every existing developer/project ID is retained. Unresolved/ambiguous mappings remain visible; contracts and send/reply totals are null pending private CRM reconciliation.

`plan_inquiry(case, link, developer, agreement)` is a pure planner for future integration with the existing OMNI outbox. Inputs must come from trusted server-side CRM reads, not a request body or model. The contract adapter owns date/project/seller verification; it must not trust LLM-provided `valid_at_request`. Result is draft-only. `idempotency_key` needs a unique database constraint in the existing durable outbox before live integration. The function by itself provides no durable dispatch, API, event loop, retries, delivery, or CRM connection.

Known gaps: legal-seller/evidence validation must be enforced by CRM adapter; 618 Phuket projects only; other 60 published market records are next; remaining pilot/QA/stage sources need field-by-field reconciliation; old research contacts are not freshly verified; private mail details not embedded. Case correlation and reply processing are defined in roadmap but not implemented in this package.

14 local tests passed on real repository data plus clearly synthetic inquiry fixtures. Live acceptance NOT_RUN. Use existing MIRA-OMNI-20260918-01 and MIRA-CLOSEOUT tasks; do not create a second CRM or transport.
