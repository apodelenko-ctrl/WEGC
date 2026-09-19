# ACI — вход для координатора и локального исполнителя

Обновлено execution-04, 2026-09-19. Это отдельный проект, не задание МИРА. Ветка `agent-company/bootstrap-20260919`; область записи `project-bible/agent-company/`.

## Получение актуального состояния

```bash
git fetch origin agent-company/bootstrap-20260919
git show origin/agent-company/bootstrap-20260919:project-bible/agent-company/README.md
git show origin/agent-company/bootstrap-20260919:project-bible/agent-company/agents/QUEUE.json
```

Работать в отдельном worktree и task-ветке. Не переключать занятую директорию МИРА. Пример только для новой ACI-022; проверить, что имена не заняты:

```bash
git worktree add -b agent-company/local-ACI-022 ../aci-ACI-022 origin/agent-company/bootstrap-20260919
cd ../aci-ACI-022
```

## Порядок чтения

AGENTS.md → Решения.md → WORK-STATUS.md → RESUME-STATE.md → agents/QUEUE.json → prompt роли. Затем prototype/HTTP-MOCK.md и research/ACI-012-SELF-REVIEW.md. Актуальная очередь важнее устаревших ссылок в историческом журнале.

## Уже сделано

ACI-009 HTTP mock завершена: 48 тестов всего, включая 33 новых. Не делать её заново. ACI-010/011/013/021 завершены как документы, не как внешние согласования. Всё выполняла ASTRA; отдельные постоянные workers пока не запускались.

## Первая проверка

На полном checkout выполнить:

```bash
python project-bible/agent-company/scripts/validate_project.py
python -m unittest discover -s project-bible/agent-company/prototype -p 'test_*.py' -v
```

Первый полный валидатор ещё не выполнен в текущей среде; сохранить реальный stdout/exit code для ACI-024. Не заменять отсутствующие файлы заглушками ради pass. Unit/HTTP tests уже выполнялись, но их надо перепроверить в новой среде.

## Следующая реализация

ACI-022: durable state и идемпотентность после рестарта. Дальше ACI-023: scopes/expiry/identity revoke. ACI-025: SQLite runner с fixture workers. Не подключать настоящие провайдеры и не выдавать фиктивные события за регистрацию компании.

## Передача результата

Сохранить receipt в agents/receipts/, обновить очередь и журналы, выполнить тесты, commit в task-ветку. Указать фактический SHA после публикации. Согласовывать только изменения каталога ACI; не merge чужую историю в main. Наличие задания не равно подтверждённому dispatch, а prompt не равен работающему агенту.
