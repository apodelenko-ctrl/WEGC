#!/usr/bin/env python3
"""Install the existing WEGC public counter after all static generators.

Printed /start/ and /go/ addresses stay unchanged. These are landing-page
visits, not proven physical QR scans. No tracking on private/operator forms.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SNIPPET = '<script type="module" src="/mira/analytics.mjs?v=20260927"></script>'
DIRECTORIES = ('start', 'go', 'growth', 'business', 'practical', 'corporate', 'catalog', 'phuket')


def wire(text):
    # The vendor collector requires Referer. Send only the site origin to
    # external services, never the current page path or query string.
    text = text.replace('<meta name="referrer" content="no-referrer">',
                        '<meta name="referrer" content="strict-origin-when-cross-origin">')
    if '/mira/analytics.mjs' in text:
        return text
    # Keep the existing restrictions; permit only the vendor script and collector.
    def csp(match):
        content = match.group(1)
        for directive, allowed in (
            ('script-src', 'https://static.cloudflareinsights.com/beacon.min.js'),
            ('connect-src', 'https://cloudflareinsights.com'),
        ):
            pattern = rf'({directive}\s+)([^;]+)'
            if not re.search(pattern, content):
                raise ValueError(f'Missing {directive} in CSP')
            content = re.sub(pattern, lambda m: m[1] + ' '.join(
                [x for x in m[2].split() if x != "'none'"] + [allowed]), content)
        return '<meta http-equiv="Content-Security-Policy" content="' + content + '">'
    text = re.sub(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">', csp, text)
    if '</head>' not in text:
        raise ValueError('Missing head')
    return text.replace('</head>', SNIPPET + '</head>', 1)


def build(root=ROOT):
    paths = [root / 'mira/index.html']
    for name in DIRECTORIES:
        paths.extend(sorted((root / 'mira' / name).rglob('*.html')))
    changed = 0
    for path in paths:
        before = path.read_text(encoding='utf-8')
        after = wire(before)
        if after != before:
            path.write_text(after, encoding='utf-8')
            changed += 1
    print(f'MIRA analytics: {len(paths)} public pages checked, {changed} updated')


if __name__ == '__main__':
    build()
