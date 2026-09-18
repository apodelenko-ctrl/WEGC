# Discovery and architecture decision — 2026-09-18

## Existing implementation inspected

Repository: `apodelenko-ctrl/WEGC`, current main read through GitHub contents API. Existing public release baseline is PR #15 / merge `22186058eb478239277ceddce52295688f5512c5`; use exact current HEAD again before integration.

- `cloudflare-worker/wegc-ai-agent.js`: `/tg` and `/web` both call shared `converse`; Anthropic Messages API, `ANTHROPIC_MODEL` override, code fallback `claude-sonnet-4-6`. Header comments mention an older default and should not drive configuration.
- `cloudflare-worker/wegc-kb.js`: `buildSystemPrompt`, project facts and `HANDOFF_TOOL`. Contains price/contract-related statements; presence in source does not prove that every statement is current or approved for MIRA B2B.
- `chat-widget.js`: website requests `/web` with a browser session ID. This is not authenticated agency identity. Canned chip answers may bypass the AI and need the same KB review on integration.
- Current memory keys split Telegram chat IDs and `web:<sid>` in KV. D1 `leads` logs exist, but this is not an Espo cross-channel contact timeline.
- Current handoff notifies owner and sets a flag; subsequent `converse` calls still invoke the model. Telegram webhook acknowledges before durable ingestion and handles async errors in `waitUntil`; no inbox dedupe found in that path.
- New LOCAL receipt `CLOUD-INBOX/receipts/MIRA-LOCAL-20260918-02.json`: CRM runtime image download in progress; 80 agency staging records, 12 drafts, no native CRM import acceptance. Chosen Espo/Brevo retained. Do not repeat their selection or installation.

## Decision

Build a PRIVATE deployable Python standard-library sidecar candidate next to the existing CRM lab. It handles transport persistence, verified identity, model decisions, policy, outbox and CRM projection. This avoids a new CRM/helpdesk dependency and does not require modifying production Cloudflare/D1. Existing web/Telegram routes can become thin adapters to the shared core after LOCAL integration.

This is a conscious service-boundary change from the original JS Worker, not a claimed drop-in JS patch. No new model provider chosen: inherit Anthropic configuration. No copied free-form website brain running beside the new brain after migration; both site and messengers must use the same core. Preserve the old path until the candidate passes integration tests.

One canonical CRM contact may have several explicitly verified endpoints. Do not merge all employees into one person because they share an agency switchboard. For this pilot `contact` is an operator-assigned stable identity, and `crm_account_id` links its company; more detailed Espo Contact mapping is LOCAL's existing CRM concern.

## Build / reuse

| Component | Decision |
|---|---|
| CRM | Reuse Espo already selected; no custom CRM implementation |
| Marketing campaigns | Reuse Brevo; no outbound campaign tool added |
| AI | Reuse current Anthropic account/model config; shared strict decision interface |
| Conversation journal | Small SQLite inbox/outbox sidecar; private durable transport, not master customer database |
| Gateway | Thin official adapters; start with one inbound Telegram bot pilot |
| Full helpdesk | Not added without a demonstrated unmet operator need; existing CRM Tasks/Notes first |
| Knowledge | Reviewed answer blocks with audience/scope/source/expiry; current inventory and richer RAG remain connected product data work |

The attached executable package is ready for isolated integration, not proof of production activation, all-channel completeness or capacity for hundreds of live conversations.
