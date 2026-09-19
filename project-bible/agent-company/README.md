# Agent Company Infrastructure — библиотека проекта

Рабочее обозначение **ACI**; не утверждённый бренд. Основана 2026-09-19. Владелец продукта: Артём. Координатор: ASTRA.

Репозиторий `apodelenko-ctrl/WEGC`, ветка `agent-company/bootstrap-20260919`, область работы только `project-bible/agent-company/`. Ветка публичная и наследует историю WEGC; main, МИРА и deployment не изменять. KYC, секреты и закрытые операционные данные здесь не хранятся.

## Концепция

API-first инфраструктура для бизнеса, выполняемого ИИ-агентом. Действительный собственник/оператор со стороны сервиса предоставляет компанию; агент получает ограниченные отзываемые полномочия. Это основная гипотеза, не подмена обычным оформлением на клиента. Отдельно проверяем, кому такая структура нужна и кто готов за неё платить.

## Актуальный checkpoint

**execution-06:** durable SQLite API и local fixture runner реализованы; всего **97 тестов прошли**. В этой сессии завершены ACI-022, ACI-023, ACI-025. Очередь: 28 задач, 16 done, 3 ready, 9 blocked. Это счётчик артефактов и задач, не процент готовности бизнеса. Постоянные специализированные LLM-агенты не запущены.

## Начать чтение

| Материал | Содержание |
|---|---|
| [Концепция](CONCEPT.md) | Исходный замысел и модель продукта |
| [Решения](Решения.md) | Решения владельца, предложения, открытые вопросы и исправления |
| [Находки](Находки.md) и [исходные источники](SOURCES.md) | Результаты первого исследования |
| [Почему ещё не стало обычным сервисом](research/WHY-NOW-AND-FAILURE-TESTS.md) | Конкуренты, правила и критерии пересмотра гипотезы |
| [Покупатель и спрос](research/ACI-010-CUSTOMER-HYPOTHESES.md) | Гипотезы сегментов и неотправленный интервью-гайд |
| [Капитал, прибыль и IP](research/ACI-011-ECONOMIC-RIGHTS.md) | Варианты прав сторон для дальнейшей проверки |
| [Правовой вопросник](research/LEGAL-DILIGENCE.md) | Что выяснить до пилота |
| [Уточнение Singapore](research/SINGAPORE-FOLLOWUP.md) | Источники ACRA |
| [Roadmap](ROADMAP.md) | Этапы и актуальная последовательность |
| [Партнёрские черновики](partners/DRAFT-REQUESTS.md) | Подготовлены, не отправлены |
| [Проект API](architecture/API-CONTRACT.md) | Целевой контракт, не весь реализован |
| [Исходный прототип](prototype/README.md) и [HTTP mock](prototype/HTTP-MOCK.md) | Сохранённый baseline |
| [Durable API](prototype/DURABLE-MOCK.md) | SQLite, версии, expiry/scopes/revocation и исторические квитанции |
| [Fixture runner](prototype/FIXTURE-RUNNER.md) | Реальный локальный код lease/fencing/recovery, не модельные агенты |
| [Самопроверка](research/ACI-012-SELF-REVIEW.md) | Исторический авторский review, не независимый аудит |
| [Runner-design](architecture/AGENT-RUNNER-DESIGN.md) | Целевая среда исполнения; реализован пока fixture subset |
| [Правила](AGENTS.md), [роли](agents/ROLES.json), [вход исполнителя](agents/START-HERE.md) | Область работы и handoff без вмешательства в МИРА |
| [Очередь](agents/QUEUE.json) | Зависимости, evidence, следующие задачи и блокеры |
| [Статус](WORK-STATUS.md), [возобновление](RESUME-STATE.md), [Контроль-борд](Контроль-борд.md) | Фактическая работа и история |

## Проверки из корня репозитория

```bash
python project-bible/agent-company/scripts/validate_project.py
python -m unittest discover -s project-bible/agent-company/prototype -p 'test_*.py' -v
python project-bible/agent-company/prototype/fixture_runner.py
```

Полный checkout validator ACI-024 ещё не выполнен: полный каталог не восстановлен локально. Через connector уже восстановлены и проверены по SHA исходные файлы кода; это рабочий путь, не глобальный блокер. Нельзя заменять отсутствующие документы заглушками. Unit/HTTP/SQLite/runner тесты выполнены: [97 tests receipt](agents/receipts/runner-tests.json). Demo завершился: [fixture receipts](agents/receipts/fixture-runner-smoke.json).

Следом ACI-024 — полный проверенный snapshot и валидатор; ACI-027 — stable business operation IDs и outbox; ACI-028 — безопасная процедура восстановления с учётом отзывов credentials. Внешние провайдеры, письма, формы, регистрации и расходы требуют отдельного owner approval. Simulated не равно formed; fixture worker не равен постоянно работающему LLM-агенту.
