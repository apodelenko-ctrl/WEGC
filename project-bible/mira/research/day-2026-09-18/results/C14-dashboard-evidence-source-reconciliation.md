# C14 — canonical dashboard evidence-source reconciliation proposal

**Checked:** 2026-09-18, Asia/Bangkok. **Run start:** 13:57:30 +07:00.  
**Scope:** research note only. No edit to `main`, generated dashboard, Worker/Access/D1/DNS, public pages or production state.

## Why C14 is needed

The canonical dashboard in current `main` still reports the application as `implemented_code_collection_closed`, authentication as `implemented_code_not_deployed`, and every product row as `deployment=not_verified`. Its control section also says secure backend deployment and live receipt/access QA remain unverified.

That output is now stale relative to newer accepted evidence, but the correct fix is **not** a manual edit of `LAUNCH-DASHBOARD.md`.

### Exact sources of the stale labels

1. `project-bible/mira/operations/LAUNCH-DASHBOARD.md` at current main `1b5e6cc053bd4b20a47c3f4231c56bb1f05d850b` is generated output and still shows the older states.
2. `scripts/mira-launch-operations.py` contains a static `PRODUCT` table with notes such as `live intake remains closed` and `implemented_code_not_deployed`; `product_rows()` assigns `deployment='not_verified'` to every capability regardless of newer deployment evidence.
3. `scripts/mira-launch-source.py` still emits the blocker `Secure backend deployment and live receipt/access QA remain unverified.`
4. Repository search confirms the same stale states are propagated into `operations/launch-dashboard.json`.

Therefore the source/generator layer must be reconciled before regeneration. Editing only the Markdown/JSON/HTML outputs would be overwritten by the next build and would break the provenance model.

## Newer evidence that must be distinguished, not flattened

### Repository/live release evidence in current main

`project-bible/mira/operations/AGENCY-INTAKE-OPERATIONS.md` records that the owner approved notice `mira-agency-2026-09-18-v1` and controlled agency intake, and defines the operator flow. It explicitly states that `Compose-email` only opens the operator's mail client; the application does not send mail or track sent-message history.

Current main `WORK-STATUS.md` records the published controlled-intake checkpoint, retained Worker/D1/Access resources, owner/operator access and successful release verification. It also keeps buyer registration/material delivery separately closed.

### Newer owner-reported live evidence in CLOUD-INBOX

`CLOUD-INBOX/START-HERE.md`, `QUEUE.json` and task `MIRA-LOCAL-20260918-02` preserve a newer owner-reported result: the invited ordinary test applicant logged in with their own OTP, submitted a technical application, received a durable server receipt, and the application survived refresh. CLOUD did not independently repeat that live test.

Still pending in that owner-reported path: operator decision, applicant-visible result, logout/re-login persistence. A technical applicant must not be promoted to active agency without real agreement evidence.

## Proposed evidence model for LOCAL

Do not use one string to mean code, deployment and business readiness. Generate each capability from four explicit dimensions:

| Dimension | Meaning | Example current proof |
|---|---|---|
| `implementation` | source/code exists | Worker/auth/admin source |
| `deployment` | deployed resource/version accepted | recorded Worker/Pages/Access release evidence |
| `live_acceptance` | a real allowed identity completed the relevant path | owner/operator session; owner-reported applicant receipt with provenance |
| `commercial_gate` | actual agreement/supply/rights permit business use | generally closed/unknown; buyer registration closed |

Recommended proof labels should also retain provenance, for example `repo_release_evidence`, `owner_reported_live_partial`, `local_live_accepted`, rather than converting every claim to a bare boolean.

## Safe current reconciliation matrix

This is a **proposal for generator input**, not an instruction to stamp these words directly into generated files without LOCAL checking the latest worktree.

| Capability | Safe implementation statement | Deployment/live statement supported now | Commercial boundary |
|---|---|---|---|
| public landing/catalogue | implemented | current main has documented published release/actual-domain acceptance | research catalogue ≠ inventory |
| application | durable protected intake implemented | controlled invite-only intake documented; owner reports one ordinary technical receipt/refresh passed | technical application ≠ active agency |
| authentication | Access-backed identity implemented | owner/operator real login documented; owner reports ordinary applicant OTP login passed | login ≠ membership/activation |
| admin workflow | operator queue/decision implemented | owner/operator UI documented live; decision on the ordinary test remains pending in shared evidence | no fabricated agreement |
| client/buyer registration | code exists behind supply gate | keep closed/not enabled | do not turn on from dashboard reconciliation |
| materials | rights/storage-gated code exists | storage/material delivery remains closed | publication rights remain per-asset |
| email/CRM | current app exposes mail-client composition only | Espo/Brevo installation/integration not confirmed | research candidates are not subscribers |

The dashboard should never infer missing business counts as zero. The existing private operator-journal model is correct: real business events stay private and are imported only as explicit, append-only observations.

## Proposed source change, not performed by CLOUD

LOCAL should change the generator so that deployment/live state comes from a small reviewed evidence input (or an equivalent existing local source), while static `PRODUCT` continues to describe code capability. Minimum fields per capability:

- capability;
- implementation state and source path/hash;
- deployment state;
- live-acceptance state;
- evidence reference;
- observed/accepted timestamp;
- proof source (`repo_release`, `owner_report`, `local_live`);
- explicit commercial gate;
- optional `supersedes` reference.

The generator must reject unknown proof states and must not silently promote an owner report to independently executed LOCAL acceptance. Generated Markdown/JSON/HTML should display provenance and the split state.

## Exact stale source items for LOCAL to fix

- `scripts/mira-launch-operations.py`: static application/public-landing notes saying intake is closed.
- `scripts/mira-launch-operations.py`: `authentication=implemented_code_not_deployed`.
- `scripts/mira-launch-operations.py`: unconditional `deployment='not_verified'` in `product_rows()`.
- `scripts/mira-launch-source.py`: stale secure-backend/live-receipt blocker.
- Any generated `LAUNCH-DASHBOARD.md`, `launch-dashboard.json`, `launch-dashboard.html` should be regenerated from the corrected source, never hand-patched.
- C13 contradiction remains separate: `/mira/start/` and `/mira/access/` source should say invite-only controlled intake, not open public self-registration and not a dead-end `closed` message.

## Acceptance tests for the reconciliation

1. Generator rebuild is deterministic and leaves manually owned/private operator data untouched.
2. Tests cover the four-state separation: code present / deployed / live accepted / commercially enabled.
3. Application/auth cannot regress to `closed/not_deployed` when reviewed deployment evidence is present.
4. Owner-reported evidence is rendered with its provenance until LOCAL independently accepts it.
5. Buyer registration/material delivery remain closed unless their own gates have evidence.
6. No business KPI is changed from `unknown` to `0` just because the private journal is absent.
7. Existing source hashes/provenance continue to be emitted.
8. Generated files, source generator and current operational handoff agree on invite-only semantics.

## Remaining holds

- LOCAL has not yet returned a receipt for `MIRA-LOCAL-20260918-02` in the shared branch.
- Operator decision / applicant-visible result / logout-relogin are pending in shared evidence unless LOCAL has a newer private result.
- EspoCRM/Brevo integration remains unconfirmed.
- Russia-without-VPN reachability remains unverified.
- Buyer registration, mass outreach and commercial activation remain closed.

**Result:** C14 complete as a source-level reconciliation proposal. No generated dashboard or production source was edited.