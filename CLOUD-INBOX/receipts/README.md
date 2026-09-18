# LOCAL → CLOUD: подтверждение получения и результаты

Это инструкция и пустой образец, НЕ подтверждение, что локальный агент уже прочитал или выполнил задание.

Каждое задание имеет stable task ID. Для текущего задания создать `CLOUD-INBOX/receipts/MIRA-LOCAL-20260918-02.json` при фактическом чтении. Ответ локальный агент сохраняет в своей reviewed-ветке; в issue #14 даёт постоянную GitHub-ссылку на commit/file. CLOUD читает этот ответ при следующем рабочем запуске и обновляет общий учёт. При безопасном доступе к общей research-ветке допустим тот же путь там: сначала проверить наличие и свежий SHA, не затирать чужой receipt.

Сначала accepted, затем in_progress, после фактической проверки done/partial/blocked. Обновлять одну запись последовательно или добавлять версии событий с указателем на предыдущую. Задание не становится done по факту импорта файла или зелёного CI.

```json
{
  "task_id": "MIRA-LOCAL-20260918-02",
  "status": "accepted",
  "read_at": "REPLACE_WITH_ACTUAL_ISO_TIMESTAMP",
  "source_commit_read": "REPLACE_WITH_EXACT_RESEARCH_COMMIT",
  "local_branch": "REPLACE_WITH_ACTUAL_BRANCH",
  "local_commit": "REPLACE_WITH_ACTUAL_HEAD",
  "startup_inbox_rule_installed": false,
  "completed": [],
  "skipped_already_done": [],
  "blocked": [],
  "tests": {"local": [], "ci": [], "live": []},
  "imports": {"projects_accepted": null, "project_holds": null, "agency_candidates_accepted": null, "duplicates": null},
  "new_publication_approved_media": null,
  "production_urls": [],
  "needs_cloud": [],
  "needs_owner": [],
  "evidence_urls": []
}
```

Подставлять только реальные значения; не коммитить REPLACE_WITH как якобы заполненные факты. В live-результате заявки указывать обезличенные этапы, не email, subject, номер квитанции, персональный payload, OTP, cookies, токены или снимок рабочей базы. Публичный технический отчёт отдельно от приватных доказательств.

Код/данные/документы, локальная проверка, production-публикация, реальный пользовательский тест и договорная активация — разные категории результата. CLOUD не исполняет команды на Mac и не считает собственный комментарий receipt LOCAL.
