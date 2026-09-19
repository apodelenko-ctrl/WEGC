# API и модель состояний — проект v0.1

2026-09-19. Это наш проект интерфейса, не документация существующего провайдера. Production не развёрнут. Mock не создаёт юрлица и не перемещает деньги.

## Сущности

`Tenant` — клиентский контур данных. `Principal` — действительное лицо/организация с документированной ролью; персональные данные хранятся приватно. `Application` — запрос на структуру. `Company` — ссылка на фактическое юрлицо после подтверждения. `AgentIdentity` — технический исполнитель. `Mandate` — субъект, компания, scopes, лимиты, срок и право отзыва. `Operation` — запрос действия. `Evidence` — проверенное подтверждение события. `ProviderConnection` — отдельные credentials и разрешённые функции. `AuditEvent` — неизменяемый журнал.

Юридическая сторона не выводится из имени агента. Tenant authorization определяется сервером из проверенного токена, не принимается как доверенное поле запроса.

## Предлагаемые маршруты

| Маршрут | Назначение | Доступ / ограничения |
|---|---|---|
| GET /v1/capabilities | Возможности и ограничения | Отдельно planned/sandbox/production |
| POST /v1/applications | Запрос структуры | Principal ref обязателен; Idempotency-Key |
| GET /v1/applications/{id} | Реальное состояние заявки | Только свой tenant |
| POST /v1/applications/{id}/approvals | Решение о подаче | Только аутентифицированный оператор; не сам агент |
| POST /v1/applications/{id}/submission | Подача через адаптер | Только после approval и production gate |
| GET /v1/companies/{id} | Компания и отдельные статусы | Не раскрывать данные другого tenant |
| GET /v1/companies/{id}/documents | Разрешённые документы | Private object storage, короткоживущие ссылки |
| POST /v1/companies/{id}/mandates | Выдать полномочия агенту | Только уполномоченный оператор |
| POST /v1/mandates/{id}/revocation | Отозвать мандат | Немедленная блокировка новых операций |
| POST /v1/operations | Запрос операции | Scope, company, expiry, risk policy, idempotency |
| GET /v1/operations/{id} | Статус и доказательства | submitted не равно completed |
| POST /internal/provider-events/{provider} | События провайдера | Отдельная проверка подлинности и replay-защита |

MCP добавляется адаптером над этими контрактами после стабилизации auth и scopes. Наличие MCP само по себе не подтверждает полномочия.

## Раздельные состояния

Application: `draft → review_required → approved_for_submission → submitted → completed`, с отдельными `action_required/rejected/cancelled`.

Formation: `not_submitted/submitted/formed/rejected`.

EIN: `not_requested/requested/issued/action_required`.

Payments: `not_requested/submitted/approved/restricted/rejected/closed`.

Mandate: `draft/active/revoked/expired`.

Operation: `requested/awaiting_approval/authorized/submitted/succeeded/failed/unknown`.

Не сворачивать эти измерения в одно поле `company_ready`. `formed` не делает payments approved. `approved` провайдером не отменяет отзыва мандата. При потере ответа операция `unknown` до reconciliation, а не автоматически failed с повторным списанием.

## Идемпотентность и события

Ключ уникален внутри tenant и операции; хранится canonical request hash. Тот же ключ/тот же запрос возвращает прежний результат. Другой payload с тем же ключом — conflict. В production нужен transactional store/outbox, а не память процесса.

Событие содержит provider ID, external event ID, тип, время, привязку к компании, evidence ref и результат проверки подлинности. Повторы не создают дубликаты; событие чужой компании отклоняется; подпись, источник и replay window проверяет backend, а не языковая модель. Необходимы reconciliation и обработка событий не по порядку.

## Полномочия

LLM предлагает действие; детерминированный backend проверяет мандат и политику. Ключи регистратора/банка не выдаются агенту напрямую. Штатные действия внутри предварительного мандата могут исполняться без ручной проверки каждого шага. Исключительные корпоративные решения и действия вне мандата требуют отдельного разрешения.

Лимиты расходов и бюджеты — утверждаемые параметры; значений сейчас нет. В test fixtures денежных сумм не требуется.

## Локальный артефакт этого checkpoint

`prototype/lifecycle.py` — чистая in-memory модель с синтетическим Actor. Проверяет последовательность и логические запреты, но **не реализует реальную аутентификацию, безопасность сети, persistence, webhooks, banking или API server**. Все evidence refs имеют prefix `sim:`. Не использовать как production access-control component.

## Критерии последующей инженерной реализации

Contract tests, настоящая проверка auth и tenancy, approvals, revocation, outbox, повторные события, секрет-хранилище, отдельные окружения, резервное копирование и restore. Security review независим от прохождения unit-тестов модели. Provider endpoints и требования берутся только из согласованной документации, не угадываются.
