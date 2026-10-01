#!/usr/bin/env python3
"""Apply the shared MIRA arrow wordmark after static page generators.
Preserves each brand link destination, accessible label and descriptive subtitle.
"""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
LOCKUP = '<b class="mira-lockup">МИРА<i aria-hidden="true">↗</i></b>'
CSS = '<link rel="stylesheet" href="/mira/brand.css?v=20261001">'
ANCHOR = re.compile(r'(<a\b[^>]*class="([^"]*)"[^>]*>)(.*?)(</a>)', re.S)

def wire(text):
    count = 0
    def replace(m):
        nonlocal count
        if not set(m[2].split()).intersection({'brand','logo','wordmark','wordmark-small'}):
            return m[0]
        if 'mira-lockup' in m[3]: return m[0]
        if not re.match(r'\s*МИРА', m[3]): return m[0]
        rest = re.sub(r'^\s*МИРА\s*', '', m[3])
        rest = re.sub(r'^(?:↗|<(?:i|span)\b[^>]*>\s*↗\s*</(?:i|span)>)\s*', '', rest)
        count += 1
        return m[1] + LOCKUP + rest + m[4]
    text = ANCHOR.sub(replace, text)
    if 'mira-lockup' in text and '/mira/brand.css' not in text:
        text = text.replace('</head>', CSS + '</head>', 1)
    return text

def build():
    changed = 0
    for path in sorted((ROOT/'mira').rglob('*.html')):
        before = path.read_text(encoding='utf-8'); after = wire(before)
        if before != after:
            path.write_text(after, encoding='utf-8'); changed += 1
    print(f'MIRA shared wordmark: {changed} pages updated')
if __name__ == '__main__': build()
