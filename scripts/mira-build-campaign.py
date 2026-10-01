#!/usr/bin/env python3
"""Publish campaign layouts without colliding with a concurrently released route.

The original layout module is preserved byte-for-byte. This explicit route
configuration reserves /business/ for the earlier independent implementation.
"""
from pathlib import Path
import importlib.util
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('mira_campaign_layouts', Path(__file__).with_name('mira-campaign-layouts.py'))
layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout)
if set(layout.VARIANTS) != {'go', 'business', 'corporate'}:
    raise ValueError('Unexpected layout registry; reconcile routes before publication')
VARIANTS = {'go': layout.VARIANTS['go'], 'practical': layout.VARIANTS['business'], 'corporate': layout.VARIANTS['corporate']}
layout.VARIANTS = VARIANTS
build_page = layout.build_page

def apply_go_offer(text):
    """Refresh only the Go offer; keep the existing layout and motion hooks."""
    if 'id="income"' in text:
        return text
    replacements = [
        ('<div class="project-picture"><img src="/images/the-modeva-exterior-4-1.webp" alt="Архивная визуализация The Modeva" loading="lazy" width="900" height="560"><span>Архивная визуализация · The Modeva</span></div>',
         '<div class="project-picture"><a href="/mira/catalog/botanica/" aria-label="Посмотреть Botanica MontAzure"><img src="/images/projects/botanica/montazure-1.jpg" alt="Botanica MontAzure — визуализация виллы Type 4C с бассейном в Камале" loading="lazy" width="1600" height="1060"></a><span>Botanica MontAzure · визуализация застройщика</span></div>'),
        ('Не отдавайте зарубежный запрос другому брокеру. Добавьте Пхукет в предложение своего агентства — клиент и ваш бренд остаются с вами.',
         'Откройте зарубежное направление в вашем агентстве. Проекты, работа с застройщиками, документы и помощь с оплатой — с поддержкой МИРА. Ваш клиент и ваш бренд остаются с вами.'),
        ('>Проекты Пхукета</a>', '>Маркетплейс</a>'),
        ('<div class="destination">ПХУКЕТ <span>↗</span></div>', '<div class="destination">МИР ОТКРЫТ <span>↗</span></div>'),
        ('<a class="button" href="/mira/catalog/">Посмотреть проекты ↗</a><a class="text-link" href="https://pilot.wegc.fund/mira/request/">Подать заявку →</a>',
         '<a class="button" href="#start">Начать работу с МИРА ↗</a><a class="text-link" href="/mira/catalog/">Объекты в маркетплейсе →</a>'),
        ('<p class="hero-fine">Выберите проекты. Сохраните подборку. Обсудите следующий шаг.</p>',
         ''),
        ('Клиент спросил о Пхукете.<br>У вас есть следующий шаг.', 'От первого запроса<br>до зарубежной сделки.'),
        ('Изучите каталог Пхукета, отберите подходящие направления и сформируйте предварительную подборку.',
         'Посмотрите проекты по разным направлениям. Мы поможем уточнить наличие, цены и условия застройщика под запрос вашего клиента.'),
        ('<h3>Подготовьте подключение</h3><p>Определите задачу команды. Согласуйте договор, проект, правила регистрации и комиссию до рабочего запроса.</p>',
         '<h3>Подключите агентство</h3><p>Оставьте рабочие контакты. Обсудим задачу вашей команды, порядок работы, регистрацию клиента и условия вознаграждения.</p>'),
        ('<h2>Начните с места.<br>Не с нового офиса.</h2>', '<h2>Начните<br>с Пхукета.</h2>'),
        ('Виллы и кондоминиумы, районы и группы девелоперов — в одном каталоге. Выбирайте проекты и собирайте свою подборку.',
         'Познакомьтесь с виллами и кондоминиумами Пхукета, выберите подходящие объекты и обсудите первый клиентский запрос с нашей командой.'),
        ('<a class="button" href="/mira/catalog/">Найти проект ↗</a>', '<a class="button" href="https://pilot.wegc.fund/mira/request/">Подключить Пхукет ↗</a>'),
        ('<summary>Платёжное сопровождение</summary><p>Отдельный запрос и проверка конкретной сделки. Средства покупателя и агентское вознаграждение не смешиваются.</p>',
         '<summary>Документы и оплата</summary><p>Поможем согласовать прямой договор покупателя с застройщиком, организовать подписание и получение оригиналов. По запросу — сопровождение оплаты и консультация местного юриста.</p>'),
    ]
    for before, after in replacements:
        if before not in text:
            raise ValueError(f'Go offer source changed: {before[:70]}')
        text = text.replace(before, after)
    opening = '<section class="impact"><div class="wrap"><h2>Клиент остаётся вашим.<br><span>География — меняется.</span></h2><a href="#how" class="round-arrow" aria-label="Как это работает">↓</a></div></section>'
    income = '''<section class="impact go-income" id="income" aria-labelledby="income-title"><div class="wrap"><div class="go-income-copy"><p class="go-income-label">ВАШ КЛИЕНТ. ВАШ БРЕНД. ВАШ ДОХОД.</p><h2 id="income-title">Комиссия застройщика&nbsp;—<br>ваш доход.</h2><p class="go-income-note">Размер комиссии зависит от проекта. Условия вознаграждения и выплаты согласуем до сделки.</p></div><div class="go-income-number"><strong class="go-income-value" role="img" aria-label="От 5 до 12 процентов"><span class="go-stencil" aria-hidden="true">5</span><span class="go-rate-divider" aria-hidden="true"></span><span class="go-stencil" aria-hidden="true">12</span><span class="go-stencil go-percent" aria-hidden="true">%</span></strong><span class="go-income-caption">комиссия от стоимости объекта</span></div></div></section>'''
    if opening not in text:
        raise ValueError('Missing Go impact section')
    text = text.replace(opening, income)
    payment = '''<section class="mira-payment wrap" id="payments" aria-labelledby="mira-payment-title"><div><p class="mira-payment-label">Сопровождение сделки</p><h2 id="mira-payment-title">Поможем организовать оплату зарубежной недвижимости</h2><p>От выбранного объекта до договора и расчётов с застройщиком — с поддержкой МИРА. Поможем с документами, подписанием и получением оригиналов. По запросу подключим местного юриста.</p><div class="mira-payment-actions"><a class="mira-payment-apply" href="https://pilot.wegc.fund/mira/request/">Обсудить оплату ↗</a><a href="/mira/payments/">Как работает сопровождение ↗</a></div></div><ol><li><h3>Обсудим задачу</h3><p>Страна, объект, сумма, валюты и предполагаемые сроки.</p></li><li><h3>Проверим возможность</h3><p>Необходимые документы и доступные варианты расчётов.</p></li><li><h3>Согласуем условия</h3><p>Порядок оплаты, комиссии, курс и сроки — до проведения платежа.</p></li></ol></section>'''
    text = text.replace('<section class="project-strip wrap">', payment + '<section class="project-strip wrap" id="phuket">', 1)
    text = text.replace('</head>', '<link rel="stylesheet" href="/mira/campaign/go-offer.css?v=20261001b"></head>', 1)
    return text

def build(root=ROOT):
    result = layout.build(root)
    hub = Path(root) / 'mira/launch/index.html'
    content = hub.read_text(encoding='utf-8')
    content = content.replace('href="#how"', 'href="/mira/go/#how"')
    content = content.replace('href="#start"', 'href="/mira/go/#start"')
    hub.write_text(content, encoding='utf-8')
    for route in [*VARIANTS, 'launch']:
        target = Path(root) / 'mira' / route / 'index.html'
        text = target.read_text(encoding='utf-8')
        marker = '<link rel="stylesheet" href="/mira/campaign/campaign.css">'
        if text.count(marker) != 1:
            raise ValueError('Unexpected campaign stylesheet boundary')
        text = text.replace(marker, marker + '<link rel="stylesheet" href="/mira/campaign/accessibility.css">')
        if route == 'go':
            text = apply_go_offer(text)
        target.write_text(text, encoding='utf-8')
    return result

if __name__ == '__main__':
    build()
