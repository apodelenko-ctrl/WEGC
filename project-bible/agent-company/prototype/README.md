# Локальные прототипы ACI

2026-09-19 · execution-04. Python 3.10+, стандартная библиотека. Никаких настоящих компаний, KYC, счетов, документов, платежей или LLM workers.

## Исходная модель

lifecycle.py и test_lifecycle.py — неизменённые файлы bootstrap с 15 unit-тестами. Actor — синтетический контекст, не механизм установления личности. Бизнес-состояния существуют только в памяти.

## Новый HTTP mock

mock_http.py и test_mock_http.py добавляют локальный HTTP adapter, серверное отображение синтетических bearer-токенов на роли, проверку payload, идемпотентность внутри процесса и 33 новых contract/HTTP теста. [Инструкция и точные ограничения](HTTP-MOCK.md).

Из корня репозитория:

```bash
python -m unittest discover -s project-bible/agent-company/prototype -p 'test_*.py' -v
python project-bible/agent-company/prototype/mock_http.py --credentials-file /tmp/aci-session.json
```

Общий результат текущего прогона: **48 tests, OK**. Тестовые credentials создаются новым файлом вне клона; не использовать их для внешних сервисов и не публиковать.

## Не реализовано

Durable state, expiry и глобальный revoke identity, production auth/TLS, неизменяемый журнал, реальные provider webhooks и финансовые функции, EIN, документы и постоянные агенты. HTTP server нельзя публиковать наружу. [Самопроверка](../research/ACI-012-SELF-REVIEW.md) не заменяет независимый review.

Следующие задачи: ACI-022 → durable state; ACI-023 → scopes/expiry/revoke; ACI-025 → локальный fixture runner. Все результаты simulation, не юридическое или production security approval.
