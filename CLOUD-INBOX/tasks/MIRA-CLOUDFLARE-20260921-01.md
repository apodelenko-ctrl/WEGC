## CF006 — 22 сентября 2026: импорт принят, операторский просмотр подготовлен

**Актуальный статус:** CF005 выполнен LOCAL в рабочей `mira-pilot`, receipt commit `c7e5704902f4b0515a8462026199088c1fef8f94`:405 агентств,43 группы застройщиков,618 связей,1 completed snapshot; replay без дублей, исходные13 таблиц/48 schema objects сохранены. Прежние требования повторить bookmark, export/import или общий аудит ниже — исторические и закрыты. Полный private native CRM/mail restore этим не подтверждён.

В `CLOUD-INBOX/packages/MIRA-RESEARCH-VIEW-20260922-01` реализован закрытый экран `/mira/research/`: поиск, страницы agency/developer, значения контактов с источниками/датами/status/conversation_scope и связи проектов. Доступ только active operator через существующий signed Access JWT; только public completed snapshot из конфигурации. **83/83 локальных теста**, full-source smoke448 записей/7742 поля (включая пропуски). Это не live acceptance и не7742 проверенных контакта.

LOCAL: выборочно интегрировать пакет по README на актуальный main, сохранить EXPO22-A и Access, установить точный snapshot из CF005, вернуть deploy SHA и live role/browser receipt. Новая D1 миграция этому экрану не нужна. Операторский экран заявок, уведомления, public intake и полная репетиция остаются отдельными этапами. Новых записей/import/deploy/отправок в этом CLOUD блоке0. Botanica signed/stamped-and-sent сохранён. До GO/NO-GO запуск не объявляется готовым.

Receipt: `CLOUD-INBOX/receipts/MIRA-CLOUDFLARE-CF006-RESEARCH-VIEW.json`; event: `CLOUD-INBOX/events/2026-09-22/cloudflare-research-view-cf006.json`. Источник main `9a5f4c89168aa9e7995ceebf6db8dbaaf9a61137`.

# MIRA-CLOUDFLARE-20260921-01 — существующая Cloudflare D1, checkpoint CF001

Поручение владельца «действуй» и screenshot21Sep23:40 подтверждают существующие ресурсы: `mira-pilot-api`, `pilot.wegc.fund`, `MIRA_DB → mira-pilot`, `MIRA_ASSETS`. Не создавать вторую productionбазу и не возвращать обязательный VPS.

Пакет [README](../packages/MIRA-CLOUDFLARE-20260921-01/README.md) реализован: импорт405/43 research записей,618 mapping IDs и optional private165 native lineage.16/16 тестов; оба полных фактических локальных прогона с replay прошли,13 operational tables unchanged. Это не remote D1 import и не полное восстановление native CRM/mail.

Следующий конкретный LOCAL/авторизованный CLOUD шаг: выполнить read-only `live-inventory.sql` в существующей `mira-pilot`, вернуть схему/миграции/счётчики и безопасный resource receipt. Использовать существующий авторизованный доступ; новые secrets не помещать в чат/Git. UUID нужно прочитать, не выводить из названия.

После сверки: backup/bookmark, изолированный D1 import+replay, controlled additive migration/import в существующую базу; сверка старых квитанций и всех прежних таблиц. Generated `0004_research_import.sql` применять только после проверки конфликтов имён/версий. BaseSQL напрямую не применять. Не merge всю research-ветку и не сбрасывать D1.

Затем operator-only view выбранного completed snapshot в существующей authboundary; native Email/Task/journal/suppression/history/agreements отдельно по реальному private export. Developer candidates87 не считать совпавшими юридическими лицами. Existing78 nativeagency references разрешены точно поID. Ниотправок, ниактивации исследований этим импортом не производится.

Вернуть receipt с фактическими source/target SHA, snapshotID, counts до/после, replay, схематическим diff и статусом deployed/live accepted. Общий аудит и повторный ACK не нужны. EXPO-03 путь нового посетителя остаётся параллельным P0. Receipt CLOUD: `CLOUD-INBOX/receipts/MIRA-CLOUDFLARE-20260921-01.json`.


## CF004 — live baseline принят 2026-09-21T17:06:24.516Z

Owner export `export (1).csv` подтвердил counts всех13 operational tables,25 индексов/10 триггеров и applied migrations0001–0003. Совпадение с main полное; сравнение сохранено в `CLOUD-INBOX/packages/MIRA-CLOUDFLARE-20260921-01/LIVE-BASELINE-20260921.json`. Исходные ненулевые counts: applications1, memberships1, events3, rate_limits1. Содержание записей и их synthetic/real статус неизвестны; сохранять все. Остальные9 таблиц0. Старые задания повторно собирать inventory выше выполнены.

Следующий шаг: в Console существующей `mira-pilot` выполнить служебную read-only команду `/bookmark` и сохранить возвращённую точку восстановления перед импортом. Это не SQL для Studio и не команда restore. Bookmark имеет ограниченный срок хранения, поэтому долгосрочный backup отдельно через штатный экспорт при доступном авторизованном исполнителе. После получения backup/recovery point перейти к уже подготовленному additive import/replay, а не новому общему аудиту. В этом checkpoint D1 writes0, full native CRM restore не выполнен. Приватный backup не публиковать.


## CF005 — выполнить готовый пакет через действующий LOCAL доступ

> **CF005 — bookmark получен 2026-09-22T06:53:11.304Z:** владелец вернул фактический ответ Console. Точка сохранена в CLOUD-INBOX/receipts/MIRA-CLOUDFLARE-CF005-BOOKMARK.json; прежний blocker «bookmark не получен» закрыт. /restore не запускался и не нужен для проверки. SQL export ещё не выполнен; Cloudflare connector/token в текущем CLOUD-сеансе отсутствуют. Следующий шаг — исполнение подготовленного импорта через имеющийся авторизованный LOCAL/Wrangler, без повторных скриншотов schema/counts/bookmark. Все предыдущие данные/EXPO22-A сохранены.

Прочитать актуальный HEAD этой research-ветки и receipts CF001–CF005, затем пакет CLOUD-INBOX/packages/MIRA-CLOUDFLARE-20260921-01. LOCAL остаётся интегратором продукта; разрешение владельца на cloud migration уже получено. Не повторять выбор VPS или запрос ACK.

1. Использовать существующий авторизованный Wrangler и фактический MIRA config. Если сессия истекла, штатный login; не переносить токены в чат/Git. Если LOCAL тоже не имеет доступа, вернуть точную ошибку авторизации.
2. Выгрузить mira-pilot в приватный каталог вне репозитория штатным d1 export --remote --output; файл не публиковать. Проверить checksum и читаемость локально. Текущая Console bookmark уже получена; отсутствие private CRM recovery key не блокирует public research import.
3. Сгенерировать public-only SQL существующим import_registry.py prepare с точным source SHA и исходными405 agency/43 developer/618 project links. Не подменять его schema.base.sql, native archive или сырым SQLite-файлом. Приватный crosswalk не нужен первому public import.
4. Выполнить изолированную D1 проверку prepared schema/import/replay, затем контролируемое аддитивное применение в существующую mira-pilot. Проверить operational rows до/после и 448 research entities/618 links в одном completed snapshot. Не суммировать повторные snapshots. При конфликте не DROP/reset; сохранить ошибку и остановить write.
5. Вернуть sanitized receipt: source SHA, target resource, bookmark reference, private export checksum, snapshot, before/after counts, replay, existing-record preservation, remote results. Никаких dump/контактов/секретов в Git. Опубликованный research snapshot не равен agency activation или full native CRM restore.

EXPO22-A отдельно: prepared public intake требует selective integration и live acceptance; новый публичный приём этим CF005 не включается. Ни писем, ни форм, ни purchases. Исходный task не разрешает вслепую менять Access или main.
