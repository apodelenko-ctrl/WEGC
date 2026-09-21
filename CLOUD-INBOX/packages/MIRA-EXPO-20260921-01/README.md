# Исполнимый пакет подготовки выставочного входа

Source main `9a5f4c89168aa9e7995ceebf6db8dbaaf9a61137`. Печатный QR в обоих готовых PDF декодирован как `https://wegc.fund/mira/start/`. Патч сохраняет адрес, выбранную визуальную подачу, защищённый вход и каталог.

## Что меняет патч

- На первом экране `/mira/start/` основная кнопка ведёт на существующее подключение агентства, каталог остаётся рядом.
- После локальной анкеты есть явная кнопка перехода к подключению. Общий qualifier используется также growth/business.
- Sticky CTA ведёт к подключению; скачанный бриф включает его постоянную ссылку и объясняет необходимость приглашения.
- Два исходника: `scripts/mira-build-launch.py`, `mira/launch/launch.mjs`. Generated pages создаёт штатный builder. Не редактировать только generated HTML: следующая сборка затрёт результат.

**Патч подготовлен, ещё не опубликован на сайте.** Он устраняет навигационный разрыв, но сам не создаёт публичный канал запроса приглашения, не открывает Access и не подключает CRM.

## Применение LOCAL

Сначала безопасный checkout/worktree от актуального main, сохраняющий пользовательские изменения. PACKAGE — локальный путь к этому пакету после чтения research-ветки; REPO — целевой изолированный checkout.

```sh
python "$PACKAGE/apply_patch.py" --repo "$REPO"
python "$PACKAGE/apply_patch.py" --repo "$REPO" --apply
```

По умолчанию только preflight. До записи любого файла проверяются оба source SHA256 и оба replacement SHA256. Чужое изменение останавливает применение без записи первого файла. Повторный запуск идемпотентен. Прерывание процесса между двумя файловыми записями не является атомарной транзакцией: повторить preflight, затем закончить применение; не deploy частичный checkout. `source.patch` — читаемый unified diff; `git apply --check` прошёл на исходном main.

В целевом checkout:

```sh
python scripts/mira-build-launch.py
node --check mira/launch/launch.mjs
python -m unittest discover -s tests -p 'test_mira_launch_public.py' -v
```

Далее текущие mobile/CSP/public browser проверки и public-only release по существующей процедуре. Не включать CLOUD-INBOX, research, private code/данные в публикацию. Не merge всей research-ветки. Принять live страницы и ссылки на deployed SHA.

## Проверки CLOUD

7/7 тестов preflight/idempotency/source drift/evidence gates. Builder выполнен на реальном наборе 618 записей; все ID и 618 detail routes сохранены. `mira/data/phuket.json` и access page побайтово не изменены. JS syntax PASS. Генерируемые изменения только start/growth/business, плюс два исходника. Полная UI-регрессия изменённой версии и deploy ожидают LOCAL. Подробно [TEST-REPORT.json](TEST-REPORT.json).

## Машинная приёмка плана

```sh
python "$PACKAGE/readiness.py" project-bible/mira/operations/LAUNCH-EVIDENCE.json --out project-bible/mira/operations/LAUNCH-READINESS.json
python -m unittest discover -s "$PACKAGE" -p 'test_*.py' -v
```

Скрипт требует все 12 уникальных EXPO IDs. `prepared`, `partial`, `blocked`, `not_run` не становятся PASS. Accepted gate требует evidence и времени проверки; истёкшее evidence исключается. Это проверка целостности статуса, не автоматическое доказательство достоверности receipt и не live-тест серверов.

Следующий шаг: EXPO-03/05 из [задачи LOCAL](../../tasks/MIRA-EXPO-20260921-01.md); дальнейший rollout — [план до выставки](../../../project-bible/mira/operations/EXHIBITION-LAUNCH-2026-09-25.md).
