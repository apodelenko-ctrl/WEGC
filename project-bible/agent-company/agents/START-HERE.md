# ACI — вход для координатора и локального агента

Это новый проект, не задание МИРА. Рабочая база: `agent-company/bootstrap-20260919`. Каталог: `project-bible/agent-company/`.

## Получение задания

Безопасно прочитать библиотеку, не переключая текущую рабочую ветку:

```bash
git fetch origin agent-company/bootstrap-20260919
git show origin/agent-company/bootstrap-20260919:project-bible/agent-company/README.md
git show origin/agent-company/bootstrap-20260919:project-bible/agent-company/agents/QUEUE.json
```

Для изменений использовать отдельный worktree и собственную task-ветку; не переключать занятую рабочую директорию МИРА. Перед созданием проверить, что имя ветки и каталог не используются. Пример для ACI-009:

```bash
git worktree add -b agent-company/local-ACI-009 ../aci-ACI-009 origin/agent-company/bootstrap-20260919
cd ../aci-ACI-009
```

## Порядок чтения

AGENTS.md → Решения.md → WORK-STATUS.md → RESUME-STATE.md → agents/QUEUE.json → файл своей роли. Назначение роли в реестре не даёт credentials или юридических полномочий.

## Доступные роли

Реестр: `agents/ROLES.json`. Координатор ASTRA; специализированные роли LEGAL-RESEARCH, PROVIDER-RESEARCH, PRODUCT, ENGINEERING, SECURITY-QA. Их prompts готовы, но отдельный runtime не provisioned. Не заявлять о получении задания локальным агентом без receipt.

## Первая инженерная задача

ACI-009: превратить локальную модель состояний в тестируемый HTTP mock-adapter по architecture/API-CONTRACT.md. Только локально, без настоящих провайдеров. Не считать fixture Actor настоящей аутентификацией.

## Отчёт

Сохранить новый receipt в `agents/receipts/`, обновить очередь и журналы, выполнить тесты, commit в своей ветке. В отчёте указать фактический commit SHA после его получения. Не присылать обещание вместо результата. Интегрировать только изменения каталога ACI после review, не сливать всю историю чужих задач.
