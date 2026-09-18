# MIRA-AUTONOMY-20260919-01 — исполнение принятой архитектуры

Владелец утвердил roadmap и начало реализации. Полная постановка и AUT-00–AUT-10: `project-bible/mira/operations/AUTONOMOUS-MIRA-ROADMAP.md`.

CLOUD продолжает обе базы и готовит code/data packages. LOCAL сохраняет текущий checkpoint CRM/собственной почты; **не начинать заново установку или выбор CRM**. Прежняя задача MIRA-CLOSEOUT-20260918-01 принята; её финальный отчёт пока не получен. Не переносить по одному только ACK.

LOCAL после checkpoint:
- вернуть per-item closeout T01–T14, неизвестное/blocked явно;
- передать sanitised manifest кода/патчей/доступов, version/schema/counts, encrypted backup reference/checksum и restore procedure;
- уточнить состояние новой owner-requested self-hosted mail и disposition предыдущего Brevo-варианта, не запрос выбора CRM;
- сопоставить существующие developer IDs, переговоры Botanica/The Title и договоры с CRM; исходную private почту в Git не копировать;
- подключать новый registry/planner избирательно: planner выдаёт только draft proposal, **не является live интеграцией**;
- сохранять принятую изоляцию Phuket buyer / MIRA agency / MIRA developer и assignedUserId fix.

CLOUD принимает результат только после восстановления и сквозных проверок без Mac. При отсутствии пригодного сервера/доступа сохранить конкретный blocker и подготовленный вариант; закупка не предполагается автоматически. Mac CRM не выключать до принятого cutover.

Общий текущий status — MASTER-STATUS; machine queue — QUEUE.json; history — events и Git. Receipt этого блока: `CLOUD-INBOX/receipts/MIRA-AUTONOMY-20260919-01.json` с отдельными flags code_ready, data_ready, crm_integrated, cloud_restored, deployed, live_accepted и remaining. Не заменять старые receipts и не ставить all_done=true по unit tests.
