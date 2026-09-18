# MIRA-DEVELOPERS-20260919-01 — база застройщиков и связей проектов

CLOUD research/implementation; LOCAL — private mail/CRM reconciliation, затем CLOUD после передачи. Начато по прямому запросу владельца. Roadmap: `project-bible/mira/operations/AUTONOMOUS-MIRA-ROADMAP.md`, AUT-02/AUT-07.

1. Читать существующие `data/phuket-developer-master.csv`, pilot, alias map, TOP60 contact QA, sales stage register/outreach queue и catalogue. Не считать все строки независимыми застройщиками.
2. Продолжить `research/developer-expansion-2026-09-19/RESUME.json`; для каждой из 618 Phuket-карточек найти первичный источник/застройщика/юрпродавца либо сохранить точный пробел. Затем подключить другие действующие market feeds; не считать Phuket-аудит завершением всех 678 карточек.
3. По застройщику собрать общий и partner/sales email, публичный рабочий телефон, ФИО/роль, messenger/social links, broker portal, проекты и field-level источники/даты. Не угадывать контакт и не выводить договор из сайта.
4. Приватно сопоставить CRM, переписку Botanica и The Title, подписанные документы и проектную область действия. Для Botanica найдена текущая переписка: LOCAL обязан сначала прочитать существующий тред и сверить новую стадию. Старые not_sent в CSV не считать текущей истиной. Не отправлять знакомство повторно. Письма/личные контакты/документы — в private CRM, не Git.
5. Запустить registry.py, проверить diff и метрики. Generated JSON — исследовательская проекция; текущие договоры и CRM-статусы не меняются импортом старого CSV.
6. Импорт: dry-run → external-ID matching → конфликтный карантин → повторный импорт без дублей → receipt counts. Требует принятой private CRM schema/backup.

Результаты: developers/project-links/enrichment-queue/metrics, sources по полям, unresolved/ambiguous list, карта остальных старых источников, next cursor и обязательный NIGHT-REPORT. Подтверждения contract active требуют evidence и проекта. Никаких новых внешних отправок этим исследовательским заданием.
