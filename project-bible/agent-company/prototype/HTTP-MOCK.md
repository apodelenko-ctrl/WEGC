# HTTP mock — ACI-009

2026-09-19. Реализована локальная HTTP-оболочка над lifecycle.py. Исходная модель и её 15 тестов не изменены; добавлены 33 contract/HTTP-теста. Полный локальный прогон: 48 tests, OK.

## Запуск

Python 3.10+, стандартная библиотека. Из корня репозитория:

```bash
python -m unittest discover -s project-bible/agent-company/prototype -p 'test_*.py' -v
python project-bible/agent-company/prototype/mock_http.py --credentials-file /tmp/aci-session.json
```

Файл credentials должен быть новым и находиться вне клона; существующий файл не перезаписывается. CLI генерирует отдельные синтетические bearer-токены agent/operator, записывает их с режимом 0600 и выводит loopback URL со свободным портом. Это локальные тестовые credentials, не KYC и не доступ к провайдерам. Не помещать файл в GitHub. Для остановки — Ctrl+C.

Сервер разрешает только 127.0.0.1, проверяет Host, отклоняет browser Origin, ограничивает body и не журналирует bearer headers. Это не production hardening. Python прямо предупреждает, что http.server не рекомендован для production: https://docs.python.org/3/library/http.server.html (проверено 2026-09-19).

## Реализованные маршруты

GET /v1/capabilities — публичное описание именно mock-возможностей.

POST /v1/applications — JSON name + principal_ref, совпадающий с серверной ролью; Bearer и Idempotency-Key обязательны.

GET /v1/applications/{id} — snapshot заявки в своём tenant/principal.

POST /v1/applications/{id}/approvals и /submission — согласование оператором, затем подача.

POST /v1/applications/{id}/simulate-formation — только оператор имитирует подтверждение. Это не webhook и не state filing.

POST /v1/applications/{id}/payment-submission и /simulate-payment-approval — отдельные mock-состояния, только оператор. Платежи не реализованы.

POST /v1/applications/{id}/mandates — agent_id + scopes; выдача оператором. Разрешены только фиктивные read_documents и prepare_invoice.

POST /v1/applications/{id}/operations — action, проверяемый по мандату агента.

POST /v1/applications/{id}/revocation — отзыв мандата оператором.

Пустые действия принимают `{}`. Все успешные POST сейчас возвращают 200; ошибки имеют JSON error.code. Неизвестные поля и попытки подставить роль в body отклоняются. Неизвестный либо чужой объект возвращает 404. Это подмножество проекта API-CONTRACT, не реализация всех будущих /companies, /documents, /operations и EIN endpoints.

## Повторы и состояния

Каждый POST требует idempotency key. Ключ разделён tenant/principal/role/agent/path; иной payload с тем же ключом даёт conflict. Внутрипроцессный lock предотвращает дубликаты конкурентных одинаковых запросов. После рестарта гарантия исчезает — нужен durable store.

Повтор возвращает snapshot первого ответа, а не актуальное состояние; актуальное состояние читается GET. Повтор старой выдачи после отзыва не восстанавливает мандат. Перед повтором операции права проверяются заново: после revocation даже закэшированный запрос отклоняется.

## Чего здесь нет

Реальной аутентификации человека/KYB, TLS, постоянного журнала, базы данных, expiry/ротации ключей, полного kill switch, настоящих документов, денежных операций, provider webhooks, EIN, реестра компаний и работающих LLM workers. Модель Actor доверяется только серверному fixture mapping, не клиентскому JSON. Отдельный независимый security review ещё не выполнен.

См. [самопроверку](../research/ACI-012-SELF-REVIEW.md) и [отчёт тестов](../agents/receipts/http-mock-tests.json). Никаких внешних регистраций или финансовых подключений не выполнялось.
