# МИРА: Cloudflare — целевой путь запуска

Уточнение владельца21сентября: планировался Cloudflare без выделенного сервера. Это исправляет ошибочную универсальную зависимость EXPO-06 от Linux/Docker host в checkpoint54424137.

В main уже есть cloudflare-worker/mira/worker.mjs, D1 migrations, Access-проверка и защищённый кабинет. Это подтверждение существующего кода, не текущая инвентаризация аккаунта или полная live-приёмка.

Целевой путь: продолжить существующие Worker + D1; защищённые материалы через предусмотренный private R2 при необходимости. Cloudflare управляет runtime; VPS/SSH не обязательны для этого приложения. Не смешивать с WET WhatsApp/hkWET.

Локальный EspoCRM/MariaDB/mail kit — другой слой. Его Docker volumes и SQL нельзя просто загрузить в Worker/D1 и считать CRM перенесённой. Проверенные5 файлов сохраняются как исходный архив/rollback. Для Cloudflare нужна миграция нужных сущностей, истории и операций с сохранением native external IDs, связей, статусов и доказательств. Worker API сейчас не равен всем функциям EspoCRM. Нельзя выбросить данные, объявить167Accounts импортированными или отключить Mac до сверки и приёмки. Точный перенос остальных CRM/mail функций следует оформить по inventory; не переписывать вслепую и не менять почтовое решение без согласования.

EXPO-06 теперь: подтвердить фактические MIRA Worker/D1/Access ресурсы через авторизованный Cloudflare доступ; проверить живую конфигурацию и текущие данные; подготовить изолированную схему/миграцию, replay-safe mapping и сравнение счётчиков; интегрировать необходимые операции и принять durable request/response/restart поведение. Не изменять существующую production D1 вслепую. Полный перенос EspoCRM в Linux остаётся альтернативой для сохранения той установки без переделки, не launch gate и не заказ на сервер.

Нынешние отсутствующие inputs: авторизованный Cloudflare account/resource inventory и доступ к отдельному recovery key либо авторизованный переносимый экспорт LOCAL для зашифрованной native базы. Ключ не нужен для продолжения открытого кода и public research. Контакты/договоры/ключи и private exports не публиковать в Git. Миграция данных — отдельная проверяемая работа, не выполнена этим решением.

Следующий конкретный блок: read-only inventory имеющихся MIRA Cloudflare ресурсов; карта текущей D1 ↔ nativeCRM сущностей/операций; разбор открытой схемы и подготовка аддитивного migration/import пакета без ожидания VPS. Затем actual import/live acceptance при доступе. Дедлайн выставки и EXPO-03 входящий путь сохраняются.

Источники: [MIRA API repository](https://github.com/apodelenko-ctrl/WEGC/blob/main/cloudflare-worker/mira/README.md), [Wrangler template](https://github.com/apodelenko-ctrl/WEGC/blob/main/cloudflare-worker/mira/wrangler.example.toml), [D1](https://developers.cloudflare.com/d1/), [Workers](https://developers.cloudflare.com/workers/).
