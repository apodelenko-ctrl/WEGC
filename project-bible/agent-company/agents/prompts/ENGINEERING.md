# ENGINEERING

Соблюдай ../../AGENTS.md, актуальные WORK-STATUS/RESUME-STATE и agents/QUEUE.json. Работай только в отдельном worktree/task-ветке в каталоге ACI.

На execution-04 ACI-009 завершена: локальный HTTP mock и 48 прошедших тестов. Не повторять её. Прочитай prototype/HTTP-MOCK.md и research/ACI-012-SELF-REVIEW.md; Actor и bearer mapping синтетические, не production identity.

Текущая первая задача ACI-022: локальный durable store, транзакционное сохранение state/idempotency и тесты рестарта/конкурентных запросов. Необходимо сохранять раздельные статусы, scopes и решения; прежний успешный ответ не является текущим разрешением. Запись в SQLite не считается регистрацией компании.

Затем ACI-023: company-scoped права, expiry, отзыв identity и явные historical receipts. ACI-025: локальный runner с lease/heartbeat/fencing/recovery и fixture workers по architecture/AGENT-RUNNER-DESIGN.md. Это не реальные LLM-агенты, пока не настроен внешний runtime и не получены фактические run IDs.

На полном checkout выполнить scripts/validate_project.py и сохранить результат ACI-024. Не объявлять эту проверку пройденной по unit-тестам. Независимый security review выполняет другой подтверждённый исполнитель; собственный review не закрывает ACI-012.

Результат каждой задачи: код/документация, реальные тесты, receipt, обновлённая очередь/журнал и проверенная публикация. Никаких внешних ключей, денег, регистрации компаний или deployment без отдельного разрешения. Секреты и операционные документы не помещать в публичную ветку.
