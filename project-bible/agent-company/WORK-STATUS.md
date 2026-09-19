# WORK-STATUS

2026-09-19 · execution-06 · ASTRA. Ветка `agent-company/bootstrap-20260919`; только каталог ACI. Первый commit этой сессии: `e014c92911f019a4ae1af36a812da013299faa1f`. Последний SHA текущего checkpoint определяется Git-историей ветки.

## Выполнено в этой сессии

**ACI-022:** транзакционный SQLite store, сохранение заявок/версий/квитанций после рестарта, optimistic version checks, восстановление после исключения и принудительного завершения процесса до commit; изолированный backup/restore test.

**ACI-023:** expiry identity и мандата; application/action scopes; отзыв одного identity и всех ключей agent_id в ACI; запрет повторного provisioning отозванного агента; текущая авторизация до выдачи historical receipt. В симуляции application_id представляет границу будущей компании, а не настоящую регистрацию.

**ACI-025:** durable fixture task/attempt state, атомарный claim, heartbeat, lease expiry, fencing token, отклонение stale results, зависимости, предел попыток, повторная квитанция и bounded execution. Приёмка fixture результата детерминирована, не равна независимому review.

## Фактические проверки

**97 tests, OK, exit code 0:** 48 baseline, 30 durable API, 19 runner. Проверены отдельный процесс и перезапуск, конкурентные обращения/claim, rollback, expiry/revocation, неправильные scopes, исторический replay, истечение lease и повторный результат. Все девять Python-файлов имеют hashes в [receipt](agents/receipts/runner-tests.json); новые blob SHA GitHub совпали с протестированными.

Demo исполнил две связанные fixture задачи и завершился с exit code 0; [квитанции](agents/receipts/fixture-runner-smoke.json). В demo input_revision из нулей — явно обозначенный синтетический marker, не реальный commit. Ни один LLM worker этим тестом не запускался.

## Очередь

28 задач: **16 done, 3 ready, 9 blocked**. Ready: ACI-024 — полный snapshot/checkout validator; ACI-027 — business operation IDs и transactional outbox на mock; ACI-028 — безопасное восстановление без возврата отозванных permissions. Это не показатель готовности коммерческого сервиса.

ACI-024 не завершена. Прямое скачивание не работает в текущей среде, но connector content recovery с проверкой SHA доступен и уже использован для кода. Полный набор документов ещё не восстановлен; поэтому полный валидатор не запускался и pass не заявлен. Это не блокирует весь проект.

## Что остаётся вне готового объёма

Независимый ACI-012 review; настоящая проверка личностей и компаний; внешние webhooks/outbox/reconciliation; KYC/EIN, банковские и платёжные интеграции; production auth; защищённый аудит; приватный production runtime и живые LLM-исполнители. Backup старой базы может восстановить более ранние permissions/receipts; ACI-028 не закрывается простым snapshot test.

Правовая структура, спрос, бюджет и партнёры не утверждены окончательно. Письма, регистрации, покупки, банковские заявки и deployment не выполнялись. Main, МИРА и workflows не менялись. Тестовые процессы завершены; фонового продолжения после сессии нет.
