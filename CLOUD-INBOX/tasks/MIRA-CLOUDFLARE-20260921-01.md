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
