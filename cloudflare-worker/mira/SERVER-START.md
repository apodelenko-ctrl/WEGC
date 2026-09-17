# MIRA — server lane for the local operator

This supplements the existing README; it does not replace the public catalogue or the work assigned to local Codex. Company/first administrator/process choices are already recorded in `project-bible/mira/operations/2026-09-17-first-partner-handoff.md`. Do not ask for them again or print private identity values in GitHub.

## Scope separation

Local Codex owns public imagery, catalogue cards, copy and browser presentation. The parallel server branch owns administrative audit, signed-identity lifecycle tests and a read-only configuration preflight. No route under `mira/` is modified by this branch. Review its PR/diff before merging into an active working tree; never reset, clean or force-push over local work.

## What this branch fixes

Previously the existing agency, project, membership and project-assignment writes could succeed without an application-level administrative audit event. The new `admin-audit.mjs` commits each mutation and its immutable event in the same D1 batch. A failed audit insert rolls back the mutation. Duplicate assignment does not generate a second false event. Events begin at this release: no historical actions or approvals are invented.

The authenticated operator can read scoped history:

```
GET /mira/api/admin/audit?entity_type=agency&entity_id=<agency-id>&limit=50
GET /mira/api/admin/audit?entity_type=membership&entity_id=<verified-subject>&after_version=0&limit=50
```

Allowed entity types: agency, membership, project, agency_project. `next_after_version` is the continuation cursor. These endpoints do not accept a claimed role or email as authorization. SQL administration outside the application remains separately controlled and is not covered by these application events. This is not a complete compliance audit system and does not add compare-and-swap protection to pre-existing admin edit endpoints.

## Local acceptance before deploying

```
node --test tests/mira-signup-journey.test.mjs
python3 -m unittest discover -s tests -p test_mira_server_preflight.py -v
```

The Node suite calls the production Worker, verifies signed synthetic RSA JWTs, uses the actual migrations on a temporary SQLite database, and mocks ONLY the Access certificate response. It exercises pending applicant isolation, receipt persistence after reopening the database, retries, operator qualification/onboarding, permissions, revocation and rollback. It does not send email, run a browser, provision a Cloudflare account or prove remote-D1 behavior.

## Inspect the real local environment, without printing credentials

Run ordinary CLI version/account status checks in the authorized repository folder. Verify the actual account and zone, not a screenshot fragment. Read the new D1's metadata and verify it is a dedicated MIRA database; a name prefix alone is not proof. Never use Charter/CCapital/Herd workers, `charter_leads`, `CONV`, their secrets or another project's bucket. No paid resource creation or changes to unrelated DNS are implied.

Create the local ignored `cloudflare-worker/mira/wrangler.toml` only with actual approved values. The existing example is incomplete by design. In addition to its fields, set `account_id`, a narrow API route, and `preview_urls = false`. All **three** existing migrations are required: `0001_mira.sql`, `0002_operations.sql`, `0003_materials.sql`. This branch adds no migration.

The preflight is read-only and never calls Wrangler or a network service:

```sh
python3 scripts/mira-server-preflight.py \
  --config cloudflare-worker/mira/wrangler.toml \
  --expected-account-id "$ACCOUNT_ID" \
  --expected-database-id "$MIRA_DB_ID" \
  --expected-origin https://wegc.fund
```

`ACCOUNT_ID` and `MIRA_DB_ID` are locally verified resource identifiers, not invented defaults. Default mode checks a closed staging configuration: both intake and material delivery disabled. For a separately reviewed intake configuration use `--mode intake-config`. Even a passing report deliberately leaves `production_ready=false`: it cannot verify hosting legality, Access policies, actual resources, email receipt, administrator identity or backups. It supports only the current single-environment TOML; additional bindings/environments must be reviewed instead of silently inherited.

## Authentication is still a deployment decision

Cloudflare Access One-time PIN can provide email-code authentication without a MIRA password database. It must be enabled/configured explicitly and exercised in the real account. An allowlist pilot is not open self-registration. A broad OTP policy allows all eligible emails to reach the application, NOT automatic business access: the Worker must keep unapproved applicants outside agency data. The admin allowlist/operator provisioning must not be inferred from a matching email header. Decide and verify this policy before collecting real email addresses.

Cloudflare does not necessarily send a code when the screen says it did; a blocked email can see the same message. Test actual delivery, single use, expiry, logout, expired-session recovery and Russian-network reachability. If using OTP, password reset is not a separate implemented feature; recovery is a new approved code/login flow. Do not claim delivery success from a mocked JWT test.

## Remaining launch acceptance

1. Authorized dedicated Worker/D1 and protected page/library/API routes; safe deployment and rollback.
2. Actual email login and privately verified first-operator identity; receipt survives logout, server restart and a second device.
3. Reviewed privacy, processing/location, retention, deletion, access and incident arrangements. The preference to migrate later is not evidence of compliance.
4. Operator can review a real approved agency without manual edits to production rows; isolation and revocation are tested on the deployment.
5. A recoverable database backup/restore exercise and a separately agreed non-disruptive capacity test.
6. Buyer registration enabled only for a separately admitted project with current inventory, seller, registration/protection and commission evidence. Agency onboarding does not wait for all catalogue rows to be sellable.

No original developer agreements, real applications, account subjects, tokens, passwords, cookies, SQL exports or personal operator details belong in this public repository. No external outreach or real transactional email is sent by this branch.

## Primary implementation references (reviewed 2026-09-17)

- D1 transaction semantics: https://developers.cloudflare.com/d1/worker-api/d1-database/#batch
- D1 migration tooling: https://developers.cloudflare.com/d1/wrangler-commands/
- Access email codes: https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/
- Access policy scope: https://developers.cloudflare.com/cloudflare-one/access-controls/policies/
