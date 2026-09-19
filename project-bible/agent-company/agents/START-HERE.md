# ACI — вход для координатора и локального исполнителя

Обновлено execution-06, 2026-09-19. Отдельный проект, не МИРА. Ветка `agent-company/bootstrap-20260919`; область записи `project-bible/agent-company/`.

```bash
git fetch origin agent-company/bootstrap-20260919
git show origin/agent-company/bootstrap-20260919:project-bible/agent-company/README.md
git show origin/agent-company/bootstrap-20260919:project-bible/agent-company/agents/QUEUE.json
```

Использовать отдельный worktree/task-ветку; не переключать занятую директорию МИРА. Пример для ACI-024, предварительно проверить свободные имена:

```bash
git worktree add -b agent-company/local-ACI-024 ../aci-ACI-024 origin/agent-company/bootstrap-20260919
cd ../aci-ACI-024
```

## Читать

AGENTS → Решения → WORK-STATUS → RESUME-STATE → QUEUE → prompt роли. Затем prototype/DURABLE-MOCK.md и prototype/FIXTURE-RUNNER.md. Актуальная очередь важнее исторических поручений.

## Не повторять

ACI-009, ACI-022, ACI-023, ACI-025 завершены в локальном объёме. 97 тестов прошли. Состояние, права и runner реализованы; настоящие provider/LLM integrations не подключены. Подготовленные исследовательские документы не равны внешним согласованиям.

## Первая задача — ACI-024

```bash
python project-bible/agent-company/scripts/validate_project.py
python -m unittest discover -s project-bible/agent-company/prototype -p 'test_*.py' -v
```

Нужен полный каталог настоящих файлов. В текущем контейнере из connector восстановлен и проверен кодовый subset; полная библиотека не восстановлена. Полный validator pass ещё не заявлен. Сохранить фактические stdout, exit code и revision. Доступен connector recovery с побайтовой проверкой SHA; прямой download не единственный путь. Заглушки недопустимы.

## Следующие задачи

ACI-027 — stable business operation IDs и atomic outbox с mock/reconciliation. ACI-028 — fail-closed restore/credential epoch, чтобы старый backup не возвращал отозванные права. ACI-012 — независимый review отдельным подтверждённым исполнителем.

## Передача результата

Receipt → очередь/журналы → тесты → commit → remote verification. Указать фактический SHA после получения. Не merge чужую историю в main. Prompt не является работающим агентом; fixture runner не является постоянным LLM runtime. Не выполнять внешние обязательства без отдельного approval и не хранить секреты в public GitHub.
