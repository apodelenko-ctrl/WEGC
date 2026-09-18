# Channel findings — 18 September 2026

Sources were opened during this task. Account-level availability is not inferred from documentation.

| Channel | Incoming / reply | First contact | Package status / remaining connection |
|---|---|---|---|
| Telegram ordinary bot | Webhook, `sendMessage` | Use inbound/started bot relationship; a public agency username is not an established bot chat | Normalizer, authenticated ingress and sender implemented; real bot acceptance pending |
| Telegram connected business bot | `business_message`, `business_connection_id`, granted reply rights | Manual account outreach may produce a reply observable by the connected bot when allowed; public username alone does not establish that route | PARTIALLY SUPPORTED: adapter fields implemented; live connection rights/revocation tracking and account scenario must be connected before enabling |
| WhatsApp Business Platform | Webhook and message reply route; free-form within current customer-service window | Approved template and recipient opt-in apply; first-message template flow not implemented here | PARTIALLY SUPPORTED: candidate signature/batch parser/text sender implemented; Meta technical webhook page unavailable, current account/version validation required |
| MAX | Bot webhook with shared secret, messages API | Arbitrary cold first contact / control of an existing company's user inbox not established by sources read | PARTIALLY SUPPORTED: bot-dialog text adapter implemented; business account eligibility and real endpoints pending |
| Email | Existing mail service can submit trusted events to `/bridge` | Existing Brevo workflow remains owner of campaigns | Bridge ingress only; native reply delivery/thread mapping and CRM suppression integration remain LOCAL |
| Web | Existing site service can submit trusted session events to `/bridge` | User opens site chat | Ingress only; website response/poll/ack hookup remains LOCAL; browser sid is not agency authentication |

## Official evidence

- [Telegram Bot API](https://core.telegram.org/bots/api): `business_message`, `BusinessConnection`, `BusinessBotRights.can_reply`, `sendMessage.business_connection_id`, webhook secret token. Current `can_reply` definition covers private chats with incoming messages in the last 24 hours. Check current rights before every business send, including revocations.
- [Telegram bot features](https://core.telegram.org/bots/features): connected business bots. This supports a business integration path, not an unrestricted cold-outreach bot.
- [WhatsApp Business Messaging Policy](https://whatsappbusiness.com/policy/): initiation via approved templates, opt-in, free-form replies within 24 hours of last user message and human escalation. Candidate sends are conservatively blocked 24 hours after the triggering inbound event.
- Meta technical webhook pages attempted: `https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks` and `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview` returned retrieval errors. The candidate adapter is not called live-verified on this evidence.
- [MAX API overview](https://dev.max.ru/docs-api): current host is `platform-api2.max.ru`; token belongs in Authorization header, not URL. Webhooks are the production route. Documented aggregate limit: 30 requests/second.
- [MAX subscriptions](https://dev.max.ru/docs-api/methods/POST/subscriptions): HTTPS webhook, `X-Max-Bot-Api-Secret`, response within 30 seconds, retry behavior. Our handler acknowledges only after durable ingestion.
- [MAX send message](https://dev.max.ru/docs-api/methods/POST/messages): user/chat destination and message body; documented limit two messages/second per dialog. Worker dispatch is sequential and conservatively paced; multiple sender workers are not supported by this limiter.
- [Espo API overview](https://docs.espocrm.com/development/api/) and [CRUD](https://docs.espocrm.com/development/api/crud/): REST entity operations. Local scoped API user and actual entity permissions must be tested; no live CRM credentials were available here.

No channel's existence proves that an observed agency phone has that messenger or permits bot-initiated contact. Store source observations separately from verified provider endpoints.
