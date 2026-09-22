# CF006 — операторский просмотр принятого research snapshot

Remote import принят по LOCAL receipt в c7e5704902f4b0515a8462026199088c1fef8f94:405 агентств,43 группы,618 связей,1 completed snapshot. Это не новое выполнение импорта CLOUD. Приватные before/after exports не загружались повторно.

Пакет добавляет read-only операторский экран `/mira/research/`, поиск по имени/городу, переключение agency/developer, страницы записей, контакты с field-level evidence/checked_at/status/conversation_scope, связи застройщика с проектами. Операции записи, кнопки рассылки/активации и private native lineage отсутствуют. Пустые значения не считаются проверенными контактами.

Настройка `MIRA_RESEARCH_SNAPSHOT` должна точно указывать на принятый completed public snapshot:

`MIRA-IMPORT-3c75b4a1a591a9bedbadc5840ea0b5640e1e6c9c2090066f22898d57e6537c7d`

Неполный/приватный/отсутствующий snapshot не показывается. Пользователь не выбирает другой snapshot через URL. Каждый запрос требует подписанный Access JWT и active operator membership. Нет изменений в текущей D1, Access или main.

## Selective integration LOCAL

1. Скопировать `research-view.mjs` и `research-ui.mjs` рядом с main `cloudflare-worker/mira/site-worker.mjs`, сохранить их имена. Скопировать тест в `tests/mira-research-view.test.mjs`.
2. В site-worker.mjs добавить импорт `import {researchView} from './research-view.mjs';`.
3. **После** существующей проверки `url.origin !== env.APP_ORIGIN` и **до** маршрутизации `/mira/api/` добавить:

```js
if (url.pathname.startsWith('/mira/research/') ||
    url.pathname === '/mira/api/admin/research' ||
    url.pathname.startsWith('/mira/api/admin/research/')) {
  return researchView(request, env);
}
```

Остальной Worker сохранить, включая EXPO22-A, если уже интегрирован. D1 миграции не нужны. Existing Access policy не ослаблять; новый экран остаётся защищённым. Ключ snapshot — обычная конфигурация, не API secret.

4. Выполнить существующие API/site tests и новые research-view tests на isolated current main. Unit harness использует минимальную синтетическую read-model fixture. Отдельный smoke использует локальную публичную SQLite базу с полной generated immutable schema; это не приватный remote export CF005.
5. После авторизованного release проверить: неавторизованный запрос401, обычный участник403, operator видит405/43/618, контакты/источники/статусы и страницы. Публичный QR и intake этим пакетом не открываются. Вернуть deploy SHA и live acceptance receipt.

Поиск — SQLite substring, не полнотекстовый поиск и не морфология. SQLite lower не выполняет полное Unicode case-fold: для кириллицы используйте исходный регистр. Экран и API не выдают исследовательские project links за доступные к продаже юниты. История private CRM и каталог operational projects не импортируются этим просмотром.

NOT_RUN: реальный браузер/mobile/Cloudflare deployment и live role acceptance. Тесты SQL/HTTP и actual public data smoke — локальные, не новый live read Cloudflare. Следующий отдельный этап: операторский экран заявок и публичный intake.

## Воспроизводимая проверка

После копирования модулей и теста в интеграционное дерево: `node --test tests/mira-research-view.test.mjs`. Нужен Node с `node:sqlite`. Для full-source smoke положить `smoke-public-db.mjs` рядом с `research-view.mjs` и существующим `auth.mjs`, затем выполнить `node cloudflare-worker/mira/smoke-public-db.mjs /absolute/path/to/public-test.sqlite`. Script создаёт временную копию, добавляет только туда синтетического оператора, читает все записи/поля и удаляет копию. Исходная база не меняется. Не использовать private backup или рабочую D1.

Проверено: 83 теста (43 прежних API/site + 29 intake + 11 research-view); smoke прочитал 448 записей и 7742 поля, включая пропуски. Публичная тестовая база имеет source commit `a2248f860580107dad82c94e5f864646c4538ecc`; связь с рабочим импортом подтверждается отдельно receipt LOCAL `c7e5704902f4b0515a8462026199088c1fef8f94`, не этим локальным smoke.
