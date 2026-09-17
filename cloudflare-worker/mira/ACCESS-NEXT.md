# Следующий шаг: Access и целевая сеть

17.09.2026. Инструкция владельцу/авторизованному локальному агенту, не отчёт о работающей регистрации.

## Продолжаем, не повторяем

PR8 интегрирован; отдельная D1 и все три миграции подготовлены по локальной передаче. Zero Trust Free существует. API403 не доказывает отсутствия плана. Не покупать тариф заново, не создавать ещё одну БД, не трогать соседние проекты.

Main новее e4a5bf34: добавлен site-worker.mjs для pilot.wegc.fund. Сначала сравнить локальную ветку и origin/main; сохранить новые локальные правки. Не заменять игнорируемый wrangler.toml пустым примером. До создания custom domain проверить реальную занятость имени в зоне. Публичный apex не переводить на proxy.

## Заполнение Destinations

Одно self-hosted приложение, например MIRA Pilot. Три публичных назначения:

| Subdomain | Domain | Path |
|---|---|---|
| pilot | wegc.fund | /mira/pilot.html |
| pilot | wegc.fund | /mira/library.html |
| pilot | wegc.fund | /mira/api/* |

Путь без повторения домена; если начальная косая черта уже показана интерфейсом, не дублировать. Итоговые назначения должны точно совпадать с указанными HTTPS URL. Не защищать целиком wegc.fund, /mira/* или все Workers аккаунта. Публичная /mira/documents/privacy.html на pilot-хосте доступна до входа. JWT-проверка защищённого HTML/API остаётся обязательной независимо от настройки dashboard.

В Login methods включить One-time PIN. Для первой технической приёмки — Allow / Emails только с адресом владельца, заданным локально. Не Everyone/Bypass. Первое агентство добавить отдельно после согласования. Такой пилот по списку не называть открытой саморегистрацией.

Сохранить приложение. Получить **Application Audience (AUD) Tag**, не Policy ID. Проверить точный team domain в действующем Zero Trust. Не подставлять AUD по аналогии с другой системой. Cookie/JWT, коды, пароли и API tokens не пересылать и не коммитить.

## Конфигурация и развёртывание

Локальный агент использует wrangler.site.example.toml как схему, сохраняя уже проверенные account_id и D1. APP_ORIGIN=https://pilot.wegc.fund; entrypoint=site-worker.mjs; custom domain только pilot.wegc.fund. previews/workers.dev выключены; assets только из pilot-assets. APPLICATIONS_ENABLED=false и MATERIALS_ENABLED=false.

В текущем исправлении восемь allowlisted файлов, включая privacy HTML/CSS. Текст и статус проекта политики сохранены: это устранение 404, не утверждение политики. После согласования её версия и точный same-origin URL фиксируются отдельно.

```sh
python3 scripts/mira-build-pilot-assets.py
python3 scripts/mira-server-preflight.py --config cloudflare-worker/mira/wrangler.toml \
  --expected-account-id "$ACCOUNT_ID" --expected-database-id "$MIRA_DB_ID" \
  --expected-origin https://pilot.wegc.fund --topology dedicated-site
```

ACCOUNT_ID/MIRA_DB_ID берутся из существующей проверенной локальной настройки. После тестов/dry-run авторизованный локальный агент развёртывает только MIRA. Этот облачный прогон не имеет местной авторизации, не делал deploy/миграций.

## Сетевая проверка

Из целевой российской сети без VPN открыть лендинг, каталог и полное изображение, затем кабинет и экран входа. Поддомен не устраняет сетевую зависимость от Cloudflare.

```sh
python3 scripts/mira-access-check.py --access-origin "$ACCESS_TEAM_DOMAIN" \
  --network-label RU-home --vpn off --out /tmp/mira-ru-home-off.json
```

Скрипт выполняет ограниченные анонимные GET: сверяет полные байты публичных ресурсов с локальной копией, проверяет ожидаемые login-редиректы и сертификаты Access. Не следует редиректам, не принимает cookie/Authorization, не отправляет коды/заявки и не пишет в БД. Отчёт вне публичного репозитория. География и VPN только заявлены оператором, не измерены скриптом. Несовпадение байтов может означать другой релиз/CDN, а не блокировку.

Отдельно браузером: действительная доставка кода, вход, выход, новая сессия; затем на согласованной конфигурации заявка/квитанция/операторское решение/изоляция/отзыв. Первого оператора назначать только по криптографически проверенному subject и подтверждённому владельцу, не по email-заголовку или форме.

## Операторский процесс

В текущем UI есть очередь/переходы заявки, но одна кнопка статуса не создаёт агентство, подтверждение подписанного договора и membership. До реального onboarding нужны защищённые административные операции с проверенными основаниями. Не создавать выдуманный EVID или договор ради прохождения теста. Регистрация покупателя/коммерческий допуск отдельно от аккаунта агентства.

## При подтверждённой недоступности

Фиксировать публичный wegc.fund, pilot-хост и Access-domain отдельно. Не менять HTTPS на HTTP и не снимать проверки подписи/прав. Альтернатива требует независимых от Cloudflare публичной доставки, auth и API; перенос только лендинга не убирает зависимость браузера от Access. До выбора инфраструктуры проверить тестовый HTTPS endpoint из целевой сети и требования места обработки данных. Миграция в отдельную БД с проверяемым экспортом/восстановлением и сохранением изоляции/отзыва. Платные услуги и изменение рабочего домена согласуются отдельно.

## Первичные ссылки, проверены 17.09.2026

- https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/
- https://developers.cloudflare.com/workers/configuration/routing/custom-domains/
- https://developers.cloudflare.com/workers/configuration/cloudflare-access/
- https://developers.cloudflare.com/support/troubleshooting/general-troubleshooting/service-disruption/
