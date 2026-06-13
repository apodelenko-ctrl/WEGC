# WEGC AI sales agent (Telegram + Claude)

Полуавтономный AI-консультант «Анна»: общается с клиентом в Telegram,
квалифицирует лид, отвечает по базе знаний WEGC, отрабатывает возражения и
передаёт тёплого клиента менеджеру (уведомление в Telegram + закрытие на Zoom).

Файлы:

- `wegc-ai-agent.js` — воркер (Telegram webhook → Claude → ответ + хендофф).
- `wegc-kb.js` — база знаний (11 проектов, районы, оплата, FAQ) + system-prompt.
- `wrangler-agent.toml` — конфиг деплоя.

Notification-relay (`wegc-form-relay.js`) — отдельный воркер, его не трогаем.

## Что нужно подготовить (один раз)

1. **Telegram-бот** для клиентов: @BotFather → `/newbot` → скопировать **TOKEN**.
   (Это НЕ тот бот, что шлёт уведомления о заявках — заводим отдельного.)
2. **Anthropic API key**: console.anthropic.com → API Keys.
3. **OWNER_CHAT_ID** — куда падают тёплые лиды. Это тот же chat id, что у relay
   (где сейчас видны заявки). Если не знаешь — напиши боту-уведомителю и открой
   `https://api.telegram.org/bot<RELAY_TOKEN>/getUpdates`, поле `chat.id`.
4. **WEBHOOK_SECRET** — придумать любую случайную строку (например, из `openssl rand -hex 16`).

## Деплой

```bash
cd cloudflare-worker

# 1) KV для памяти диалогов — создать и вставить id в wrangler-agent.toml
wrangler kv namespace create CONV
#  → скопировать выданный id в поле id = "..." в wrangler-agent.toml

# 2) Секреты
wrangler secret put AGENT_BOT_TOKEN   -c wrangler-agent.toml
wrangler secret put ANTHROPIC_API_KEY -c wrangler-agent.toml
wrangler secret put OWNER_CHAT_ID     -c wrangler-agent.toml
wrangler secret put WEBHOOK_SECRET    -c wrangler-agent.toml

# 3) Деплой
wrangler deploy -c wrangler-agent.toml
#  → запомнить URL воркера: https://wegc-ai-agent.<...>.workers.dev

# 4) Подключить Telegram webhook к боту
curl "https://api.telegram.org/bot<AGENT_BOT_TOKEN>/setWebhook" \
  -d "url=https://wegc-ai-agent.<...>.workers.dev/tg" \
  -d "secret_token=<WEBHOOK_SECRET>"
```

Проверка: напиши боту `/start` — должно прийти приветствие от Анны.

## Подключение к сайту (после теста)

Когда бот заработает — ведём на него лиды:

- Кнопка/ссылка `https://t.me/<bot_username>` на CTA и в посадочных под Яндекс.Директ.
- Можно добавить как канал в чат-виджет рядом с формой.

## Стоимость

- Cloudflare Worker + KV — в рамках бесплатного тарифа на старте.
- Токены Claude — ориентировочно $0.02–0.10 за диалог-квалификацию
  (модель в `ANTHROPIC_MODEL`; дешевле — `claude-3-5-haiku-latest`).

## Обновление каталога/цен

Правим данные в `wegc-kb.js` (массив `PROJECTS`, блоки `FAQ`/`COMPANY`) и
повторяем `wrangler deploy -c wrangler-agent.toml`. RAG/векторная база не нужна —
весь каталог помещается в контекст.
