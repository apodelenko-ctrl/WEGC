# MIRA — assigned developer catalogue and private material delivery

Checkpoint09, 2026-09-16. Code and offline tests; **not deployed, no assets uploaded, collection and material delivery remain closed**.

## Scope

`/mira/library.html` is a read-only companion to the pilot cabinet. An active member sees only developer-family groups built from the projects assigned to its agency. Counts are agency-scoped, not the complete developer portfolio. A family/brand is not the buyer's legal seller or proof of an agency agreement. Unknown families stay unknown.

Project materials are approved **marketing files for internal agency use**, not buyer documents, private agency agreements or a contract-evidence vault. Client redistribution, public advertisements, white-label editing and permission to use trademarks are not granted by a download. Inventory, registration and commission gates remain independent.

## Routes

| Method / API route | Access and effect |
|---|---|
| GET `/developers` and `/developers/:id` | Active member; assigned project-family catalogue, no full-portfolio inference. |
| GET `/projects/:id/materials` | Assigned project, current agency agreement; only current permitted files. Closed/unconfigured storage returns no substitute public URL. |
| POST `/admin/materials` | Operator; register an immutable version after verifying evidence and actual bucket bytes. It does not upload the file. |
| POST `/admin/materials/:id/revoke` | Operator; audited revocation with reason. Version cannot be silently changed or restored. |
| GET `/materials/:id/download` | Recheck membership, assignment, agency agreement, per-file rights/release, expiry and content integrity before releasing bytes. |

All paths use `/mira/api`. Existing authentication, exact-origin JSON mutation checks, size limits and operator controls continue to apply. The library never sends an external message or submits a developer form.

## Owner-controlled deployment and asset preparation

1. Finish the existing Worker/D1/Access/privacy deployment gates. Protect **`/mira/library.html` together with `/mira/pilot.html` and `/mira/api/*`**. Static JS/CSS contain no business records or credentials; session/API authentication is still mandatory.
2. Apply additive migration `0003_materials.sql` to the new MIRA database, after migrations0001 and0002. Do not migrate the legacy WEGC relay/database.
3. Create a separate private marketing-assets R2 bucket and bind it as `MIRA_MATERIALS`. **Keep r2.dev and public custom-domain access disabled.** No public or presigned object URL is needed. The commented example is a placeholder, not an actual bucket/account.
4. A designated reviewer checks the exact file, its origin and distribution rights. Run the approved malware/content review separately, then record the real opaque scan reference. This implementation **does not scan for malware**: a magic signature and SHA-256 prove neither safety nor permission. Do not mark `content_reviewed` true until the review actually happened.
5. Record two separate, verified and expiring evidence entries: `materials_rights` and `material_release`. Both must have the same `project_id`, `entity_id` equal to the material's `MAT-...` ID, and matching agency scope (a specific agency, or a deliberately reviewed shared scope). A project-level or old agency agreement is not a substitute for per-file permission.
6. `material_release.facts` binds exact `sha256`, `mime_type`, integer `size_bytes`, `audience=agency_internal`, `allow_download=true`, `content_reviewed=true` and opaque `malware_scan_ref=SCAN-...`. Unknown fields and non-internal audiences are rejected. Evidence content and raw document-storage URLs are not disclosed to agency users.
7. Upload the reviewed bytes by approved owner-controlled storage administration, not through this API. Required key: `marketing/<project_id>/<sha256>.<extension>`. Do not expose credentials or add files to GitHub. Supported formats: PDF, PNG, JPEG and WebP. Maximum8MiB is this MVP's deliberate resource policy, not a Cloudflare service limit.
8. Register the material through the operator API with its ID, project, title, kind, language, MIME, exact size/hash, rights/release refs and expiry. Expiry cannot outlive either evidence record. Supported kinds: brochure, floor_plan, field_report, training; languages ru/en/th. Registration validates actual stored bytes even while delivery is closed. Changed content needs a new version/ID and new review; exact retries return the existing version, not a second business event.
9. Test live role/tenant isolation, expired/revoked rights, missing/mutated objects, double-checking after storage retrieval, unavailable API, pagination and browser error handling. Only after authorization and review set `MATERIALS_ENABLED=true`. This flag does not enable client registration, approve outreach or close any commercial gate.

## Integrity and status semantics

The server validates bounded object size, a format signature and SHA-256 at registration and again for every download. It buffers only a bounded approved asset, rechecks membership/rights after retrieval, and then returns an attachment with no-store, nosniff and restrictive document policy. Ranges are rejected rather than serving partially unchecked data. The browser independently checks size/type/hash before creating a download.

Download metadata never contains the R2 key, raw vault reference or signed public storage URL. File titles are rendered as text. The UI does not accept arbitrary returned download hosts or fallback to demo data when the protected API fails.

An immutable access entry means **validated bytes were released to the browser**, not that a user saved/read the file or that an agency activated. An asset list means the evidence was current at listing; authorization is checked again at download. Empty pages may still contain a pagination cursor after rights filtering.

## Controls still outside this MVP

Live R2/Access deployment, malware scanning, content authenticity, legal distribution review, backups, incident response and approved retention remain operational responsibilities. Audit tables intentionally have no ordinary update/delete API; a reviewed retention/erasure procedure is required before production, rather than pretending indefinite retention is automatically suitable. No anonymous public file sharing, client-facing distribution, file uploads, arbitrary remote fetch, material editing, refunds or payment execution is implemented.

## Tests and primary references

`node --test tests/mira-*.test.mjs` uses actual SQLite migrations, signed synthetic Access JWTs and an in-memory fake R2 binding. `python -m unittest discover -s tests -p 'test_mira*.py' -v` covers static boundaries. Optional `python tests/mira-library-ui.py` uses offline DOM fixtures and an intercepted download; **none of these are deployed Cloudflare E2E tests**.

Official API reference: https://developers.cloudflare.com/r2/api/workers/workers-api-reference/

Private/public bucket controls: https://developers.cloudflare.com/r2/buckets/public-buckets/
