#!/usr/bin/env python3
"""One public navigation, applied after generators. Legacy URLs remain intact.

Do not include email previews, private cabinets, demos or printed assets here.
Their layouts and workflow controls are independent of public site navigation.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = {'go', 'start', 'agency', 'design', 'business', 'growth', 'practical',
            'corporate', 'access', 'payments', 'phuket', 'catalog', 'documents', 'en'}
CSS = '<link rel="stylesheet" href="/mira/navigation.css?v=20261001">'
MARKER = re.compile(r'<!-- mira-navigation -->.*?<!-- /mira-navigation -->', re.S)

def navigation(path):
    section = path.split('/')[0]
    current = '/mira/'
    if path != 'index.html':
        current = '/mira/catalog/' if section in {'catalog', 'phuket'} else '/mira/documents/' if section == 'documents' else '/mira/go/'
    if section == 'payments':
        current = '/mira/#payments'
    items = [('/mira/', 'О МИРА'), ('/mira/go/', 'Начать работу'),
             ('/mira/catalog/', 'Каталог'), ('/mira/documents/', 'Документы'),
             ('/mira/go/#payments' if section == 'go' else '/mira/#payments', 'Оплата')]
    if section == 'en':
        items = [('/mira/en/#about', 'The idea'), ('/mira/en/#partnership', 'Partnership'), ('/mira/en/#contact', 'Get in touch'), ('/mira/', 'RU')]
        current = ''
    links = ''.join(f'<a href="{url}"'+(' aria-current="page"' if url == current else '')+f'>{label}</a>' for url, label in items)
    if section != 'en':
        links += '<a class="mira-shell-apply" href="https://pilot.wegc.fund/mira/request/">Подать заявку ↗</a><a href="/mira/en/" lang="en" aria-label="For international partners">EN</a>'
    shell = '<!-- mira-navigation --><div class="mira-shell" role="banner"><div class="mira-shell-inner"><a class="mira-shell-brand" href="/mira/" aria-label="МИРА — главная"><b>МИРА<span aria-hidden="true">↗</span></b><span class="mira-shell-descriptor">B2B Marketplace<br>зарубежной недвижимости</span></a><nav class="mira-shell-desktop" aria-label="Основная навигация">'+links+'</nav><details class="mira-shell-mobile"><summary>Меню<span aria-hidden="true">☰</span></summary><nav aria-label="Мобильная навигация">'+links+'</nav></details></div></div><!-- /mira-navigation -->'
    shell = shell.replace('class="mira-shell"', f'class="mira-shell" data-mira-surface="{section}"', 1)
    if section == 'en':
        shell = shell.replace('href="/mira/" aria-label="МИРА — главная"', 'href="/mira/en/" aria-label="MIRA — home"').replace('зарубежной недвижимости', 'international property').replace('Основная навигация', 'Main navigation').replace('Мобильная навигация', 'Mobile navigation').replace('>Меню<', '>Menu<')
    return shell

def wire(text, path):
    shell = navigation(path)
    if MARKER.search(text):
        text = MARKER.sub(lambda _: shell, text, count=1)
    else:
        pattern = r'<nav\b[^>]*>.*?</nav>' if path == 'index.html' else r'<header\b[^>]*>.*?</header>'
        text, count = re.subn(pattern, lambda _: shell, text, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f'Missing public header: {path}')
    if 'href="/mira/navigation.css' not in text:
        text = text.replace('</head>', CSS+'</head>', 1)
    # Any public brand returns home; explicit demos and their workflow links stay intact.
    text = re.sub(r'(<a\b[^>]*class="(?:brand|logo|wordmark)(?: [^"]*)?"[^>]*href=")/mira/(?:start|agency|go)/(")', r'\1/mira/\2', text)
    return text

def build(root=ROOT):
    changed = 0
    for path in sorted((Path(root)/'mira').rglob('*.html')):
        relative = path.relative_to(Path(root)/'mira').as_posix()
        if relative != 'index.html' and relative.split('/')[0] not in SECTIONS:
            continue
        if '/source/' in relative or '/downloads/' in relative:
            continue
        before = path.read_text(encoding='utf-8')
        after = wire(before, relative)
        if before != after:
            path.write_text(after, encoding='utf-8'); changed += 1
    print(f'MIRA public navigation: {changed} pages updated')

if __name__ == '__main__':
    build()
