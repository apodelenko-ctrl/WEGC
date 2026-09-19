# MIRA-CLOUD-CUTOVER-20260919-01

Owner intent: finish current LOCAL work, then remove operational dependence on the sleeping Mac. This task is a continuation of MIRA-AUTONOMY-20260919-01 and T14, not a new CRM/OMNI build.

## Current confirmed source state

- LOCAL closeout receipt exists and reports private source `54d80452d36080ded3d141fbac56a2c22506f16c`.
- Native private lab: EspoCRM 10.0.8 + MariaDB 11.4, 167 Accounts total (78 agency research, 87 developer research, 2 synthetic), native mail lab accepted locally, external mail 0.
- Encrypted local backup exists: AES-256-GCM, SHA-256 `48945a6b0ebee8d52bb9b4b32198119cdd78afb55a4578e6a62778de93a25140`; recovery key must remain separate.
- Public marketplace release is already deployed independently; do not touch Worker/Access/D1/public catalogue for this transfer.
- Latest CLOUD OMNI/client-flow source remains separate from the private runtime and still needs selective LOCAL integration/live acceptance.

## Private cloud destination prepared by CLOUD

CLOUD created an **owner-only Google Drive folder** named:

`MIRA CLOUD HANDOFF — PRIVATE — 2026-09-19`

with four private subfolders:
1. `01 — encrypted runtime backup`
2. `02 — code and restore package`
3. `03 — manifests and crosswalk`
4. `04 — acceptance receipts`

The Drive URL/IDs are intentionally **not written to this public repository**. The folder is not shared publicly.

## LOCAL transfer deliverables

Do not publish plaintext data, credentials, correspondence, contracts or the recovery key.

### A. encrypted runtime backup
Upload the existing encrypted archive unchanged to private subfolder 01. Record:
- filename
- byte size
- SHA-256
- cipher
- created_at
- source private checkpoint
- recovery-key location: only a label, never the value

CLOUD/owner readback must reproduce SHA-256 exactly before this item is PASS.

### B. code and restore package
Place a private package in subfolder 02 containing only what is required to recreate the accepted lab:
- private source commit/export corresponding to the accepted runtime
- compose/runtime configuration with secrets removed
- pinned container/image versions/digests where known
- migrations/additive field definitions
- OMNI native integration patches already accepted
- restore/start/stop/rollback procedure
- health/readiness commands
- no caches, raw mailbox exports or credentials

### C. sanitized manifests and crosswalk
Subfolder 03:
- sanitized worktree/branch/commit manifest
- schema/table/entity counts
- secret **names** only
- ports/endpoints/dependencies
- current 78 agency + 87 developer external-ID crosswalk or explicit unresolved rows
- private/public source mappings needed for selective import
- list of deferred integrations: latest CLOUD client flow, live channels/model, public mail, media/VIVI, QR/Russia network

### D. acceptance receipts
Subfolder 04:
- current LOCAL/MKT/OMNI/CLOSEOUT receipts
- cloud restore receipt once performed
- checksums only; no sensitive raw evidence

## Restore acceptance

A cloud migration is NOT complete merely because files were uploaded.

Required later on an approved persistent runtime:
1. restore encrypted backup with separately supplied key;
2. database integrity and expected entity counts;
3. non-admin ACL;
4. CRM login + restart persistence;
5. local mail journal/reply bridge without external sending;
6. OMNI replay/idempotency;
7. latest client-flow selective integration preserving `assignedUserId`;
8. backup-after-restore and second restore test;
9. only after successful restore may Mac cease to be the sole runtime.

No VPS purchase, DNS change, external mail, buyer enablement or production cutover is authorized by this task.

## Receipt

Update existing closeout/autonomy evidence and create/update:
`CLOUD-INBOX/receipts/MIRA-CLOUD-CUTOVER-20260919-01.json`

Minimum fields:
- read_source_sha
- local_private_source
- backup_uploaded
- backup_sha256_verified
- code_package_uploaded
- sanitized_manifest_uploaded
- crosswalk_status
- cloud_runtime_selected
- cloud_restore_status
- tests
- remaining_holds
- all_done

Use `all_done=false` until actual restore and end-to-end acceptance are complete.
