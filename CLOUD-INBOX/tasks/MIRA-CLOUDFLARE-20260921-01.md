# MIRA-CLOUDFLARE-20260921-01 — существующая Cloudflare D1, checkpoint CF001

Поручение владельца «действуй» и screenshot21Sep23:40 подтверждают существующие ресурсы: `mira-pilot-api`, `pilot.wegc.fund`, `MIRA_DB → mira-pilot`, `MIRA_ASSETS`. Не создавать вторую productionбазу и не возвращать обязательный VPS.

Пакет [README](../packages/MIRA-CLOUDFLARE-20260921-01/README.md) реализован: импорт405/43 research записей,618 mapping IDs и optional private165 native lineage.16/16 тестов; оба полных фактических локальных прогона с replay прошли,13 operational tables unchanged. Это не remote D1 import и не полное восстановление native CRM/mail.

Следующий конкретный LOCAL/авторизованный CLOUD шаг: выполнить read-only `live-inventory.sql` в существующей `mira-pilot`, вернуть схему/миграции/счётчики и безопасный resource receipt. Использовать существующий авторизованный доступ; новые secrets не помещать в чат/Git. UUID нужно прочитать, не выводить из названия.

После сверки: backup/bookmark, изолированный D1 import+replay, controlled additive migration/import в существующую базу; сверка старых квитанций и всех прежних таблиц. Generated `0004_research_import.sql` применять только после проверки конфликтов имён/версий. BaseSQL напрямую не применять. Не merge всю research-ветку и не сбрасывать D1.

Затем operator-only view выбранного completed snapshot в существующей authboundary; native Email/Task/journal/suppression/history/agreements отдельно по реальному private export. Developer candidates87 не считать совпавшими юридическими лицами. Existing78 nativeagency references разрешены точно поID. Ниотправок, ниактивации исследований этим импортом не производится.

Вернуть receipt с фактическими source/target SHA, snapshotID, counts до/после, replay, схематическим diff и статусом deployed/live accepted. Общий аудит и повторный ACK не нужны. EXPO-03 путь нового посетителя остаётся параллельным P0. Receipt CLOUD: `CLOUD-INBOX/receipts/MIRA-CLOUDFLARE-20260921-01.json`.
