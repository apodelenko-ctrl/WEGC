# WORK-STATUS

2026-09-19 · execution-05 · ASTRA. База продолжения: `6f5740942a9aa65395930989967baf392d85385b`. Текущий SHA определяется Git-историей рабочей ветки.

## Новый реализованный блок

**ACI-022 done:** versioned SQLite state, атомарные записи состояния/квитанции/события, идемпотентность после нового экземпляра и отдельного процесса, optimistic version check, локальный backup/restore. В тесте процесс принудительно завершается до commit; восстановление не оставляет ложного результата.

**ACI-023 done в объёме симулятора:** срок identity и мандата, application/action scopes, отзыв одного identity и всех ключей agent_id внутри ACI, запрет повторного provisioning отозванного агента, current authorization до historical replay. Старый ответ не восстанавливает отозванный мандат.

78 tests, OK, 0 failures/errors. Это 48 сохранённых baseline-тестов и 30 новых. Все семь Python-файлов имеют контрольные суммы в [receipt](agents/receipts/durable-tests.json). Новые blob SHA, возвращённые GitHub, совпадают с протестированными. Подробности запуска и ограничения: [DURABLE-MOCK](prototype/DURABLE-MOCK.md).

## Очередь

26 задач: 15 done, 2 ready, 9 blocked. Следующая независимая работа — **ACI-025**, локальный runner с lease/fencing/receipt. ACI-024 остаётся открытой: полного checkout для scripts/validate_project.py ещё нет; прямой download повторно не прошёл DNS. Отдельные code tests не заменяют проверку всей библиотеки.

## Сохраняющиеся ограничения

Независимый review ACI-012, настоящие provider webhooks/outbox, KYC/EIN, финансовые подключения, production auth и постоянные LLM workers не выполнены. Fixture identity не является проверенной юридической стороной. Backup — изолированный snapshot test, не безопасная процедура возврата production в работу: старый снимок может вернуть более ранние permissions и receipts.

Юрисдикции, права сторон и провайдеры не утверждены окончательно. Письма, регистрации, банковские заявки, покупки и deployment не выполнялись. Изменения только в `project-bible/agent-company/`, не main/МИРА/workflows.
