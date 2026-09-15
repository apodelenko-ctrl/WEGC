# МИРА — стандарты данных пилота

Дата: 2026-09-15 UTC.

## Агентства

CSV/JSON-поля: company_name, country, city, region, website, email, phone, telegram, whatsapp, vk, instagram, youtube, director_or_owner, director_contact, team_size_estimate, segments, new_builds_yes_no, foreign_property_yes_no, foreign_markets, premium_signal, activity_signal, lead_score_0_100, rating, why_relevant, source_urls, last_verified, verification_notes.

Правила: одна организация — одна строка; филиалы объединяются, если решение централизовано; неизвестное значение — unknown; официальный сайт и дата проверки обязательны; рекламная формулировка не считается подтверждением без источника.

## Застройщики

Поля: developer_brand, legal_name, country, region, website, projects, districts, sales_email, sales_phone, partner_contact, agency_program, published_agent_commission, commission_source, lead_registration, payment_plans, broker_portal, direct_agreement_status, existing_wegc_relation, priority, source_urls, last_verified, verification_notes.

Тип источника обязательно классифицировать: official_developer, official_partner_page, official_registry, verified_secondary, discovery_only.

## Контроль качества

Перед outreach: дедупликация по домену/телефону/юрлицу; проверка мёртвых сайтов; выборочная повторная проверка минимум 10–20%; разделение confirmed/probable/unverified; удаление строк без источника.
