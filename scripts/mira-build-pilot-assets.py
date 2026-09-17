#!/usr/bin/env python3
"""Package only the reviewed public UI files for the dedicated MIRA Worker.

Never use the repository root as an assets directory: it includes operational
documents and server code. This bundle contains no business records or secrets.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'cloudflare-worker/mira/pilot-assets'
FILES = ('pilot.html', 'library.html', 'pilot.mjs', 'library.mjs', 'marketplace.css', 'library.css', 'pilot.css', 'agency-privacy.html')


def build(output=OUTPUT):
    output = Path(output)
    allowed = {'mira/' + name for name in FILES}
    if output.is_symlink():
        raise ValueError('Asset directory must not be a symlink')
    if output.exists():
        for path in output.rglob('*'):
            if path.is_symlink() or (path.is_file() and path.relative_to(output).as_posix() not in allowed):
                raise ValueError('Unexpected content in asset directory; review it before packaging')
    (output / 'mira').mkdir(parents=True, exist_ok=True)
    for name in FILES:
        content = (ROOT / 'mira' / name).read_text(encoding='utf8')
        if name in ('pilot.html', 'library.html'):
            content = content.replace('</header>', '<a href="/cdn-cgi/access/logout">Выйти</a></header>')
        (output / 'mira' / name).write_text(content, encoding='utf8')
    return sorted(allowed)


if __name__ == '__main__':
    for name in build():
        print(name)
