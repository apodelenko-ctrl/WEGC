# RESUME-STATE

2026-09-19 · execution-06 · ACI. Ветка `agent-company/bootstrap-20260919` в `apodelenko-ctrl/WEGC`. Область записи — только `project-bible/agent-company/`.

## Сначала

Fetch фактический HEAD; читать README, Решения, WORK-STATUS, Контроль-борд и agents/QUEUE.json. Начальная база этой сессии `6f5740942a9aa65395930989967baf392d85385b`; checkpoint durable API опубликован `e014c92911f019a4ae1af36a812da013299faa1f`. Текущий последний SHA смотреть в Git, не угадывать.

## Не повторять

ACI-022 и ACI-023 завершены в заявленном локальном объёме: SQLite state/idempotency/versions, expiry/scopes, identity/all-agent-key revoke, historical receipts. ACI-025 завершена как fixture runner с lease/fencing/heartbeat/recovery. Всего 97 тестов прошли; demo выполнил две связанные fixture задачи. См. prototype/DURABLE-MOCK.md, prototype/FIXTURE-RUNNER.md и agents/receipts/runner-tests.json.

Девять Python-файлов кода/тестов доступны локально в этой сессии; четыре исходных восстановлены из connector и совпадают по Git blob SHA. Полный каталог библиотеки локально ещё НЕ собран. Не выдавать это за полный checkout.

## Следующая последовательность

1. **ACI-024:** восстановить весь каталог через доступный GitHub connector, сверяя Git blob SHA каждого настоящего файла, либо получить полноценный checkout в рабочей среде. Выполнить scripts/validate_project.py, сохранить stdout/exit code и проверяемый revision. Не считать DNS единственным возможным путём и не закрывать задачу на подставных документах.
2. **ACI-027:** стабильный business operation ID и atomic outbox на mock. Неизвестный результат доставки не должен автоматически означать повторное внешнее действие. Проверить изменение credential identity и повторные попытки после restart.
3. **ACI-028:** спроектировать и проверить восстановление старого snapshot без возврата отозванных полномочий; fail-closed startup, key epoch/rotation и сверка состояния. Не путать backup existence и безопасное возобновление production.

## Важные границы

Fixture runner исполняет только allowlisted функции echo/count, не shell и не модели. Input_revision фиксируется, но не выполняет remote checkout. Все нулевые SHA в demo помечены как fixture, не существующие коммиты. Постоянные специализированные агенты не запущены, LOCAL dispatch не подтверждён.

Durable API — только loopback. Identity mapping синтетический, не KYC. Отзыв действует в ACI, не отменяет уже исполненное и не выключает внешние системы. Idempotency пока scoped к identity/route, не к внешней бизнес-операции; исправление ACI-027. SQLite audit не immutable относительно администратора.

Исходный замысел сохранён: реальный owner/operator со стороны сервиса предоставляет компанию агентскому бизнесу. Operator-owned нужность и допустимость ещё проверяются; Wyoming/doola — кандидаты. Не заменять модель client-owned без решения владельца.

## Исполнение

Результат → тесты → receipt → очередь/журналы → commit → remote verification. Не менять main/МИРА/сайт/workflows, не публиковать KYC/секреты, не делать внешние обязательства и deployment без отдельного approval. Следующую независимую работу выполнять в активной сессии, не обещать фоновое продолжение без реального runtime.
