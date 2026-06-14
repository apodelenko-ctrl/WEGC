# Phuket new-launch digest (Telegram)

Утренний дайджест анонсов новостроек Пхукета. Скрипт от лица отдельного Telegram-аккаунта читает выбранные каналы застройщиков/агентств, Claude вытаскивает значимые события (презентация, пресейл, старт продаж, новый этап, цены) и присылает тебе сводку в Telegram. Запуск — GitHub Actions по крону, каждое утро 08:00 (Asia/Bangkok).

## Что понадобится (один раз)

1. **Отдельный Telegram-аккаунт** (номер) для коллектора — НЕ твой основной. С него зайди (вступи) во все каналы, которые хочешь мониторить.
2. **API ID / API HASH**: зайди на https://my.telegram.org → API development tools → создай приложение → скопируй `api_id` и `api_hash`.
3. **Бот для отправки дайджеста**: можно переиспользовать существующего бота (его токен) — главное, чтобы ты этому боту хоть раз написал `/start`, и знать свой `chat_id` (OWNER_CHAT_ID).
4. **Anthropic API key** (тот же, что у агента Анны).

## Шаг 1. Список каналов

Двумя путями:

**А) Автопоиск (рекомендуется, если списка нет).** После шага 2 (есть TG_SESSION) запусти разведчик — он найдёт каналы по теме и пришлёт тебе нумерованный список в Telegram:
```bash
cd tg-digest
TG_API_ID=.. TG_API_HASH=.. TG_SESSION=.. TG_BOT_TOKEN=.. OWNER_CHAT_ID=.. npm run discover
```
Результат: файл `discovered.json` + список топ-40 в Telegram. Выбери нужные номера и примени:
```bash
npm run apply "1,3,5,8,12"
```
Это запишет выбранные каналы в `channels.json`. Запросы для поиска правятся в `discover-queries.json`.

**Б) Вручную.** Открой `channels.json` и впиши реальные `@username` каналов.

> После выбора **зайди (вступи) в эти каналы с аккаунта-коллектора** — иначе их не прочитать.

## Шаг 2. Получить TG_SESSION (один раз, локально)

```bash
cd tg-digest
npm install
TG_API_ID=12345678 TG_API_HASH=xxxxxxxx npm run login
```
Введи номер аккаунта-коллектора, код из Telegram (и 2FA-пароль, если есть). Скрипт напечатает длинную строку SESSION — скопируй её.

## Шаг 3. Секреты в GitHub

Repo → Settings → Secrets and variables → Actions → New repository secret. Добавь:

| Secret | Значение |
|---|---|
| `TG_API_ID` | api_id с my.telegram.org |
| `TG_API_HASH` | api_hash с my.telegram.org |
| `TG_SESSION` | строка из шага 2 |
| `ANTHROPIC_API_KEY` | ключ Anthropic |
| `TG_BOT_TOKEN` | токен бота для отправки дайджеста |
| `OWNER_CHAT_ID` | твой chat id (куда слать дайджест) |
| `ANTHROPIC_MODEL` | (опционально) напр. `claude-sonnet-4-6` |

## Шаг 4. Проверка

Actions → «Phuket new-launch digest» → Run workflow (кнопка ручного запуска). Через 1–2 минуты должен прийти дайджест в Telegram.

Дальше работает сам, каждое утро. Файл `.state.json` хранит id последних просмотренных сообщений (чтобы не повторяться) и обновляется автоматически.

## Локальный тест (опционально)

```bash
cd tg-digest
TG_API_ID=.. TG_API_HASH=.. TG_SESSION=.. ANTHROPIC_API_KEY=.. \
TG_BOT_TOKEN=.. OWNER_CHAT_ID=.. npm run collect
```

## Заметки

- Аккаунт-коллектор должен быть **участником** каналов (публичные `@username` читаются после вступления).
- Время крона — в UTC. `0 1 * * *` = 08:00 Бангкок. Поменять — в `.github/workflows/phuket-digest.yml`.
- Расширение на Instagram (Apify) — отдельным этапом, в тот же пайплайн.
