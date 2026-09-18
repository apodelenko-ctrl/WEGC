# МИРА — общий реестр задач, хвостов и истории

**Единая текущая сводка для CLOUD и LOCAL.** Срез:18.09.2026 17:46 UTC /19.09.2026 00:46 Asia/Bangkok. Операционный день18.09; даты исходных событий не переименовывать. Task: MIRA-CLOSEOUT-20260918-01. Владелец исполнения интеграции:LOCAL; research: CLOUD. Статус: **OPEN — требуется отчёт LOCAL**.

## Что проверено и что означает этот файл

Проверены доступные фрагменты сегодняшних разговоров,12 удалённых веток,8 PR (MIRA открытых нет, HERD PR1 вне задачи), issue14,15 последних Actions runs,174 коммита research-ветки с17.09 17:00 UTC, C01–C16/RESUME, общие журналы,32 CSV data/sales, исходники ночного пакета и3 актуальных receipts LOCAL/MKT/OMNI. Research snapshot:e0f7e405c0e040ff4208a6c3b26f9f6a20b33fa6; main:4972b4bca407d6944ca39dfacc810dc16147efbb. История Git доступна по этим SHA.

Это не доступ ко всем приватным worktree LOCAL или ко всем несохранённым репликам ChatGPT. Их инвентаризация и возврат отчёта ниже обязательны. Общие файлы уже существовали, но текущие флаги QUEUE/board и старый research RESUME отставали от receipts. Старые записи сохраняются как история, текущая сводка — здесь; машинная очередь — QUEUE.json; доказательства — receipts и events. Не создавать новую конкурирующую очередь.

## Фактически закрыто / сохранено

| Работа | Результат | Доказательство / граница |
|---|---|---|
| C01–C16 | Исследование и контент закончены; старые ночная/дневная автоматизации выключены | Дневной RESUME, C16; это не завершение внедрения |
| Проекты | Опубликованы5 рынков,678 research-карточек:618 Phuket+15 Bali+15 Dubai+15 Vietnam+15 Montenegro | PR15; source4bd05d7, merge2218605, generated4972b4b;30 новых VN/ME:27complete,3partial; commercial0 |
| Публикация | Deploy35327093244 и full verification35327298919 success | [PR15](https://github.com/apodelenko-ctrl/WEGC/pull/15), [приёмка](https://github.com/apodelenko-ctrl/WEGC/actions/runs/35327298919); отменённый промежуточный Pages run заменён успешным |
| Техническая заявка | Решение оператора, видимость заявителю и новый OTP вход пройдены | LOCAL receipt17:27:20UTC; старый pending снят; это не commercial onboarding |
| CRM | EspoCRM10.0.8/MariaDB11.4 в private Lima VM;12 реальных C10 Accounts +synthetic отдельно, Notes,20 inactive templates; повторный импорт без дублей и restart persistence | LOCAL/MKT receipts, private checkpoint f72cee88463379a9bf90acf29912d2f4d7b08243;68 staging не импортированы |
| OMNI/KB |23 блока,47 старых проектных ссылок не одобрены;3 изолированных профиля; native CRM Note+Task/pause/replay прошли LOCAL | OMNI receipt, private6af4703, sourceed2db2e9;43 local checks; реальный канал/модель не приняты |
| Новый client flow | Бриф→research shortlist→CRM→специалист,53 CLOUD tests | e0f7e40; **LOCAL ещё не подтвердил именно эту версию**;1 активный клиентский бриф на контакт |
| QR/demo/dashboard | Публичный текст согласован с invited intake; dashboard обновлён из source | LOCAL receipt; физический QR и РФ без VPN не приняты |
| X01 | Албания/север Италии исследованы |7f858db; не опубликованный новый ассортимент; X02+ не выполнены |

## Вся найденная незавершённая работа — единое задание LOCAL

LOCAL брать после текущего безопасного checkpoint. Не переустанавливать сделанное и не повторять закрытую заявку. Обновлять каждую строку фактами. Если один пункт заблокирован — продолжать независимые.

| ID / приоритет | Ответственный | Статус сейчас | Следующее действие и условие закрытия |
|---|---|---|---|
| T01/P0 Ассистент МИРА | LOCAL, MIRA-OMNI | partial; новый flow pending | Взять e0f7e40, сохранить native Task fix assignedUserId; подключить существующие approved endpoint/model config/scoped CRM HTTPS; фактически проверить сообщение→профиль→база→CRM→ответ→handoff/pause; replay без дублей. Сайт Phuket не говорит про MIRA, включая canned greetings; записать обе реальные проверки |
| T02/P0 Каналы | LOCAL, MIRA-OMNI | NOT_RUN live | Website/email response bridge, реально используемые TG/WA/MAX адаптеры по существующему доступу; Telegram Business permissions/revocation, global suppression и operator notification/intent/status mapping. Для неиспользуемого канала явное deferred с причиной, не фиктивный PASS |
| T03/P0 Почта/Brevo | LOCAL, MIRA-MKT |20 inactive templates готовы; provider pending | Проверить имеющиеся учётки; подключить Espo mailbox SMTP/IMAP/OAuth и Brevo sender/ReplyTo/domain; выбранная почта/Gmail connector не равны подключённой Espo. Не спрашивать повторно выбор ПО; запросить только точно отсутствующий доступ |
| T04/P0 Контроль отправок | LOCAL, MIRA-MKT | M04 частично/NOT_RUN | Реально проверить cap200, stop-on-reply, unsubscribe/global suppression, complaint/bounce/delivery и kill-switch; закрыть unresolved footer. A01/A14 локально пройдены, A03/A04/A13 partial; остальные тесты не считать выполненными. Пилот/внешняя отправка — только при выполненных действующих gates |
| T05/P1 Надёжность CRM/OMNI | LOCAL | partial | Scoped non-admin role, hosted runtime при необходимости, backup+restore, retention/load, private bridge security. Доказательства сценариями, а не флагами |
| T06/P1 Полный счётчик агентств | CLOUD+LOCAL | техническая свёртка готова, canonical pending | Сверить старые data/sales с RU50/BY30 и private CRM; отделить юрлицо/бренд/филиал; вернуть source IDs/aliases/число до-после.332 групп — предварительно, не чистая база |
| T07/P1 Новая ночная выборка | CLOUD research; LOCAL import | scheduled | [MIRA-AGENCIES-20260919-01](tasks/MIRA-AGENCIES-20260919-01.md):47 основных+13 дополнительных городов,2 столицы отдельно; минимум10 подходящих на город, обогащение всех контактных полей; итог и незакрытое обязательны |
| T08/P1 VIVI и медиа | LOCAL | private dossier/drafts; holds | Подтвердить договорную актуальность, inventory/pricing, lead protection/downstream rights и media scope; new approved media0. Реестр30 проектов уже есть. Не публиковать private договоры/условия; factual evidence или конкретный blocker |
| T09/P1 Полевая приёмка | LOCAL | NOT_RUN | Физический QR, РФ без VPN, прямое наблюдение403 admin API; отдельные доказательства. Не повторять уже пройденную заявку и не создавать коммерческую активацию |
| T10/P1 Старые ветки | LOCAL |3 diverged ветки требуют disposition | Сопоставить патчи с текущим main: admin-checkpoint2 ahead/20 behind; cloud-onboarding2/21; russia-insights1/234. Для каждого изменения integrated/superseded/retain/apply-selectively с SHA. Не сливать целиком старые ветки/историю |
| T11/P1 Приватные хвосты | LOCAL | не видны CLOUD | Проверить собственные worktrees, branches, stash, untracked результаты и текущие поручения. Вернуть sanitised manifest path/task/source/result SHA/status. f72cee…/6af4703 и прежние internal checkpoints намеренно private; не публиковать их целиком |
| T12/P1 Общий учёт и финальный отчёт | LOCAL+CLOUD | OPEN | ACK нового задания; затем receipt по каждой строке, журнал событий и итог:что закрыто/что блокирует/кто/следующее действие. Не завершать «всё готово» при NOT_RUN |
| T14/P1 Передача из Mac в облако | LOCAL inventory; CLOUD coordination | следующий этап после текущего LOCAL checkpoint | Прямое новое намерение владельца: завершить LOCAL и перенести основной процесс в облако. Подготовить sanitised manifest кода/worktrees, CRM schema+counts, encrypted backup location, restore procedure, перечень secret names и необходимых доступов без значений, persistent storage/endpoint dependencies, unresolved tasks. Сам перенос/выключение Mac CRM ещё не выполнены; сначала выбрать пригодный постоянный runtime, проверить restore и live acceptance, затем переключать |
| T13/P2 Отложенные исследования | CLOUD/LOCAL по принадлежности | backlog, не выполнено | HF Spaces discovery, Instagram/Postiz setup, X02+ страны, multiple buyer case routing, генеративный dialogue/dynamic inventory. Не блокируют уже готовые части; назначить disposition в отчёте, не объявлять автоматически согласованными релизами |

Новый ночной поиск не прерывает действующие LOCAL задачи. Предложение из голосового чата о персональных Gmail drafts (~590/600) не является доказательством созданных черновиков и не заменяет самовольно согласованный mail-путь. Найти существующие drafts/поручения, зафиксировать реальный счётчик; не создавать дубликаты и не отправлять автоматически.

## Сколько агентств есть сейчас

| Срез | Фактический счётчик | Как трактовать |
|---|---:|---|
| Все прочитанные agency source layers после технической свёртки |332 группы | Страна+нормализованный hostname; при отсутствии домена имя.197RU,60BY,75прочие. Возможны alias-дубли и объединение независимых франчайзи. Не число проверенных юрлиц |
| Старый RU pilot |324 строки |117 уникальных написаний названий,127 доменов; есть source-seeded office hypotheses, не324 независимых агентства |
| Launch100 |100 организаций в cohort |50 прошли contact/role review,13 помечены ready_for_owner_review; не100 полностью обогащённых и не разрешённая рассылка |
| Пакет18.09 |50RU+30BY | Уже входит в332, повторно не прибавлять |
| Native Espo из C10 |12 |+1synthetic отдельно;68 night records staging.Приватный полный CRM total LOCAL ещё должен сверить |
| Полностью обогащённые всеми запрошенными каналами |не установлен | Нельзя заменить количеством строк/доменов |

[Машинный разбор и lineage](../project-bible/mira/research/agency-expansion-2026-09-19/BASELINE-AUDIT.json). Техническая дедупликация — первый проход, точный канонический счётчик остаётся T06. Суммы разных csv складывать запрещено.

Города: пересчёт по [таблице оценки01.01.2025](https://ru.wikipedia.org/wiki/Список_городов_России_с_населением_более_100_тысяч_жителей) даёт47 городов300тыс.–1млн и ещё13 при пороге250тыс. (Россия в международно признанных границах). Источник вторичный, числа округлены; актуальные official estimates требуется перепроверить.60×10=600;6000 означает около100 на город или расширение географии. Это две разные цели.

## Ветки и публикации

design/mira-editorial-motion уже является предком main (ahead0), хвоста по ancestry нет. PR8/9/10/11/12/13/15 merged; существование их веток не означает незавершённость. Research — сознательно несмешиваемая ветка обмена. HERD olives/PR1 другой проект. Три diverged ветки перечислены в T10: ancestry divergence не доказывает потерю функциональности, нужна содержательная сверка LOCAL. Частные непушенные checkpoint намеренно сохранены после отказа публиковать internal branch; public-only PR15 опубликован отдельно.

## История: что было дано, сделано и каким commit

| Событие | Исполнитель / результат | Commit / место |
|---|---|---|
| Общие журналы и очередь | CLOUD создал учёт |ba46adab04af7d9e259d122384efd811d23392e7; CLOUD-INBOX |
| CRM shortlist/drafts | CLOUD C10,12 кандидатов |78c75ea71a810d292e96bf19cdca384ab8271529; day results |
| Конкретное задание интеграции | CLOUD I1–I6 |03db1ac77f9ce30e8072121746e022251cf40198 |
| Качество/финал исследований | CLOUD C14/C15/C16 |7994591,ca4553d,4e5156a; day results |
| X01 | CLOUD исследование стран |7f858db4a4b7752d9cda5402525012416eb406be |
| Product release | LOCAL, main/Pages |PR15→22186058eb478239277ceddce52295688f5512c5→4972b4bca407d6944ca39dfacc810dc16147efbb |
| OMNI code | CLOUD |b406e01d83c977644279cc33f23e805acaba2d74 |
| Изоляция знаний | CLOUD |ed2db2e9e22956547a2c24dd93fd92bb9f31319f |
| Native CRM/заявка/MKT receipts | LOCAL evidence сохранено18.09 17:28UTC |5868b84,c38e86a; privatef72cee…; receipts |
| Native OMNI receipt/fix | LOCAL evidence |449f795; private6af4703; receipts |
| Client brief/shortlist/handoff | CLOUD53tests |e0f7e405c0e040ff4208a6c3b26f9f6a20b33fa6; LOCAL ещё pending |
| Сверка хвостов и ночной поиск | CLOUD по прямому поручению владельца |Коммит, добавляющий этот файл; точный SHA в issue14 и Git history. Не записывать выдуманный self-SHA |

Время push исторически не равно author/committer time. Где нет отдельного подтверждения push, хранить commit time и observed_at раздельно; GitHub ref/issue подтверждают доступность, а не точный момент старого push.

## Обязательный протокол отныне

На старте любого нового блока читать этот файл+QUEUE+свежие receipts. Новая задача получает ID,owner,created_at,scope,next_action и критерий закрытия. После фактического checkpoint обновить текущую строку и добавить event с task_id, UTC/ICT временем, source_sha, result_sha, pushed_branch, deployed_url/run_id либо not_deployed, test evidence, status, blocker_owner, next_action. Историю не стирать; старый pending явно superseded новым evidence. Код готов / интегрирован / опубликован / live принят / коммерчески разрешён — разные поля.

LOCAL вернуть **CLOUD-INBOX/receipts/MIRA-CLOSEOUT-20260918-01.json**: ack_at, read_source_sha, active_local_branch/head, items[{id,status,source_sha,result_sha,publication,test_evidence,remaining,blocker_owner,next_action}], private_work_manifest_sanitized, canonical_agency_counts, all_done. Статусы done/partial/blocked/deferred/superseded с причиной; all_done=false при незакрытых обязательных пунктах. Финальный текстовый отчёт в issue14 и обновление этого файла обязательны даже при блокировке. Текущая передача ≠ подтверждение получения; ACK ещё нет.


## Ночная база: canonical checkpoint 18.09.2026

T06 / MIRA-AGENCIES-20260919-01 — IN_PROGRESS. Восстановлен master-agencies.json/CSV с сохранением 332 исходных identity keys и старых IDs. После разделения ошибочного общего домена каталога (+8) и свёртки сетевых поддоменов (−3) — 337 предварительных кандидатов: 195 RU, 59 BY, 83 прочих. Это не +5 найденных агентств и не итог verified entities. C10 CRM: прежние 12 подтверждены; новых импортов 0. Саратов в работе; официальный пересчёт населения не подтверждён из-за ошибок доступа к Росстату. Event: events/2026-09-18/cloud-agencies-canonical-1807.json. Все LOCAL задачи/receipts сохранены.


## Саратов B001 — 2026-09-18T18:10:52Z

T06 IN_PROGRESS. Canonical345 (RU203/BY59/прочие83); новых кандидатов8, обогащены2 прежние записи;4 подходящих рабочих кандидата в Саратове из10, остальные требуют проверки. Прямые Telegram2, WhatsApp URL1; полная статистика и holds в [CHECKPOINT-001](../project-bible/mira/research/agency-expansion-2026-09-19/CHECKPOINT-001.md). RSS исправлен Воронеж→Саратов с сохранением ID. Canonical base SHA e31f94559265f7417f5f03240d6087197e4f9faa. CRM12 прежних импортов, новых0; рассылок0. Следующий cursor Саратов; официальная статистика населения не подтверждена. Новых обязательств LOCAL не добавлено.



## Автономная МИРА — принятое продолжение, 2026-09-18T18:36:48.626807Z

MIRA-AUTONOMY-20260919-01 / AUT-00–AUT-10: [единый roadmap](../project-bible/mira/operations/AUTONOMOUS-MIRA-ROADMAP.md). Это следующая стадия существующей системы. AUT-01/02 идут до передачи Mac; AUT-04 требует настоящего восстановления.

**Исправление T12/T14:** receipt MIRA-CLOSEOUT-20260918-01 от 18:23:20UTC подтверждает ACK (source ad312425), all_done=false. Старое «ACK нет» выше superseded. LOCAL заканчивает current private CRM/mail checkpoint; final manifest/backup/restore пока не представлены. По receipt владелец запросил собственный mail server option и пока не имеет VPS; покупки не одобрены. Старую MKT-постановку сверить с этим поручением, не навязывать повторный выбор ПО.

**AUT-02 / новая база застройщиков:** найдены existing master40, pilot31, TOP60 project-contact rows, stage8. Код сохранил все 618 IDs и создал 618 задач связи плюс40 задач контактов/CRM. Family:111/618; однозначный inherited join91, ambiguous5, unmatched family15, no family507. Это кандидаты связей, не подтверждённые продавцы. Свежие публичные контакты3 застройщиков, источники по полям. Договоры/sent/replied totals=null до private reconciliation.

**AUT-08:** pure inquiry planner с case scope, contract/project/recipient checks и стабильным ключом; draft-only, CRM/live интеграция pending. 14 local tests PASS. Research output и code ready не равны deployed/accepted.

**Агентства:** сохранён последний подтверждённый checkpoint345 provisional groups (203RU/59BY/83other), Saratov4 suitable,12 прежних CRM C10; этот блок не добавлял новые агентства. Ночная задача расширяется на developer backlog и проверку свежих LOCAL receipts. Массовых отправок нет.

Следующий LOCAL результат обязателен по прежней closeout схеме плюс [новое дополнение](tasks/MIRA-AUTONOMY-20260919-01.md). Передача этого обновления в Git не означает новый ACK или завершение облачного переноса.


## 2026-09-18T18:39:09Z — LOCAL-MAIL-20260919-01

LOCAL checkpoint supersedes previous CRM12/mail-not-connected facts **only for the private lab**. Результат: [MKT receipt](receipts/MIRA-MKT-20260918-01.json), [T01–T14 и manifest](receipts/MIRA-CLOSEOUT-20260918-01.json).

Private source54d80452d36080ded3d141fbac56a2c22506f16c; WEGC checkpointd472b7462de1a3f50eb571ca756580c1fe3ba2fa. Native167Accounts=78agency+87developer+2synthetic;20inactive templates. MailSMTP/IMAP/Tasks/Notifications/reply documents/approval/stop and native scheduling accepted locally;47Python,36PHP,9nativegroups,ACL/browser and encrypted isolated restorePASS. Zero external messages. Current owner chooses own server and requested VPS preparation; no purchase or DNS modification. Brevo requirement superseded by this owner instruction; public delivery/DSN/FBL stillNOT_RUN.

Per-item: T01partial newflow/model; T02localemailPASS/livechannels pending; T03localownmailPASS/publicVPS pending; T04localcap/stopPASS/externalfeedback pending; T05localACL/restorePASS/hostedoffsite pending; T06privatecount78+2holds/fullcanonical reconciliation pending; T07CLOUD existingnighttask unchanged; T08externalmedia/contracts holds; T09fieldchecksNOT_RUN; T10branches disposition recorded, oldpreflight retained; T11private manifest returned; T12checkpoint report returned; T13backlog; T14migration prepared, not performed. **all_done=false**. Original historical entries and CLOUD night checkpoint remain in place.
