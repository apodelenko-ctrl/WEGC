# C15 — final handoff validation and actual remaining holds

**Checked:** 2026-09-18, Asia/Bangkok. **Run start:** 13:57:30 +07:00.  
**Scope:** validate the current CLOUD→LOCAL handoff evidence and its proof boundaries. No import, merge, deployment, outreach or production mutation.

## Sources re-read

- immutable night research snapshot `beb9707c8561c138c896b122c6776a217ee4b3f0` as referenced by the handoff;
- current `main` still `1b5e6cc053bd4b20a47c3f4231c56bb1f05d850b` at this check;
- `TRANSFER-QA.md`;
- `CLOUD-INBOX/DATA-HANDOFF-20260918.md`;
- `CLOUD-INBOX/project-taxonomy-20260918.json`;
- `CLOUD-INBOX/START-HERE.md`, `QUEUE.json`, and `tasks/MIRA-LOCAL-20260918-02.md`;
- current day `RESUME-STATE.json` through C13;
- C14 source-reconciliation result created in this run.

## Validation ledger

| Check | Current result | Proof level / limitation |
|---|---|---|
| immutable project source | 15 Vietnam + 15 Montenegro | recorded night snapshot + transfer QA; not commercial inventory |
| research quality after day corrections | 27 complete-for-discovery / 3 partial | C02–C04 recommendation only; remaining partial: Waterpoint, Merit Starlit, Porto Budva |
| Russia candidate transport | 50 compact IDs joined to 29+21 detail rows | prior machine QA recorded; candidates, not active agencies |
| Belarus candidate transport | 30 records from structured JSON joined by stable ID | prior machine QA recorded; damaged detailed CSV explicitly banned |
| damaged Belarus CSV | 29 records; 14 over-wide rows under 18-field header | evidence-only; must not be imported |
| restored Belarus missing ID | `by-eksklyuziv-group` | prior repair by stable-ID join; no guessed fields |
| combined RU+BY IDs | 80 unique | prior machine QA recorded; not legal/rebrand/local-CRM dedupe |
| exact-domain baseline scan | 52 main data/sales CSVs, zero exact candidate-domain matches | prior machine scan; does not cover unpublished LOCAL CRM or legal aliases |
| explicit project taxonomy | 30 mappings present | current GitHub JSON read; `condo/villa/mixed/hotel`; original `propertyTypes` must remain |
| taxonomy commercial gate | `commerciallyEnabled=false` | current `project-taxonomy-20260918.json` |
| taxonomy media gate | `imagePublicationApproved=false` | current `project-taxonomy-20260918.json` |
| Lumi Hanoi group correction | `CapitaLand Group`; developer brand remains CapitaLand Development | transfer QA + cited first-party source; legal seller remains unknown |
| new publication-approved expansion media | 0 | day/media evidence; rights routes exist but permissions not acquired |
| external outreach/send | not authorized | queue and task gates remain closed |
| buyer registration | disabled/closed | queue/task and current product boundaries |
| CRM/Brevo | implementation not confirmed | M05/M06 prepared; no shared LOCAL receipt proving runtime/import/send acceptance |
| Phuket commercial path | VIVI selected as first acceptance dossier | C12; commercially enabled remains false until private holds close |
| expo/intake path | invite-only controlled-intake reconciliation proposed | C13/C14; no public self-registration claim |

## Machine-verification scope — keep the distinction explicit

### Previously executed machine verification

`TRANSFER-QA.md` records:

- source export run `35294630054` / artifact `10527386378` succeeded;
- source archive SHA-256 `5de4497f3238da892f0cd870cbc61b14a2e94f22b1ba0a796562003228d49a08` matched;
- all 230 declared exported source hashes were checked;
- corrected Belarus delivery was serialized from structured JSON and validated as 30 rectangular rows;
- RU 29+21 detail rows joined to the 50 compact IDs;
- combined 80 IDs were unique;
- exact-domain comparison across 52 main data/sales CSVs found zero exact matches;
- the owner transfer package verifier passed its own manifest/parse/ID/taxonomy/gate checks.

Those results are retained as executed proof. C15 does **not** rename them as a fresh rerun.

### What C15 actually rechecked now

Using the current GitHub branch, C15 re-read the handoff instructions, current taxonomy/gates, current queue/task, source-level dashboard contradiction and the recorded QA evidence. It confirms that the current documentation still points LOCAL to the repaired source path and does not reopen commercial/send/buyer/media gates.

The cloud execution environment could not clone the public repository through its shell because DNS resolution to GitHub failed, so C15 did not pretend to rerun the old package parser from a local checkout. GitHub connector reads remained available. This limitation does not invalidate the earlier machine-verification record; it only scopes this checkpoint accurately.

## Night-source hashes preserved in the handoff

The current `DATA-HANDOFF-20260918.md` retains SHA-256 values for the key immutable source files:

- `vietnam-projects.json` — `e4ee5b5255fa4a9d82160416e5acfd0422618fa5bb2faf942e6b62bccccb61c0`;
- `montenegro-projects.json` — `e6c1d2b20804d74a8a8d9aea4067d31aba9d46deea25f5ad395de2f12786b76a`;
- `03-russia-a.csv` — `fb51f56f6f085420a67d96518d8f6cb0ac1393e017e3263d5b895a4af4bc42f3`;
- `04-russia-b.csv` — `305bbda4df04ec0b2b91d24f09c9790c92b31cd87dfccdd5a3fa2437add3358f`;
- `russia-agencies.csv` — `faffd94a95e435c6d49b2dec96b63d0a3305af095c1326b387d9443e50d02b77`;
- `belarus-agencies.csv` — `c74cb6ddf445592d12da414b5bdd409afd8d8faf572f835ad2a2241c7d1411d4`;
- `05-belarus-agencies.json` — `2056743ce68fc67da2f3e410d085d5f3524be57de985484fd49653ee4b3965be`.

These hashes belong to the immutable NIGHT snapshot / earlier verified transfer, not to later C02–C14 notes.

## No gate accidentally opened by the handoff

Current handoff still requires all of the following:

- research candidates are not active agencies or Brevo subscribers;
- `outreach_status=not_authorized` until a separate release;
- no current organisation-level Belarus licence claim without regulator evidence;
- no project image becomes publication-approved merely because a URL/media kit/partner portal exists;
- VIVI private evidence is not copied into public GitHub and does not generalize to the whole Phuket catalogue;
- new VN/ME records are `research_only` / `commerciallyEnabled=false` until a project-specific commercial path exists;
- buyer registration remains off;
- CLOUD-INBOX must stay out of the public static bundle;
- the research branch is not to be wholesale-merged into main.

## Required LOCAL acceptance after selective integration

The next LOCAL receipt should report, separately:

1. exact research commit read and local branch/HEAD;
2. imported project count and stable-ID set;
3. imported agency/research candidate count, duplicate/hold count and local CRM/legal/rebrand dedupe result;
4. rectangular CSV/JSON parse checks on the locally generated import artifacts;
5. taxonomy distribution with mixed/hotel preserved and original `propertyTypes` retained;
6. source/provenance references retained per imported record;
7. media approved/held counts by exact asset and usage basis;
8. build/test/browser results for changed code/data only;
9. actual-domain publication result separately from local/CI success;
10. buyer/send/commercial gates unchanged unless a separately evidenced release explicitly changes them.

## Actual remaining holds after C15

- No shared LOCAL receipt yet for `MIRA-LOCAL-20260918-02`.
- Operator decision → applicant-visible result → logout/relogin still pending in shared evidence unless LOCAL has a newer private result.
- VN/ME data are not yet confirmed selectively integrated into current product.
- Local CRM/legal/rebrand dedupe for 80 agency candidates remains unverified.
- Six Belarus owner-review candidates lack independently verified current organisation-level licence status.
- EspoCRM/Brevo runtime/account/domain/import/reply-stop/suppression/delivery acceptance remains unconfirmed.
- VIVI continuity/current inventory/payment plan/lead-protection/downstream agency and media rights remain private operational holds.
- New publication-approved Bali/Dubai media remains zero.
- C13/C14 source contradictions have proposed fixes but no LOCAL code/deploy result yet.
- Russia-without-VPN remains unverified.

**Result:** C15 complete as a handoff/proof-boundary validation. Existing machine QA is preserved accurately; no new live/product acceptance is claimed.