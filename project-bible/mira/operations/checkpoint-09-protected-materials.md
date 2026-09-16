# Checkpoint09 — assigned developer catalogue and protected materials

2026-09-16. Code and offline QA, not deployment or commercial activation.

## Delivered

The protected read-only `/mira/library.html` complements the pilot: assigned developer-family groups, scoped project drill-down and authorised material listings. A group is not a legal seller or the developer's full portfolio. No mock data appears in production source when API access is unavailable.

`cloudflare-worker/mira/materials.mjs` and additive migration0003 implement immutable marketing-asset versions, separate per-file rights and release evidence, private R2 retrieval, bounded size/MIME signature/SHA-256 verification, rechecks after storage access, audited release of validated bytes and irreversible revocation. Agency-specific evidence does not leak across agencies sharing a project. Downloads are internal-use only; no client redistribution right is inferred.

The operator registers actual reviewed bytes by an exact deterministic object key. No arbitrary URL retrieval, upload, public/signed R2 URL, external message or client document handling is added. Release evidence requires a real prior malware/content-review reference; this code is not itself a malware scanner. Delivery remains disabled and requires a new private bucket plus the existing Access/Worker deployment gates.

The canonical19-capability dashboard now marks developer/material functionality as implemented code, with storage/deployment still closed. `MATERIALS-README.md` defines exact operator preparation, Access protection for the library, supported formats, limits, evidence scopes and remaining retention/security duties.

## Verification

Local57 Node and66 Python tests passed. The17 new API/storage tests cover scoped groups, pagination, release facts, operator-only registration, immutable versions, protected listing/download, closed storage, expired/revoked or incorrectly scoped evidence, corruption/size/MIME rejection, changes during retrieval, revocation, pagination after rights filtering and unauthorized/range requests. Four source-boundary tests and four literal-edit-integrity tests were added.

Six new offline browser scenarios passed on desktop/mobile, including closed storage, revoked download, hash mismatch and API unavailable; no external requests or overflow. Existing offline pilot/demo regression also passed. Synthetic fixtures and intercepted browser downloads are not deployed R2/Access E2E tests or proof that a real user saved a file.

New files are stored as readable source. Seven small integration edits use literal old/new UTF-8 text with before/after hashes through the existing reviewed-checkpoint validator. CI commits the resulting ordinary source after tests; no large compressed payload is copied. Verify the resulting checkpoint and remote CI before claiming deployment or remote success.

## Continue

Phuket first-party project/family evidence and developer owner-review pack; current project-specific supply gate; additional strong agency decision routes; bible index/decisions synchronization. No external contact or file upload occurred. Primary private contracts and their commercial clauses remain outside public GitHub.
