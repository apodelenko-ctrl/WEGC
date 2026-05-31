#!/usr/bin/env python3
"""Wire downloaded floor-plan images into the fp-tab panels of passports."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "projects"

# panel id -> (image filename without dir, English label for alt)
MAPS = {
    'vivana': {
        'dir': '/images/projects/vivana',
        'name_en': 'The Title Vivana', 'name_ru': 'The Title Vivana',
        'files': {'en': 'the-title-vivana-en.html', 'ru': 'the-title-vivana.html'},
        'panels': {
            'fpV1s': ('fp-1bed-s.jpg', '1 Bedroom S'),
            'fpV1m': ('fp-1bed-m.jpg', '1 Bedroom M'),
            'fpV1l': ('fp-1bed-l.jpg', '1 Bedroom L'),
            'fpV1p': ('fp-1bed-p.jpg', '1 Bedroom Plus'),
            'fpV2m': ('fp-2bed-m.jpg', '2 Bedroom M'),
        },
    },
    'balcony': {
        'dir': '/images/projects/balcony',
        'name_en': 'The Title Balcony', 'name_ru': 'The Title Balcony',
        'files': {'en': 'the-title-balcony-en.html', 'ru': 'the-title-balcony.html'},
        'panels': {
            'fpB1m': ('fp-1bed-m.jpg', '1 Bedroom M'),
            'fpB1l': ('fp-1bed-l.jpg', '1 Bedroom L'),
            'fpB2s': ('fp-2bed-s.jpg', '2 Bedroom S'),
            'fpB2m': ('fp-2bed-m.jpg', '2 Bedroom M'),
        },
    },
}

PANEL_RE = re.compile(r'<div class="fp-panel[^"]*" id="(\w+)" role="tabpanel">.*?\n    </div>', re.S)

def transform_panel(block, panel_id, cfg):
    if panel_id not in cfg['panels']:
        return block
    fname, label = cfg['panels'][panel_id]
    src = f"{cfg['dir']}/{fname}"
    alt = f"{cfg['name_en']} — {label} floor plan"
    # drop spec-only modifier
    block = block.replace('class="fp-panel fp-spec-only active"', 'class="fp-panel active"', 1)
    block = block.replace('class="fp-panel fp-spec-only"', 'class="fp-panel"', 1)
    # insert figure right after the opening panel tag (before <div class="fp-info">)
    figure = (
        f'      <figure class="fp-figure" style="margin:0;background:#f3f0e8">'
        f'<a href="{src}" target="_blank" rel="noopener" style="display:block;width:100%;height:100%">'
        f'<img src="{src}" alt="{alt}" loading="lazy" style="object-fit:contain"/></a></figure>\n'
    )
    block = re.sub(r'(role="tabpanel">\n)(      <div class="fp-info">)', r'\1' + figure + r'\2', block, count=1)
    # remove the "floor plan on request" / "Планировка по запросу" row inside this panel
    block = re.sub(r'\s*<div class="row"><span class="k">(?:Floor plan|Планировка)</span>'
                   r'<span class="val">(?:Floor plan on request|Планировка по запросу)</span></div>', '', block, count=1)
    return block

def process(path, cfg):
    text = path.read_text(encoding='utf-8')
    def repl(m):
        return transform_panel(m.group(0), m.group(1), cfg)
    new = PANEL_RE.sub(repl, text)
    if new != text:
        path.write_text(new, encoding='utf-8')
        print('embedded floor plans:', path.name)
    else:
        print('no change:', path.name)

def main():
    for proj, cfg in MAPS.items():
        for lang, fname in cfg['files'].items():
            process(ROOT / fname, cfg)

if __name__ == '__main__':
    main()
