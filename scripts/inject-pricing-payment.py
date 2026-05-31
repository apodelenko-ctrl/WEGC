#!/usr/bin/env python3
"""Inject pricing, layout tabs and payment plan sections into project passports."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "projects"

FP_JS = """
/* Floor-plan tabs */
(function(){
  var tabs=document.querySelectorAll('.fp-tab');
  if(!tabs.length)return;
  tabs.forEach(function(t){
    t.addEventListener('click',function(){
      var id=t.getAttribute('data-fp');
      document.querySelectorAll('.fp-tab').forEach(function(x){x.classList.remove('active');x.setAttribute('aria-selected','false');});
      document.querySelectorAll('.fp-panel').forEach(function(x){x.classList.remove('active');});
      t.classList.add('active');t.setAttribute('aria-selected','true');
      var panel=document.getElementById(id);
      if(panel)panel.classList.add('active');
    });
  });
})();"""

def layout_panel(panel_id, active, title, price, rows, lang):
    act = ' active' if active else ''
    sel = 'true' if active else 'false'
    rows_html = ''.join(f'<div class="row"><span class="k">{k}</span><span class="val">{v}</span></div>' for k, v in rows)
    req = 'Floor plan on request' if lang == 'en' else 'Планировка по запросу'
    return f'''    <div class="fp-panel fp-spec-only{act}" id="{panel_id}" role="tabpanel">
      <div class="fp-info">
        <h3>{title}</h3>
        <div class="fp-price">{price}</div>
        <div class="fp-specs">
{rows_html}
          <div class="row"><span class="k">{"Floor plan" if lang=="en" else "Планировка"}</span><span class="val">{req}</span></div>
        </div>
      </div>
    </div>'''

def build_pricing_section(lang, meta):
    m = meta[lang]
    tabs = m['tabs']
    tab_btns = []
    panels = []
    for i, tab in enumerate(tabs):
        tab_id, label = tab['id'], tab['label']
        act_cls = ' active' if i == 0 else ''
        sel = 'true' if i == 0 else 'false'
        tab_btns.append(f'      <button class="fp-tab{act_cls}" data-fp="{tab_id}" role="tab" aria-selected="{sel}">{label}</button>')
        panels.append(layout_panel(tab_id, i == 0, tab['title'], tab['price'], tab['rows'], lang))

    return f'''<section class="s" id="pricing">
  <div class="container">
    <div class="s-head">
      <span class="kicker">{m['pricing_kicker']}</span>
      <h2>{m['pricing_h2']}</h2>
      <p>{m['pricing_p']}</p>
    </div>
    <div class="price-grid">
      <div class="price-card">
        <div class="l">{m['from_l']}</div>
        <div class="v">{m['from_v']}</div>
        <div class="sub">{m['from_sub']}</div>
      </div>
      <div class="price-card featured">
        <div class="l">{m['to_l']}</div>
        <div class="v">{m['to_v']}</div>
        <div class="sub">{m['to_sub']}</div>
      </div>
    </div>
    <div class="fp-tabs" role="tablist" aria-label="{m['tabs_aria']}">
{chr(10).join(tab_btns)}
    </div>
{chr(10).join(panels)}
  </div>
</section>'''

def build_payment_section(lang, meta):
    m = meta[lang]
    steps = []
    for i, step in enumerate(m['pay_steps'], 1):
        fin = ' final' if i == len(m['pay_steps']) else ''
        small = f'<small>{step["sub"]}</small>' if step.get('sub') else ''
        steps.append(f'      <div class="pay-step{fin}"><div class="n">{i}</div><div class="lbl">{step["lbl"]}{small}</div><div class="pct">{step["pct"]}</div></div>')
    cream = '' if m.get('pay_plain') else ' cream'
    return f'''<section class="s{cream}" id="payment">
  <div class="container">
    <div class="s-head">
      <span class="kicker">{m['pay_kicker']}</span>
      <h2>{m['pay_h2']}</h2>
      <p>{m['pay_p']}</p>
    </div>
    <div class="pay-timeline">
{chr(10).join(steps)}
    </div>
    <p class="pay-note">{m['pay_note']}</p>
  </div>
</section>'''

def pay_std(lang, completion):
    if lang == 'en':
        return [
            {'lbl': 'Reservation deposit', 'sub': 'On reservation — credited against the purchase price', 'pct': '100,000 THB'},
            {'lbl': 'Contract signing', 'sub': 'On execution of the sale & purchase agreement', 'pct': '25%'},
            {'lbl': '2nd instalment', 'sub': 'During construction', 'pct': '25%'},
            {'lbl': '3rd instalment', 'sub': 'During construction', 'pct': '25%'},
            {'lbl': 'Transfer of ownership', 'sub': f'Keys handover · completion {completion}', 'pct': '25%'},
        ]
    return [
        {'lbl': 'Депозит бронирования', 'sub': 'При бронировании — зачитывается в стоимость', 'pct': '100 000 THB'},
        {'lbl': 'Подписание договора', 'sub': 'При заключении договора купли-продажи', 'pct': '25%'},
        {'lbl': '2-й платёж', 'sub': 'В период строительства', 'pct': '25%'},
        {'lbl': '3-й платёж', 'sub': 'В период строительства', 'pct': '25%'},
        {'lbl': 'Передача права собственности', 'sub': f'Выдача ключей · сдача {completion}', 'pct': '25%'},
    ]

def pay_biancana(lang):
    if lang == 'en':
        return [
            {'lbl': 'Reservation deposit', 'sub': 'On reservation', 'pct': '100,000 THB'},
            {'lbl': 'Contract signing', 'sub': 'Within 30 days of contract execution', 'pct': '25%'},
            {'lbl': 'Foundation completion', 'sub': 'Construction milestone', 'pct': '25%'},
            {'lbl': 'Framework completion', 'sub': 'Construction milestone', 'pct': '25%'},
            {'lbl': 'Key handover', 'sub': 'Transfer of ownership · Q1 2029', 'pct': '25%'},
        ]
    return [
        {'lbl': 'Депозит бронирования', 'sub': 'При бронировании', 'pct': '100 000 THB'},
        {'lbl': 'Подписание договора', 'sub': 'В течение 30 дней после заключения', 'pct': '25%'},
        {'lbl': 'Завершение фундамента', 'sub': 'Этап строительства', 'pct': '25%'},
        {'lbl': 'Завершение каркаса', 'sub': 'Этап строительства', 'pct': '25%'},
        {'lbl': 'Выдача ключей', 'sub': 'Передача права собственности · Q1 2029', 'pct': '25%'},
    ]

def pay_olive(lang):
    if lang == 'en':
        return [
            {'lbl': 'Reservation deposit', 'sub': 'On pre-sale reservation', 'pct': '100,000 THB'},
            {'lbl': 'Contract signing', 'sub': 'Within 30 days of contract execution', 'pct': '25%'},
            {'lbl': '2nd instalment', 'sub': '7 months after contract signing', 'pct': '25%'},
            {'lbl': '3rd instalment', 'sub': '7 months after 2nd payment', 'pct': '25%'},
            {'lbl': 'Transfer of ownership', 'sub': 'Completion & handover · Q1 2029', 'pct': '25%'},
        ]
    return [
        {'lbl': 'Депозит бронирования', 'sub': 'При предпродажном бронировании', 'pct': '100 000 THB'},
        {'lbl': 'Подписание договора', 'sub': 'В течение 30 дней после заключения', 'pct': '25%'},
        {'lbl': '2-й платёж', 'sub': 'Через 7 месяцев после подписания', 'pct': '25%'},
        {'lbl': '3-й платёж', 'sub': 'Через 7 месяцев после 2-го платежа', 'pct': '25%'},
        {'lbl': 'Передача права собственности', 'sub': 'Сдача и выдача ключей · Q1 2029', 'pct': '25%'},
    ]

def pay_katabello(lang):
    if lang == 'en':
        return [
            {'lbl': 'Reservation deposit', 'sub': 'On booking', 'pct': '100,000 THB'},
            {'lbl': 'Contract signing', 'sub': 'Within 30 days of the reservation agreement', 'pct': '25%'},
            {'lbl': '2nd instalment', 'sub': '3 months after contract signing', 'pct': '25%'},
            {'lbl': '3rd instalment', 'sub': '3 months after the 2nd payment', 'pct': '25%'},
            {'lbl': 'Transfer of ownership', 'sub': 'On completion · Q3 2027', 'pct': '25%'},
        ]
    return [
        {'lbl': 'Депозит бронирования', 'sub': 'При бронировании', 'pct': '100 000 THB'},
        {'lbl': 'Подписание договора', 'sub': 'В течение 30 дней после договора бронирования', 'pct': '25%'},
        {'lbl': '2-й платёж', 'sub': 'Через 3 месяца после подписания', 'pct': '25%'},
        {'lbl': '3-й платёж', 'sub': 'Через 3 месяца после 2-го платежа', 'pct': '25%'},
        {'lbl': 'Передача права собственности', 'sub': 'По завершении · Q3 2027', 'pct': '25%'},
    ]

NOTE_EN = 'Interest-free instalments during construction. Percentages are of the total unit price; the reservation deposit is credited against the first instalment. Schedule is indicative and confirmed in the reservation agreement and sale & purchase agreement; subject to developer terms, applicable taxes and fees. Not an offer.'
NOTE_RU = 'Беспроцентная рассрочка на период строительства. Проценты от полной стоимости; депозит бронирования зачитывается в первый платёж. График ориентировочный и подтверждается в договоре бронирования и договоре купли-продажи; с учётом условий застройщика, налогов и сборов. Не оферта.'

PROJECTS = {
    'vivana': {
        'files': {'en': 'the-title-vivana-en.html', 'ru': 'the-title-vivana.html'},
        'en': {
            'pricing_kicker': 'Pricing & floor plans', 'pricing_h2': 'Indicative pricing and apartment layouts.',
            'pricing_p': 'Seven layout types across four 8-storey buildings — studios to penthouses, 30–128 m². Pricing is indicative and subject to availability, unit selection and final developer confirmation — not an offer.',
            'from_l': 'Starting from', 'from_v': '3.62M THB', 'from_sub': 'approx. $111,000 · 1 Bedroom S (30 m²)',
            'to_l': 'Up to', 'to_v': '10.5M THB', 'to_sub': '2 Bedroom Penthouse · top configuration',
            'tabs_aria': 'Apartment types',
            'tabs': [
                {'id': 'fpV1s', 'label': '1BR S', 'title': '1 Bedroom S', 'price': 'From 3.62M THB',
                 'rows': [('Area', '30 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Type', 'Apartment')]},
                {'id': 'fpV1m', 'label': '1BR M', 'title': '1 Bedroom M', 'price': 'From 3.72M THB',
                 'rows': [('Area', '32–36 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Type', 'Apartment')]},
                {'id': 'fpV1l', 'label': '1BR L', 'title': '1 Bedroom L', 'price': 'From 4.77M THB',
                 'rows': [('Area', '40–44 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Type', 'Apartment')]},
                {'id': 'fpV1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'From 5.85M THB',
                 'rows': [('Area', '50–56 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Type', 'Apartment')]},
                {'id': 'fpV2m', 'label': '2BR', 'title': '2 Bedroom M', 'price': 'From 7.01M THB',
                 'rows': [('Area', '60–66 m²'), ('Bedrooms', '2'), ('Bathrooms', '2'), ('Type', 'Apartment')]},
                {'id': 'fpVph1', 'label': 'PH 01', 'title': '2 Bedroom Penthouse 01', 'price': 'From 10.45M THB',
                 'rows': [('Area', '89–100 m²'), ('Bedrooms', '2'), ('Bathrooms', '2'), ('Type', 'Penthouse')]},
                {'id': 'fpVph2', 'label': 'PH 02', 'title': '2 Bedroom Plus Penthouse 02', 'price': 'On request',
                 'rows': [('Area', '121–128 m²'), ('Bedrooms', '2'), ('Bathrooms', '2'), ('Type', 'Penthouse')]},
            ],
            'pay_kicker': 'Payment plan', 'pay_h2': 'Interest-free instalment schedule.',
            'pay_p': 'Four equal 25% instalments during construction, per The Title standard schedule for off-plan condominiums. Completion targeted Q4 2028.',
            'pay_steps': pay_std('en', 'Q4 2028'), 'pay_note': NOTE_EN,
        },
        'ru': {
            'pricing_kicker': 'Цены и планировки', 'pricing_h2': 'Ориентировочные цены и типы апартаментов.',
            'pricing_p': 'Семь типов планировок в четырёх 8-этажных корпусах — от компактных до пентхаусов, 30–128 м². Цены ориентировочные и зависят от наличия, выбора лота и финального подтверждения застройщика — не оферта.',
            'from_l': 'От', 'from_v': '3,62 млн THB', 'from_sub': '≈ $111 000 · 1 Bedroom S (30 м²)',
            'to_l': 'До', 'to_v': '10,5 млн THB', 'to_sub': '2 Bedroom Penthouse · топовая конфигурация',
            'tabs_aria': 'Типы апартаментов',
            'tabs': [
                {'id': 'fpV1s', 'label': '1BR S', 'title': '1 Bedroom S', 'price': 'От 3,62 млн THB',
                 'rows': [('Площадь', '30 м²'), ('Спальни', '1'), ('С/у', '1'), ('Тип', 'Апартамент')]},
                {'id': 'fpV1m', 'label': '1BR M', 'title': '1 Bedroom M', 'price': 'От 3,72 млн THB',
                 'rows': [('Площадь', '32–36 м²'), ('Спальни', '1'), ('С/у', '1'), ('Тип', 'Апартамент')]},
                {'id': 'fpV1l', 'label': '1BR L', 'title': '1 Bedroom L', 'price': 'От 4,77 млн THB',
                 'rows': [('Площадь', '40–44 м²'), ('Спальни', '1'), ('С/у', '1'), ('Тип', 'Апартамент')]},
                {'id': 'fpV1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'От 5,85 млн THB',
                 'rows': [('Площадь', '50–56 м²'), ('Спальни', '1'), ('С/у', '1'), ('Тип', 'Апартамент')]},
                {'id': 'fpV2m', 'label': '2BR', 'title': '2 Bedroom M', 'price': 'От 7,01 млн THB',
                 'rows': [('Площадь', '60–66 м²'), ('Спальни', '2'), ('С/у', '2'), ('Тип', 'Апартамент')]},
                {'id': 'fpVph1', 'label': 'PH 01', 'title': '2 Bedroom Penthouse 01', 'price': 'От 10,45 млн THB',
                 'rows': [('Площадь', '89–100 м²'), ('Спальни', '2'), ('С/у', '2'), ('Тип', 'Пентхаус')]},
                {'id': 'fpVph2', 'label': 'PH 02', 'title': '2 Bedroom Plus Penthouse 02', 'price': 'По запросу',
                 'rows': [('Площадь', '121–128 м²'), ('Спальни', '2'), ('С/у', '2'), ('Тип', 'Пентхаус')]},
            ],
            'pay_kicker': 'График платежей', 'pay_h2': 'Беспроцентная рассрочка.',
            'pay_p': 'Четыре равных платежа по 25% в период строительства — стандартный график The Title для кондоминиумов на этапе строительства. Сдача — Q4 2028.',
            'pay_steps': pay_std('ru', 'Q4 2028'), 'pay_note': NOTE_RU,
        },
    },
    'sierra': {
        'files': {'en': 'the-title-sierra-en.html', 'ru': 'the-title-sierra.html'},
        'en': {
            'pricing_kicker': 'Pricing & floor plans', 'pricing_h2': 'Indicative pricing and apartment layouts.',
            'pricing_p': 'Five layout types across three 8-storey buildings — compact studios to two-bedroom units, 28–62 m². Pricing is indicative and subject to availability — not an offer.',
            'from_l': 'Starting from', 'from_v': '3.05M THB', 'from_sub': 'approx. $94,000 · 1 Bedroom S (28 m²)',
            'to_l': 'Up to', 'to_v': '5.23M THB', 'to_sub': '1 Bedroom Plus · larger layout',
            'tabs_aria': 'Apartment types',
            'tabs': [
                {'id': 'fpS1bs', 'label': '1BR S', 'title': '1 Bedroom S (BS)', 'price': 'From 3.05M THB',
                 'rows': [('Area', '28 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Buildings', '3 × 8 floors')]},
                {'id': 'fpS1m', 'label': '1BR M', 'title': '1 Bedroom M', 'price': 'From 3.66M THB',
                 'rows': [('Area', '30 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Buildings', '3 × 8 floors')]},
                {'id': 'fpS1bp', 'label': '1BR Plus', 'title': '1 Bedroom Plus (BP)', 'price': 'From 5.23M THB',
                 'rows': [('Area', '44 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Buildings', '3 × 8 floors')]},
                {'id': 'fpS2s', 'label': '2BR S', 'title': '2 Bedroom S', 'price': 'From 5.05M THB',
                 'rows': [('Area', '55 m²'), ('Bedrooms', '2'), ('Bathrooms', '2'), ('Buildings', '3 × 8 floors')]},
                {'id': 'fpS2m', 'label': '2BR M', 'title': '2 Bedroom M', 'price': 'From 5.50M THB',
                 'rows': [('Area', '62 m²'), ('Bedrooms', '2'), ('Bathrooms', '2'), ('Buildings', '3 × 8 floors')]},
            ],
            'pay_kicker': 'Payment plan', 'pay_h2': 'Interest-free instalment schedule.',
            'pay_p': 'Four equal 25% instalments during construction. Completion targeted Q3 2028.',
            'pay_steps': pay_std('en', 'Q3 2028'), 'pay_note': NOTE_EN,
        },
        'ru': {
            'pricing_kicker': 'Цены и планировки', 'pricing_h2': 'Ориентировочные цены и типы апартаментов.',
            'pricing_p': 'Пять типов планировок в трёх 8-этажных корпусах — от компактных до двухспальных, 28–62 м². Цены ориентировочные — не оферта.',
            'from_l': 'От', 'from_v': '3,05 млн THB', 'from_sub': '≈ $94 000 · 1 Bedroom S (28 м²)',
            'to_l': 'До', 'to_v': '5,23 млн THB', 'to_sub': '1 Bedroom Plus · крупная планировка',
            'tabs_aria': 'Типы апартаментов',
            'tabs': [
                {'id': 'fpS1bs', 'label': '1BR S', 'title': '1 Bedroom S (BS)', 'price': 'От 3,05 млн THB',
                 'rows': [('Площадь', '28 м²'), ('Спальни', '1'), ('С/у', '1'), ('Корпуса', '3 × 8 этажей')]},
                {'id': 'fpS1m', 'label': '1BR M', 'title': '1 Bedroom M', 'price': 'От 3,66 млн THB',
                 'rows': [('Площадь', '30 м²'), ('Спальни', '1'), ('С/у', '1'), ('Корпуса', '3 × 8 этажей')]},
                {'id': 'fpS1bp', 'label': '1BR Plus', 'title': '1 Bedroom Plus (BP)', 'price': 'От 5,23 млн THB',
                 'rows': [('Площадь', '44 m²'), ('Спальни', '1'), ('С/у', '1'), ('Корпуса', '3 × 8 этажей')]},
                {'id': 'fpS2s', 'label': '2BR S', 'title': '2 Bedroom S', 'price': 'От 5,05 млн THB',
                 'rows': [('Площадь', '55 m²'), ('Спальни', '2'), ('С/у', '2'), ('Корпуса', '3 × 8 этажей')]},
                {'id': 'fpS2m', 'label': '2BR M', 'title': '2 Bedroom M', 'price': 'От 5,50 млн THB',
                 'rows': [('Площадь', '62 m²'), ('Спальни', '2'), ('С/у', '2'), ('Корпуса', '3 × 8 этажей')]},
            ],
            'pay_kicker': 'График платежей', 'pay_h2': 'Беспроцентная рассрочка.',
            'pay_p': 'Четыре равных платежа по 25% в период строительства. Сдача — Q3 2028.',
            'pay_steps': pay_std('ru', 'Q3 2028'), 'pay_note': NOTE_RU,
        },
    },
    'olive': {
        'files': {'en': 'the-olive-en.html', 'ru': 'the-olive.html'},
        'en': {
            'pricing_kicker': 'Pricing & floor plans', 'pricing_h2': 'Pre-sale pricing and apartment layouts.',
            'pricing_p': 'Three layout groups across two 8-storey Mediterranean-style buildings — 32–63 m². Pre-sale from 115,000 THB/m². Pricing is indicative — not an offer.',
            'from_l': 'Starting from', 'from_v': '3.7M THB', 'from_sub': '115,000 THB/m² · 1 Bedroom (32 m²)',
            'to_l': 'Price per m²', 'to_v': '115K THB', 'to_sub': 'Pre-sale · up to 10% discount available',
            'tabs_aria': 'Apartment types',
            'tabs': [
                {'id': 'fpO1', 'label': '1BR', 'title': '1 Bedroom', 'price': 'From ~3.7M THB (115K/m²)',
                 'rows': [('Area', '32–34 m²'), ('Bedrooms', '1'), ('Buildings', '2 × 8 floors'), ('Units', '291 total')]},
                {'id': 'fpO1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'From ~5.1M THB (115K/m²)',
                 'rows': [('Area', '44–52 m²'), ('Bedrooms', '1'), ('Buildings', '2 × 8 floors'), ('Pet-friendly', 'Building A')]},
                {'id': 'fpO2', 'label': '2BR', 'title': '2 Bedroom', 'price': 'From ~6.4M THB (115K/m²)',
                 'rows': [('Area', '56–63 m²'), ('Bedrooms', '2'), ('Buildings', '2 × 8 floors'), ('Beach', '450 m to Nai Yang')]},
            ],
            'pay_kicker': 'Payment plan', 'pay_h2': '0% interest-free pre-sale instalments.',
            'pay_p': 'Four equal 25% instalments on a fixed timeline during construction. Pre-sale launch 2026; completion targeted Q1 2029.',
            'pay_steps': pay_olive('en'), 'pay_note': NOTE_EN,
        },
        'ru': {
            'pricing_kicker': 'Цены и планировки', 'pricing_h2': 'Предпродажные цены и типы апартаментов.',
            'pricing_p': 'Три группы планировок в двух 8-этажных зданиях в средиземноморском стиле — 32–63 м². Предпродажа от 115 000 THB/м². Цены ориентировочные — не оферта.',
            'from_l': 'От', 'from_v': '3,7 млн THB', 'from_sub': '115 000 THB/м² · 1 Bedroom (32 м²)',
            'to_l': 'Цена за м²', 'to_v': '115K THB', 'to_sub': 'Предпродажа · скидка до 10%',
            'tabs_aria': 'Типы апартаментов',
            'tabs': [
                {'id': 'fpO1', 'label': '1BR', 'title': '1 Bedroom', 'price': 'От ~3,7 млн THB (115K/м²)',
                 'rows': [('Площадь', '32–34 m²'), ('Спальни', '1'), ('Корпуса', '2 × 8 этажей'), ('Юнитов', '291 всего')]},
                {'id': 'fpO1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'От ~5,1 млн THB (115K/м²)',
                 'rows': [('Площадь', '44–52 m²'), ('Спальни', '1'), ('Корпуса', '2 × 8 этажей'), ('Pet-friendly', 'Корпус A')]},
                {'id': 'fpO2', 'label': '2BR', 'title': '2 Bedroom', 'price': 'От ~6,4 млн THB (115K/м²)',
                 'rows': [('Площадь', '56–63 m²'), ('Спальни', '2'), ('Корпуса', '2 × 8 этажей'), ('Пляж', '450 м до Nai Yang')]},
            ],
            'pay_kicker': 'График платежей', 'pay_h2': 'Беспроцентная предпродажная рассрочка 0%.',
            'pay_p': 'Четыре равных платежа по 25% по фиксированному графику в период строительства. Старт предпродажи 2026; сдача — Q1 2029.',
            'pay_steps': pay_olive('ru'), 'pay_note': NOTE_RU,
        },
    },
    'balcony': {
        'files': {'en': 'the-title-balcony-en.html', 'ru': 'the-title-balcony.html'},
        'en': {
            'pricing_kicker': 'Pricing & floor plans', 'pricing_h2': 'Indicative pricing and apartment layouts.',
            'pricing_p': 'Beachfront condominium at Nai Yang — four 6-storey buildings, 100 m to the beach. Layouts from compact one-bedroom to three-bedroom penthouses. Pricing is indicative — not an offer.',
            'from_l': 'Starting from', 'from_v': '5.24M THB', 'from_sub': 'approx. $161,000 · 1 Bedroom M (35 m²)',
            'to_l': 'Up to', 'to_v': '25.9M THB', 'to_sub': '3 Bedroom Penthouse · 139 m²',
            'tabs_aria': 'Apartment types',
            'tabs': [
                {'id': 'fpB1m', 'label': '1BR M', 'title': '1 Bedroom M', 'price': 'From 5.24M THB',
                 'rows': [('Area', '33–36 m²'), ('Bedrooms', '1'), ('Beach', '~100 m'), ('Completion', 'Q1 2028')]},
                {'id': 'fpB1l', 'label': '1BR L', 'title': '1 Bedroom L', 'price': 'From 5.53M THB',
                 'rows': [('Area', '40–50 m²'), ('Bedrooms', '1'), ('Beach', '~100 m'), ('Completion', 'Q1 2028')]},
                {'id': 'fpB1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'From 7.01M THB',
                 'rows': [('Area', '45 m²'), ('Bedrooms', '1'), ('Beach', '~100 m'), ('Completion', 'Q1 2028')]},
                {'id': 'fpB2s', 'label': '2BR S', 'title': '2 Bedroom S', 'price': 'From 7.83M THB',
                 'rows': [('Area', '55 m²'), ('Bedrooms', '2'), ('Beach', '~100 m'), ('Completion', 'Q1 2028')]},
                {'id': 'fpB2m', 'label': '2BR M', 'title': '2 Bedroom M', 'price': 'From 10.24M THB',
                 'rows': [('Area', '62–77 m²'), ('Bedrooms', '2'), ('Beach', '~100 m'), ('Completion', 'Q1 2028')]},
                {'id': 'fpBph', 'label': 'PH', 'title': '3 Bedroom Penthouse', 'price': 'From 25.9M THB',
                 'rows': [('Area', '135–139 m²'), ('Bedrooms', '3'), ('Beach', '~100 m'), ('Completion', 'Q1 2028')]},
            ],
            'pay_kicker': 'Payment plan', 'pay_h2': 'Interest-free instalment schedule.',
            'pay_p': 'Four equal 25% instalments during construction. Completion targeted Q1 2028.',
            'pay_steps': pay_std('en', 'Q1 2028'), 'pay_note': NOTE_EN,
        },
        'ru': {
            'pricing_kicker': 'Цены и планировки', 'pricing_h2': 'Ориентировочные цены и типы апартаментов.',
            'pricing_p': 'Пляжный кондоминиум в Nai Yang — четыре 6-этажных корпуса, 100 м до пляжа. Планировки от компактных однушек до трёхспальных пентхаусов. Цены ориентировочные — не оферта.',
            'from_l': 'От', 'from_v': '5,24 млн THB', 'from_sub': '≈ $161 000 · 1 Bedroom M (35 m²)',
            'to_l': 'До', 'to_v': '25,9 млн THB', 'to_sub': '3 Bedroom Penthouse · 139 m²',
            'tabs_aria': 'Типы апартаментов',
            'tabs': [
                {'id': 'fpB1m', 'label': '1BR M', 'title': '1 Bedroom M', 'price': 'От 5,24 млн THB',
                 'rows': [('Площадь', '33–36 m²'), ('Спальни', '1'), ('Пляж', '~100 m'), ('Сдача', 'Q1 2028')]},
                {'id': 'fpB1l', 'label': '1BR L', 'title': '1 Bedroom L', 'price': 'От 5,53 млн THB',
                 'rows': [('Площадь', '40–50 m²'), ('Спальни', '1'), ('Пляж', '~100 m'), ('Сдача', 'Q1 2028')]},
                {'id': 'fpB1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'От 7,01 млн THB',
                 'rows': [('Площадь', '45 m²'), ('Спальни', '1'), ('Пляж', '~100 m'), ('Сдача', 'Q1 2028')]},
                {'id': 'fpB2s', 'label': '2BR S', 'title': '2 Bedroom S', 'price': 'От 7,83 млн THB',
                 'rows': [('Площадь', '55 m²'), ('Спальни', '2'), ('Пляж', '~100 m'), ('Сдача', 'Q1 2028')]},
                {'id': 'fpB2m', 'label': '2BR M', 'title': '2 Bedroom M', 'price': 'От 10,24 млн THB',
                 'rows': [('Площадь', '62–77 m²'), ('Спальни', '2'), ('Пляж', '~100 m'), ('Сдача', 'Q1 2028')]},
                {'id': 'fpBph', 'label': 'PH', 'title': '3 Bedroom Penthouse', 'price': 'От 25,9 млн THB',
                 'rows': [('Площадь', '135–139 m²'), ('Спальни', '3'), ('Пляж', '~100 m'), ('Сдача', 'Q1 2028')]},
            ],
            'pay_kicker': 'График платежей', 'pay_h2': 'Беспроцентная рассрочка.',
            'pay_p': 'Четыре равных платежа по 25% в период строительства. Сдача — Q1 2028.',
            'pay_steps': pay_std('ru', 'Q1 2028'), 'pay_note': NOTE_RU,
        },
    },
    'biancana': {
        'files': {'en': 'the-title-biancana-en.html', 'ru': 'the-title-biancana.html'},
        'en': {
            'pricing_kicker': 'Pricing & floor plans', 'pricing_h2': 'Indicative pricing and apartment layouts.',
            'pricing_p': 'Seven layout types across four 5-storey buildings near Surin Beach — 31–131 m². Construction-linked instalments. Pricing is indicative — not an offer.',
            'from_l': 'Starting from', 'from_v': '6.30M THB', 'from_sub': 'approx. $193,000 · 1 Bedroom M (31 m²)',
            'to_l': 'Up to', 'to_v': '19.1M THB', 'to_sub': '2 Bedroom Plus M · premium layout',
            'tabs_aria': 'Apartment types',
            'tabs': [
                {'id': 'fpBi1m', 'label': '1BR M', 'title': '1 Bedroom M', 'price': 'From 6.30M THB',
                 'rows': [('Area', '31 m²'), ('Bedrooms', '1'), ('Beach', '≈ 200 m to Surin'), ('Completion', 'Q1 2029')]},
                {'id': 'fpBi1l', 'label': '1BR L', 'title': '1 Bedroom L', 'price': 'From 7.03M THB',
                 'rows': [('Area', '39 m²'), ('Bedrooms', '1'), ('Beach', '≈ 200 m to Surin'), ('Completion', 'Q1 2029')]},
                {'id': 'fpBi1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'From 11.5M THB',
                 'rows': [('Area', '49–62 m²'), ('Bedrooms', '1'), ('Beach', '≈ 200 m to Surin'), ('Completion', 'Q1 2029')]},
                {'id': 'fpBi2m', 'label': '2BR M', 'title': '2 Bedroom M', 'price': 'From 12.1M THB',
                 'rows': [('Area', '62–73 m²'), ('Bedrooms', '2'), ('Beach', '≈ 200 m to Surin'), ('Completion', 'Q1 2029')]},
                {'id': 'fpBi2l', 'label': '2BR L', 'title': '2 Bedroom L', 'price': 'From 13.7M THB',
                 'rows': [('Area', '76 m²'), ('Bedrooms', '2'), ('Beach', '≈ 200 m to Surin'), ('Completion', 'Q1 2029')]},
                {'id': 'fpBi2pm', 'label': '2BR Plus', 'title': '2 Bedroom Plus M', 'price': 'From 19.1M THB',
                 'rows': [('Area', '90–100 m²'), ('Bedrooms', '2'), ('Beach', '≈ 200 m to Surin'), ('Completion', 'Q1 2029')]},
                {'id': 'fpBi3ph', 'label': '3BR PH', 'title': '3 Bedroom Penthouse', 'price': 'On request',
                 'rows': [('Area', '131 m²'), ('Bedrooms', '3'), ('Beach', '≈ 200 m to Surin'), ('Completion', 'Q1 2029')]},
            ],
            'pay_kicker': 'Payment plan', 'pay_h2': 'Construction-linked instalment schedule.',
            'pay_p': 'Payments tied to construction milestones — foundation, framework and handover. Completion targeted Q1 2029.',
            'pay_steps': pay_biancana('en'), 'pay_note': NOTE_EN,
        },
        'ru': {
            'pricing_kicker': 'Цены и планировки', 'pricing_h2': 'Ориентировочные цены и типы апартаментов.',
            'pricing_p': 'Семь типов планировок в четырёх 5-этажных корпусах у пляжа Surin — 31–131 m². Рассрочка, привязанная к этапам строительства. Цены ориентировочные — не оферта.',
            'from_l': 'От', 'from_v': '6,30 млн THB', 'from_sub': '≈ $193 000 · 1 Bedroom M (31 m²)',
            'to_l': 'До', 'to_v': '19,1 млн THB', 'to_sub': '2 Bedroom Plus M · премиальная планировка',
            'tabs_aria': 'Типы апартаментов',
            'tabs': [
                {'id': 'fpBi1m', 'label': '1BR M', 'title': '1 Bedroom M', 'price': 'От 6,30 млн THB',
                 'rows': [('Площадь', '31 m²'), ('Спальни', '1'), ('Пляж', '≈ 200 m до Surin'), ('Сдача', 'Q1 2029')]},
                {'id': 'fpBi1l', 'label': '1BR L', 'title': '1 Bedroom L', 'price': 'От 7,03 млн THB',
                 'rows': [('Площадь', '39 m²'), ('Спальни', '1'), ('Пляж', '≈ 200 m до Surin'), ('Сдача', 'Q1 2029')]},
                {'id': 'fpBi1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'От 11,5 млн THB',
                 'rows': [('Площадь', '49–62 m²'), ('Спальни', '1'), ('Пляж', '≈ 200 m до Surin'), ('Сдача', 'Q1 2029')]},
                {'id': 'fpBi2m', 'label': '2BR M', 'title': '2 Bedroom M', 'price': 'От 12,1 млн THB',
                 'rows': [('Площадь', '62–73 m²'), ('Спальни', '2'), ('Пляж', '≈ 200 m до Surin'), ('Сдача', 'Q1 2029')]},
                {'id': 'fpBi2l', 'label': '2BR L', 'title': '2 Bedroom L', 'price': 'От 13,7 млн THB',
                 'rows': [('Площадь', '76 m²'), ('Спальни', '2'), ('Пляж', '≈ 200 m до Surin'), ('Сдача', 'Q1 2029')]},
                {'id': 'fpBi2pm', 'label': '2BR Plus', 'title': '2 Bedroom Plus M', 'price': 'От 19,1 млн THB',
                 'rows': [('Площадь', '90–100 m²'), ('Спальни', '2'), ('Пляж', '≈ 200 m до Surin'), ('Сдача', 'Q1 2029')]},
                {'id': 'fpBi3ph', 'label': '3BR PH', 'title': '3 Bedroom Penthouse', 'price': 'По запросу',
                 'rows': [('Площадь', '131 m²'), ('Спальни', '3'), ('Пляж', '≈ 200 m до Surin'), ('Сдача', 'Q1 2029')]},
            ],
            'pay_kicker': 'График платежей', 'pay_h2': 'Рассрочка, привязанная к этапам строительства.',
            'pay_p': 'Платежи привязаны к этапам — фундамент, каркас и выдача ключей. Сдача — Q1 2029.',
            'pay_steps': pay_biancana('ru'), 'pay_note': NOTE_RU,
        },
    },
    'modeva': {
        'files': {'en': 'the-modeva-en.html', 'ru': 'the-modeva.html'},
        'en': {
            'pricing_kicker': 'Pricing & floor plans', 'pricing_h2': 'Indicative pricing and apartment layouts.',
            'pricing_p': 'Lifestyle condominium in Bang Tao — seven 7-storey buildings, 859 units, ~200–500 m to the beach. Layouts from compact one-bedroom to three-bedroom. Pricing is indicative — not an offer.',
            'from_l': 'Starting from', 'from_v': '4.78M THB', 'from_sub': 'approx. $147,000 · 1 Bedroom S (29 m²)',
            'to_l': 'Layouts', 'to_v': '1–3 bed', 'to_sub': '29–148 m² · 859 units · 5% discount on full payment',
            'tabs_aria': 'Apartment types',
            'tabs': [
                {'id': 'fpM1s', 'label': '1BR S', 'title': '1 Bedroom S', 'price': 'From 4.78M THB',
                 'rows': [('Area', '29 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q1 2027')]},
                {'id': 'fpM1m', 'label': '1BR M', 'title': '1 Bedroom M', 'price': 'From 5.34M THB',
                 'rows': [('Area', '33 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q1 2027')]},
                {'id': 'fpM1l', 'label': '1BR L', 'title': '1 Bedroom L', 'price': 'From 6.48M THB',
                 'rows': [('Area', '37–41 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q1 2027')]},
                {'id': 'fpM1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'On request',
                 'rows': [('Area', '55–58 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q1 2027')]},
                {'id': 'fpM2', 'label': '2BR', 'title': '2 Bedroom', 'price': 'On request',
                 'rows': [('Area', '65–118 m²'), ('Bedrooms', '2'), ('Bathrooms', '2'), ('Completion', 'Q1 2027')]},
                {'id': 'fpM3', 'label': '3BR', 'title': '3 Bedroom Penthouse', 'price': 'On request',
                 'rows': [('Area', '130–148 m²'), ('Bedrooms', '3'), ('Bathrooms', '3'), ('Completion', 'Q1 2027')]},
            ],
            'pay_kicker': 'Payment plan', 'pay_h2': 'Interest-free instalment schedule.',
            'pay_p': 'Four equal 25% instalments during construction. Completion targeted Q1 2027.',
            'pay_steps': pay_std('en', 'Q1 2027'), 'pay_note': NOTE_EN,
        },
        'ru': {
            'pricing_kicker': 'Цены и планировки', 'pricing_h2': 'Ориентировочные цены и типы апартаментов.',
            'pricing_p': 'Lifestyle-кондоминиум в Банг Тао — семь 7-этажных корпусов, 859 юнитов, ~200–500 м до пляжа. Планировки от компактных однушек до трёхспальных. Цены ориентировочные — не оферта.',
            'from_l': 'От', 'from_v': '4,78 млн THB', 'from_sub': '≈ $147 000 · 1 Bedroom S (29 m²)',
            'to_l': 'Планировки', 'to_v': '1–3 спальни', 'to_sub': '29–148 m² · 859 юнитов · скидка 5% при полной оплате',
            'tabs_aria': 'Типы апартаментов',
            'tabs': [
                {'id': 'fpM1s', 'label': '1BR S', 'title': '1 Bedroom S', 'price': 'От 4,78 млн THB',
                 'rows': [('Площадь', '29 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q1 2027')]},
                {'id': 'fpM1m', 'label': '1BR M', 'title': '1 Bedroom M', 'price': 'От 5,34 млн THB',
                 'rows': [('Площадь', '33 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q1 2027')]},
                {'id': 'fpM1l', 'label': '1BR L', 'title': '1 Bedroom L', 'price': 'От 6,48 млн THB',
                 'rows': [('Площадь', '37–41 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q1 2027')]},
                {'id': 'fpM1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'По запросу',
                 'rows': [('Площадь', '55–58 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q1 2027')]},
                {'id': 'fpM2', 'label': '2BR', 'title': '2 Bedroom', 'price': 'По запросу',
                 'rows': [('Площадь', '65–118 m²'), ('Спальни', '2'), ('С/у', '2'), ('Сдача', 'Q1 2027')]},
                {'id': 'fpM3', 'label': '3BR', 'title': '3 Bedroom Penthouse', 'price': 'По запросу',
                 'rows': [('Площадь', '130–148 m²'), ('Спальни', '3'), ('С/у', '3'), ('Сдача', 'Q1 2027')]},
            ],
            'pay_kicker': 'График платежей', 'pay_h2': 'Беспроцентная рассрочка.',
            'pay_p': 'Четыре равных платежа по 25% в период строительства. Сдача — Q1 2027.',
            'pay_steps': pay_std('ru', 'Q1 2027'), 'pay_note': NOTE_RU,
        },
    },
    'artrio': {
        'files': {'en': 'the-title-artrio-en.html', 'ru': 'the-title-artrio.html'},
        'en': {
            'pricing_kicker': 'Pricing & floor plans', 'pricing_h2': 'Indicative pricing and apartment layouts.',
            'pricing_p': 'Art-inspired condominium in Bang Tao — four 7-storey buildings, 435 units. Layouts from compact one-bedroom to two-bedroom duplexes. Pricing is indicative — not an offer.',
            'from_l': 'Starting from', 'from_v': '4.26M THB', 'from_sub': 'approx. $131,000 · 1 Bedroom S (28 m²)',
            'to_l': 'Layouts', 'to_v': '1–2 bed', 'to_sub': '28–132 m² · 435 units · 5% discount on full payment',
            'tabs_aria': 'Apartment types',
            'tabs': [
                {'id': 'fpA1s', 'label': '1BR S', 'title': '1 Bedroom S (1BS)', 'price': 'From 4.26M THB',
                 'rows': [('Area', '28–29 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q1 2027')]},
                {'id': 'fpA1m', 'label': '1BR M', 'title': '1 Bedroom M (1BM)', 'price': 'From 4.70M THB',
                 'rows': [('Area', '32–34 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q1 2027')]},
                {'id': 'fpA1l', 'label': '1BR L', 'title': '1 Bedroom L (1BL)', 'price': 'From 5.88M THB',
                 'rows': [('Area', '40–43 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q1 2027')]},
                {'id': 'fpA1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'On request',
                 'rows': [('Area', '57–58 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q1 2027')]},
                {'id': 'fpAd', 'label': '1BR Duplex', 'title': '1 Bedroom Duplex', 'price': 'On request',
                 'rows': [('Area', '61–63 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q1 2027')]},
                {'id': 'fpA2', 'label': '2BR', 'title': '2 Bedroom', 'price': 'On request',
                 'rows': [('Area', '65–132 m²'), ('Bedrooms', '2'), ('Bathrooms', '2'), ('Completion', 'Q1 2027')]},
            ],
            'pay_kicker': 'Payment plan', 'pay_h2': 'Interest-free instalment schedule.',
            'pay_p': 'Four equal 25% instalments during construction. Completion targeted Q1 2027.',
            'pay_steps': pay_std('en', 'Q1 2027'), 'pay_note': NOTE_EN,
        },
        'ru': {
            'pricing_kicker': 'Цены и планировки', 'pricing_h2': 'Ориентировочные цены и типы апартаментов.',
            'pricing_p': 'Кондоминиум в Банг Тао с «галерейной» концепцией — четыре 7-этажных корпуса, 435 юнитов. Планировки от компактных однушек до двухспальных дуплексов. Цены ориентировочные — не оферта.',
            'from_l': 'От', 'from_v': '4,26 млн THB', 'from_sub': '≈ $131 000 · 1 Bedroom S (28 m²)',
            'to_l': 'Планировки', 'to_v': '1–2 спальни', 'to_sub': '28–132 m² · 435 юнитов · скидка 5% при полной оплате',
            'tabs_aria': 'Типы апартаментов',
            'tabs': [
                {'id': 'fpA1s', 'label': '1BR S', 'title': '1 Bedroom S (1BS)', 'price': 'От 4,26 млн THB',
                 'rows': [('Площадь', '28–29 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q1 2027')]},
                {'id': 'fpA1m', 'label': '1BR M', 'title': '1 Bedroom M (1BM)', 'price': 'От 4,70 млн THB',
                 'rows': [('Площадь', '32–34 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q1 2027')]},
                {'id': 'fpA1l', 'label': '1BR L', 'title': '1 Bedroom L (1BL)', 'price': 'От 5,88 млн THB',
                 'rows': [('Площадь', '40–43 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q1 2027')]},
                {'id': 'fpA1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'По запросу',
                 'rows': [('Площадь', '57–58 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q1 2027')]},
                {'id': 'fpAd', 'label': '1BR Duplex', 'title': '1 Bedroom Duplex', 'price': 'По запросу',
                 'rows': [('Площадь', '61–63 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q1 2027')]},
                {'id': 'fpA2', 'label': '2BR', 'title': '2 Bedroom', 'price': 'По запросу',
                 'rows': [('Площадь', '65–132 m²'), ('Спальни', '2'), ('С/у', '2'), ('Сдача', 'Q1 2027')]},
            ],
            'pay_kicker': 'График платежей', 'pay_h2': 'Беспроцентная рассрочка.',
            'pay_p': 'Четыре равных платежа по 25% в период строительства. Сдача — Q1 2027.',
            'pay_steps': pay_std('ru', 'Q1 2027'), 'pay_note': NOTE_RU,
        },
    },
    'adora': {
        'files': {'en': 'the-title-adora-en.html', 'ru': 'the-title-adora.html'},
        'en': {
            'pricing_kicker': 'Pricing & floor plans', 'pricing_h2': 'Indicative pricing and apartment layouts.',
            'pricing_p': 'Low-rise lifestyle condominium near the ocean — eight 4-storey buildings, 210 units. Layouts from one-bedroom to two-bedroom. Pricing is indicative — not an offer.',
            'from_l': 'Starting from', 'from_v': '4.2M THB', 'from_sub': 'approx. $122,000 · 1 Bedroom (32 m²)',
            'to_l': 'Layouts', 'to_v': '1–2 bed', 'to_sub': '32–81 m² · 210 units · interest-free instalments',
            'tabs_aria': 'Apartment types',
            'tabs': [
                {'id': 'fpAdo1', 'label': '1BR', 'title': '1 Bedroom', 'price': 'From 4.2M THB',
                 'rows': [('Area', '32–43 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q1 2027')]},
                {'id': 'fpAdo1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'On request',
                 'rows': [('Area', '49–57 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q1 2027')]},
                {'id': 'fpAdo2', 'label': '2BR', 'title': '2 Bedroom', 'price': 'On request',
                 'rows': [('Area', '63–81 m²'), ('Bedrooms', '2'), ('Bathrooms', '2'), ('Completion', 'Q1 2027')]},
            ],
            'pay_kicker': 'Payment plan', 'pay_h2': 'Interest-free instalment schedule.',
            'pay_p': 'Four equal 25% instalments during construction, or full payment within 30 days. Completion targeted Q1 2027.',
            'pay_steps': pay_std('en', 'Q1 2027'), 'pay_note': NOTE_EN,
        },
        'ru': {
            'pricing_kicker': 'Цены и планировки', 'pricing_h2': 'Ориентировочные цены и типы апартаментов.',
            'pricing_p': 'Малоэтажный lifestyle-кондоминиум у океана — восемь 4-этажных корпусов, 210 юнитов. Планировки от однушек до двухспальных. Цены ориентировочные — не оферта.',
            'from_l': 'От', 'from_v': '4,2 млн THB', 'from_sub': '≈ $122 000 · 1 Bedroom (32 m²)',
            'to_l': 'Планировки', 'to_v': '1–2 спальни', 'to_sub': '32–81 m² · 210 юнитов · беспроцентная рассрочка',
            'tabs_aria': 'Типы апартаментов',
            'tabs': [
                {'id': 'fpAdo1', 'label': '1BR', 'title': '1 Bedroom', 'price': 'От 4,2 млн THB',
                 'rows': [('Площадь', '32–43 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q1 2027')]},
                {'id': 'fpAdo1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'По запросу',
                 'rows': [('Площадь', '49–57 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q1 2027')]},
                {'id': 'fpAdo2', 'label': '2BR', 'title': '2 Bedroom', 'price': 'По запросу',
                 'rows': [('Площадь', '63–81 m²'), ('Спальни', '2'), ('С/у', '2'), ('Сдача', 'Q1 2027')]},
            ],
            'pay_kicker': 'График платежей', 'pay_h2': 'Беспроцентная рассрочка.',
            'pay_p': 'Четыре равных платежа по 25% в период строительства или полная оплата в течение 30 дней. Сдача — Q1 2027.',
            'pay_steps': pay_std('ru', 'Q1 2027'), 'pay_note': NOTE_RU,
        },
    },
    'katabello': {
        'files': {'en': 'the-title-katabello-en.html', 'ru': 'the-title-katabello.html'},
        'en': {
            'pricing_kicker': 'Pricing & floor plans', 'pricing_h2': 'Indicative pricing and apartment layouts.',
            'pricing_p': 'Mediterranean-style leisure condo resort near Kata Beach — eight 7-storey buildings, 760 units. Layouts from one-bedroom to sea-view penthouses. Pricing is indicative — not an offer.',
            'from_l': 'Starting from', 'from_v': '3.83M THB', 'from_sub': 'approx. $118,000 · 1 Bedroom (28 m²)',
            'to_l': 'Up to', 'to_v': '11.97M THB', 'to_sub': 'Penthouse · 68–168 m²',
            'tabs_aria': 'Apartment types',
            'tabs': [
                {'id': 'fpK1', 'label': '1BR', 'title': '1 Bedroom', 'price': 'From 3.83M THB',
                 'rows': [('Area', '28–41 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q3 2027')]},
                {'id': 'fpK1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'From 6.01M THB',
                 'rows': [('Area', '47–56 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q3 2027')]},
                {'id': 'fpK2', 'label': '2BR', 'title': '2 Bedroom', 'price': 'From 8.32M THB',
                 'rows': [('Area', '66–71 m²'), ('Bedrooms', '2'), ('Bathrooms', '2'), ('Completion', 'Q3 2027')]},
                {'id': 'fpKph', 'label': 'Penthouse', 'title': 'Penthouse', 'price': 'From 11.97M THB',
                 'rows': [('Area', '68–168 m²'), ('Bedrooms', '2–3'), ('Bathrooms', '2–3'), ('Completion', 'Q3 2027')]},
            ],
            'pay_kicker': 'Payment plan', 'pay_h2': 'Interest-free instalment schedule.',
            'pay_p': 'Four equal 25% instalments tied to a fixed timeline during construction. Completion targeted Q3 2027.',
            'pay_steps': pay_katabello('en'), 'pay_note': NOTE_EN,
        },
        'ru': {
            'pricing_kicker': 'Цены и планировки', 'pricing_h2': 'Ориентировочные цены и типы апартаментов.',
            'pricing_p': 'Курортный кондоминиум в средиземноморском стиле у пляжа Ката — восемь 7-этажных корпусов, 760 юнитов. Планировки от однушек до пентхаусов с видом на море. Цены ориентировочные — не оферта.',
            'from_l': 'От', 'from_v': '3,83 млн THB', 'from_sub': '≈ $118 000 · 1 Bedroom (28 m²)',
            'to_l': 'До', 'to_v': '11,97 млн THB', 'to_sub': 'Пентхаус · 68–168 m²',
            'tabs_aria': 'Типы апартаментов',
            'tabs': [
                {'id': 'fpK1', 'label': '1BR', 'title': '1 Bedroom', 'price': 'От 3,83 млн THB',
                 'rows': [('Площадь', '28–41 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q3 2027')]},
                {'id': 'fpK1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'От 6,01 млн THB',
                 'rows': [('Площадь', '47–56 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q3 2027')]},
                {'id': 'fpK2', 'label': '2BR', 'title': '2 Bedroom', 'price': 'От 8,32 млн THB',
                 'rows': [('Площадь', '66–71 m²'), ('Спальни', '2'), ('С/у', '2'), ('Сдача', 'Q3 2027')]},
                {'id': 'fpKph', 'label': 'Penthouse', 'title': 'Пентхаус', 'price': 'От 11,97 млн THB',
                 'rows': [('Площадь', '68–168 m²'), ('Спальни', '2–3'), ('С/у', '2–3'), ('Сдача', 'Q3 2027')]},
            ],
            'pay_kicker': 'График платежей', 'pay_h2': 'Беспроцентная рассрочка.',
            'pay_p': 'Четыре равных платежа по 25% по фиксированному графику в период строительства. Сдача — Q3 2027.',
            'pay_steps': pay_katabello('ru'), 'pay_note': NOTE_RU,
        },
    },
    'vivi': {
        'files': {'en': 'title-vivi-en.html', 'ru': 'title-vivi.html'},
        'en': {
            'pricing_kicker': 'Pricing & floor plans', 'pricing_h2': 'Indicative pricing and apartment layouts.',
            'pricing_p': 'Compact resort condominium in Bang Tao — 181 units, sea and mountain views. One-bedroom layouts. Pricing is indicative — not an offer.',
            'from_l': 'Starting from', 'from_v': '3.16M THB', 'from_sub': 'approx. $97,000 · 1 Bedroom S (28 m²)',
            'to_l': 'Layouts', 'to_v': '1 bed', 'to_sub': '28–46 m² · 181 units · completion Q4 2027',
            'tabs_aria': 'Apartment types',
            'tabs': [
                {'id': 'fpVi1s', 'label': '1BR S', 'title': '1 Bedroom S', 'price': 'From 3.16M THB',
                 'rows': [('Area', '28 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q4 2027')]},
                {'id': 'fpVi1m', 'label': '1BR M', 'title': '1 Bedroom M', 'price': 'On request',
                 'rows': [('Area', '30 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q4 2027')]},
                {'id': 'fpVi1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'On request',
                 'rows': [('Area', '46 m²'), ('Bedrooms', '1'), ('Bathrooms', '1'), ('Completion', 'Q4 2027')]},
            ],
            'pay_kicker': 'Payment plan', 'pay_h2': 'Interest-free instalment schedule.',
            'pay_p': 'Four equal 25% instalments during construction. Completion targeted Q4 2027.',
            'pay_steps': pay_std('en', 'Q4 2027'), 'pay_note': NOTE_EN,
        },
        'ru': {
            'pricing_kicker': 'Цены и планировки', 'pricing_h2': 'Ориентировочные цены и типы апартаментов.',
            'pricing_p': 'Компактный курортный кондоминиум в Банг Тао — 181 юнит, виды на море и горы. Планировки с одной спальней. Цены ориентировочные — не оферта.',
            'from_l': 'От', 'from_v': '3,16 млн THB', 'from_sub': '≈ $97 000 · 1 Bedroom S (28 m²)',
            'to_l': 'Планировки', 'to_v': '1 спальня', 'to_sub': '28–46 m² · 181 юнит · сдача Q4 2027',
            'tabs_aria': 'Типы апартаментов',
            'tabs': [
                {'id': 'fpVi1s', 'label': '1BR S', 'title': '1 Bedroom S', 'price': 'От 3,16 млн THB',
                 'rows': [('Площадь', '28 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q4 2027')]},
                {'id': 'fpVi1m', 'label': '1BR M', 'title': '1 Bedroom M', 'price': 'По запросу',
                 'rows': [('Площадь', '30 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q4 2027')]},
                {'id': 'fpVi1p', 'label': '1BR Plus', 'title': '1 Bedroom Plus', 'price': 'По запросу',
                 'rows': [('Площадь', '46 m²'), ('Спальни', '1'), ('С/у', '1'), ('Сдача', 'Q4 2027')]},
            ],
            'pay_kicker': 'График платежей', 'pay_h2': 'Беспроцентная рассрочка.',
            'pay_p': 'Четыре равных платежа по 25% в период строительства. Сдача — Q4 2027.',
            'pay_steps': pay_std('ru', 'Q4 2027'), 'pay_note': NOTE_RU,
        },
    },
}

# Insert the block immediately BEFORE the opening tag of the investment
# section (new projects) or the location section (older projects).
MARKER_BEFORE = re.compile(
    r'(?:<!--[^>]*-->\s*\n\s*)?<section class="s cream-2" id="investment">'
    r'|(?:<!--[^>]*-->\s*\n\s*)?<section class="s[^"]*" id="location">'
)

def process_file(path, lang, meta):
    text = path.read_text(encoding='utf-8')
    if 'id="pricing"' in text:
        print(f'  skip (already has pricing): {path.name}')
        return False

    block = build_pricing_section(lang, meta) + '\n\n' + build_payment_section(lang, meta) + '\n\n'
    m = MARKER_BEFORE.search(text)
    if not m:
        print(f'  ERROR: no insertion point in {path.name}')
        return False
    text = text[:m.start()] + block + text[m.start():]

    needle = "document.addEventListener('DOMContentLoaded',()=>document.body.classList.add('page-ready'));"
    if 'Floor-plan tabs' not in text and needle in text:
        text = text.replace(needle, needle + FP_JS, 1)

    # Update lowPrice in JSON-LD if present (per project, THB)
    low_prices = {
        'the-modeva': '4781000',
        'the-title-artrio': '4263000',
        'the-title-adora': '4200000',
        'the-title-katabello': '3830000',
        'title-vivi': '3160000',
    }
    for key, p in low_prices.items():
        if path.stem == key + '-en' or path.stem == key:
            text = re.sub(r'"lowPrice":\s*"[^"]*"', f'"lowPrice": "{p}"', text, count=1)
            break

    path.write_text(text, encoding='utf-8')
    print(f'  updated: {path.name}')
    return True

def main():
    for proj_key, proj in PROJECTS.items():
        print(proj_key)
        for lang, fname in proj['files'].items():
            process_file(ROOT / fname, lang, proj)

if __name__ == '__main__':
    main()
