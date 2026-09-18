# MIRA Omnichannel — LOCAL integration package

Task: **MIRA-OMNI-20260918-01**. Prepared 2026-09-18. State: **implemented and locally tested integration candidate; not deployed, not live-accepted**.

This is executable code, not another discovery request. It extends the shared-intelligence architecture already present in `cloudflare-worker/wegc-ai-agent.js`. Existing product integration and deployment belong to LOCAL. Do not merge the research branch wholesale or publish this internal folder with the website.

## Required product-profile update

Read [KNOWLEDGE-AUDIT-RU.md](KNOWLEDGE-AUDIT-RU.md) first. Set server-owned `MIRA_PROFILE` to `phuket_buyer`, `mira_agency`, or `mira_developer`; use separate private databases/tokens/routes for each. All Store callers now require explicit profile; contexts and incoming events carry the same profile. Old unscoped staging journals require deliberate migration, never automatic reuse. Use `knowledge/approved-context.json` (23 sourced blocks) with strict profile/visibility filtering. The 47 project references are unapproved review seeds, not current inventory. Current suite: 41/41 local tests PASS. This update supersedes any earlier instruction to share raw buyer and agency memory.

## What is implemented

- Durable SQLite inbox, canonical contact-to-endpoint bindings, arrival-order processing, per-contact leases and cross-channel timeline. SQLite is the delivery journal/cache, not a replacement CRM. Verified `crm_account_id` maps to the existing Espo Account.
- Text webhook normalizers and send adapters for Telegram (including explicitly enabled business connection), WhatsApp and MAX; authenticated ingress, sender account isolation and raw-body signature verification for Meta.
- One model decision interface and one knowledge policy for all channels. Anthropic API/key/model configuration is reused from the existing Worker. Model name is required explicitly; do not silently change the deployed model.
- Approved-fact selection, intent classification, explicit human handoff, contact-wide pause and opt-out. The model's own answer prose is never automatically sent. This initial automatic mode returns approved answer blocks; richer generated prose remains a later reviewed extension. It is NOT a claim that the full free-form B2B sales-agent specification is complete.
- Separate durable outbox for replies, CRM Notes and Tasks. Provider acknowledgements are logged separately from planned replies and mirrored to CRM. Failure/timeout is `uncertain`, never automatically resent. A process crash during send also requires reconciliation.
- Contact enrichment from supplied public HTML: tel/mailto, Telegram/WhatsApp/MAX/VK links and JSON-LD telephone/email with source and observation time. A phone number does not prove messenger membership. This package does not claim enrichment of the actual 80-row private CRM database.
- Authenticated `/bridge` ingress for existing web/email services. Native website polling/response delivery and native email sender are deliberately integration ports, not new public sessions or a second mailing system.

## Quick local verification

Python 3.11 or newer; standard library only. Run from this package directory:

```sh
python3 -m unittest discover -s tests -v
```

All fixtures are synthetic. No external messages, paid model calls, real CRM imports, or live credentials are needed for tests.

## Integrate in this order

1. Finish the already-running isolated Espo installation. Keep current Access/Worker/D1 and existing agency intake untouched. Copy this package selectively into a PRIVATE service checkout; keep runtime database, credentials, knowledge and bindings outside Git.
2. Re-run tests. Set `MIRA_DB` to an absolute private SQLite path on persistent LOCAL storage. This Python process is a service beside Espo, **not deployable into a JS Cloudflare Worker as-is**. Existing Cloudflare Worker may proxy through a private service connection; LOCAL decides approved hosting from current infrastructure. No paid hosting was purchased.
3. Import verified endpoint bindings through `src/admin.py --db PATH --profile mira_agency bind PRIVATE.json`. A binding contains `contact`, `context` (including `profile: mira_agency`, `role: agency`, name, city, `crm_account_id`), `channel`, `account`, `peer`, and `evidence`. Use numeric provider IDs, not a claimed username/phone in message text. Conflict => review, not automatic merge. Unknown inbound endpoints go to `identity_review`; bind then `resolve EVENT_ID`. Never fuzzy-merge by company name.
4. Create private `MIRA_KB` JSON array of approved answer blocks: `{id,text,source,profiles,audiences,visibility,approved,valid_until,contact_ids?}`. `valid_until` is an actual review expiry as Unix seconds, not an invented product validity. Use `contact_ids` for restricted terms. Do not bulk approve `wegc-kb.js`: historical prices/contract claims require current source checks. With no valid answer, the system creates a handoff task and pauses.
5. Reuse `ANTHROPIC_API_KEY` and actual `ANTHROPIC_MODEL` privately from the existing service. Keep `MIRA_SEND_ENABLED=false`. Set random `MIRA_INTERNAL_TOKEN` (32+ characters). Start `python3 src/service.py` on loopback and run bounded `python3 src/worker.py --limit 100` under the existing service supervisor. No watcher/schedule is installed by this package.
6. Configure one sender account per channel per process: `TELEGRAM_ACCOUNT_ID`, `AGENT_BOT_TOKEN`, `WEBHOOK_SECRET`; `WA_PHONE_NUMBER_ID`, `WA_ACCESS_TOKEN`, `META_APP_SECRET`, `WA_VERIFY_TOKEN`, `META_GRAPH_VERSION`; `MAX_ACCOUNT_ID`, `MAX_BOT_TOKEN`, `MAX_WEBHOOK_SECRET`. Keep unrelated channels unset. Set `ESPO_URL` (HTTPS) and scoped `ESPO_API_KEY`. Never put secrets in browser JS.
7. Place webhook ingress behind the existing reviewed HTTPS proxy, with body/rate/time limits and durable storage monitoring. Register only the selected pilot webhook. `/bridge` is server-to-server bearer authenticated; authenticated existing web/email services supply trusted session/thread IDs. End users cannot bind themselves to a CRM Account.
8. For Telegram Business, LOCAL must implement live `business_connection` updates/revocation and current `can_reply` checks before enabling `TG_BUSINESS_CONNECTIONS`. The package allowlist alone is NOT live revocation tracking. Ordinary inbound bot mode is the first testable channel.
9. Create/verify Espo custom fields/mapping for lead status/intent if used. This adapter writes standard Account Notes and Tasks (including intent), and does not guess your custom CRM schema. Assign Tasks and notifications using existing CRM workflow; the runtime does not claim that an operator has been notified merely because an outbox row exists.
10. Connect existing `/web` and `/tg` routes to this single core in an isolated branch. Retire the legacy `converse` path only after equivalence tests. Do not run both engines against one webhook. `/bridge` currently acknowledges a durable event; LOCAL must connect the site's response/poll/ack path to the resulting outbox and log actual delivery. Existing email service must likewise consume its channel's reply outbox and feed trusted incoming email thread events.
11. Populate one real approved agency binding and current KB, then run the full inbound → identification → previous outreach context → decision → reply in original channel → CRM Note/status → Task/handoff scenario. Enable sends only for that reviewed pilot after sender setup. This is account connection/acceptance, not permission to start mass outreach.

## Deliberate limits / remaining acceptance

- No live provider/model/CRM calls were made in CLOUD. WhatsApp official webhook implementation page was unavailable during research: verify the candidate adapter with the selected current Graph API account before use. No invented API version default.
- Email outbound and website response bridge need LOCAL integration. MAX bot acquisition/business-account eligibility and cold first-contact capability are not proven for our account. Business Telegram rights updates are not implemented; keep that mode off until connected.
- SQLite supports one host with a shared local persistent disk, short write transactions and bounded workers. Per-contact processing is serialized. Use one outbound dispatcher to keep pacing coherent. This is not evidence of production capacity for 100 concurrent LLM dialogs; load/rate-limit acceptance remains.
- Model calls have a 25-second timeout; process leases are 90 seconds. A killed decision process leaves a pending event recoverable after lease expiry. Automatic model outage currently pauses the contact and queues a Task rather than repeatedly spending tokens.
- Before restarting dispatch after a crash, stop other dispatchers and call `Dispatcher.recover()`. Reconcile `uncertain` rows against provider/CRM receipts manually; never reset them blindly. A 429 is also conservatively uncertain in this version. Automatic exactly-once delivery is NOT promised.
- Raw inbound and timeline contain personal data: private filesystem permissions, encryption/backups/retention and authenticated operator review are deployment requirements. No purge UI/job is included.
- Knowledge expiry is checked on selection and before dispatch; urgent revocation requires cancelling pending replies before worker restart. Dynamic per-project inventory tools and semantic retrieval are future integrations; this pilot uses bounded approved answer blocks. Keep KB small enough for the configured model context.
- Opt-out is enforced in this service. LOCAL must wire the existing Brevo/global CRM suppression workflow before multi-channel marketing; this package does not remotely unsubscribe Brevo recipients.
- No first-contact send API is exposed. `record_outreach` records a real previously sent message plus provider/campaign/template IDs so the reply engine has context. It does not manufacture an outreach event or send a campaign.

## Acceptance evidence to return

Add `CLOUD-INBOX/receipts/MIRA-OMNI-20260918-01.json`: exact read commit, local commit, provider/configuration (no keys), tests, one real channel cycle, CRM entity IDs redacted where needed, handoff pause/resume result, cross-channel identity test and remaining blockers. Mark **accepted / integrated / live_accepted** separately. Preserve existing MIRA-LOCAL and MIRA-MKT work.
