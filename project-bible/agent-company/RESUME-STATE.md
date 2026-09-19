# RESUME-STATE

2026-09-19 · execution-05 · ACI. Рабочая ветка `agent-company/bootstrap-20260919`, каталог `project-bible/agent-company/` в `apodelenko-ctrl/WEGC`. Перед продолжением читать фактический HEAD. Начальная база этой сессии: `6f5740942a9aa65395930989967baf392d85385b`.

## Не потерять замысел

Реальный owner/operator со стороны сервиса предоставляет компанию агентскому бизнесу. Не подменять основной режим обычным client-owned formation. Коммерческая нужность такого владения и юридическая пригодность остаются проверяемыми гипотезами; Wyoming/doola — кандидаты, не окончательные решения.

## Сделано

ACI-022/023 реализованы и проверены: durable SQLite state, версии, идемпотентность после рестарта, атомарные state/receipt/audit, expiry и scopes, identity revoke и all-key agent revoke внутри ACI, маркировка исторического replay. 78 тестов прошли; receipt `agents/receipts/durable-tests.json`. Базовые четыре Python-файла не менялись.

## Следом

ACI-025: реализовать локальный fixture runner на существующем sqlite_store.py; dispatch, lease, heartbeat, fencing, bounded execution, receipt и восстановление. Это не разрешение запуска внешнего LLM runtime или платных ресурсов. Перед работой читать architecture/AGENT-RUNNER-DESIGN.md и agents/QUEUE.json.

ACI-024 требует полный каталог с настоящими файлами и запуск scripts/validate_project.py; статус не закрывать по тестам одного прототипа. DNS raw download снова не работает, GitHub connector работает. Возможен дальнейший побайтовый recovery файлов с проверкой Git blob SHA; заглушки вместо недостающих документов недопустимы.

## Технические пределы

Durable API слушает только loopback; CLI хранит базу/credentials вне репозитория. Mandate expires_at обязателен в новой версии. Квитанция replay историческая, GET — текущий статус. Identity-based idempotency ещё не дедуплицирует одну бизнес-операцию между разными credential identities. Backup не является production disaster recovery. SQLite audit не защищён от администратора. Нет настоящих provider events, outbox, KYC/EIN, финансовых операций и независимого review.

## Режим исполнения

ASTRA работает интерактивно. Подготовленные специализированные роли не являются запущенными постоянными агентами; LOCAL dispatch не подтверждён. Сохранять код, тесты, receipt, очередь и журналы после результата. Не менять main, МИРА, сайт и workflows; не публиковать персональные данные и секреты; не выполнять внешние обязательства без отдельного approval.
