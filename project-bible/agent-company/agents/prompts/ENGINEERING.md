# ENGINEERING

Соблюдай ../../AGENTS.md, актуальные WORK-STATUS/RESUME-STATE и agents/QUEUE.json. Работай в отдельном worktree/task-ветке, только каталог ACI.

На execution-06 ACI-009/022/023/025 завершены в локальном объёме: HTTP mock, SQLite state, expiry/scopes/revocation и fixture runner. 97 тестов прошли. Не начинать эти задачи заново. Читать prototype/DURABLE-MOCK.md и prototype/FIXTURE-RUNNER.md. Actor/identity provisioning синтетические; реальные компании и люди не верифицированы.

Сначала ACI-024: полный проверенный каталог, scripts/validate_project.py, stdout/exit code и реальный revision. Connector content recovery с проверкой Git blob SHA — допустимый путь; невозможность direct download не является глобальным blocker. Не подменять недостающие документы заглушками и не закрывать validator по unit-тестам кода.

Затем ACI-027: стабильный business operation ID, transactional outbox, текущая авторизация перед dispatch, mock reconciliation неизвестного результата. Identity-scoped request cache не решает дедупликацию после ротации credentials. Никаких реальных финансовых API.

ACI-028: fail-closed восстановление старого backup, epoch/rotation и сверка отзывов. Изолированный snapshot test не является готовым production disaster recovery. Не возвращать отозванные permissions автоматически.

Каждая задача даёт код/документ, реальные тесты, receipt, обновление очереди/журналов и проверенную публикацию. Независимый review требует другого подтверждённого исполнителя. Нет внешних расходов, регистрации, provider calls и deployment без отдельного approval. Постоянный LLM runtime не запускался.
