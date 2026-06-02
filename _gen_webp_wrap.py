#!/usr/bin/env python3
"""Wrap <img> (local jpg/png) in <picture> + webp source on live, indexable pages.

Skips files that carry a robots noindex meta (drafts/backups/redirect stubs).
Adds `picture{display:contents}` so wrapping does not change layout
(no direct-child CSS selectors exist; all img rules are descendant selectors).
"""
import os, re
import _gen_webp as g

NOINDEX_RE = re.compile(r"""name=["']robots["'][^>]*noindex""", re.IGNORECASE)
DISPLAY_RULE = "picture{display:contents}"


def webp_for(src):
    return g.webp_src(src)


def wrap_imgs(html):
    count = 0

    def repl(m):
        nonlocal count
        tag = m.group(0)
        sm = g.SRC_RE.search(tag)
        if not sm:
            return tag
        src = sm.group(1)
        if not g.RASTER_RE.search(src):
            return tag
        if g.resolve(src) is None:
            return tag
        count += 1
        ws = webp_for(src)
        return f'<picture><source srcset="{ws}" type="image/webp">{tag}</picture>'

    new = g.IMG_RE.sub(repl, html)
    return new, count


def ensure_display_rule(html):
    if DISPLAY_RULE in html:
        return html
    idx = html.find("</style>")
    if idx != -1:
        return html[:idx] + DISPLAY_RULE + html[idx:]
    # no inline style: inject a minimal one before </head>
    h = html.find("</head>")
    if h != -1:
        return html[:h] + f"<style>{DISPLAY_RULE}</style>\n" + html[h:]
    return html


def main():
    files = sorted(g.collect_html())
    modified = 0
    skipped = 0
    total_imgs = 0
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            html = f.read()
        if NOINDEX_RE.search(html):
            skipped += 1
            continue
        if "<picture>" in html:
            # already processed (idempotent guard)
            print(f"  already has <picture>, skipping: {os.path.relpath(fp, g.ROOT)}")
            skipped += 1
            continue
        new, n = wrap_imgs(html)
        if n == 0:
            continue
        new = ensure_display_rule(new)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(new)
        modified += 1
        total_imgs += n
        print(f"  +{n:3d} imgs  {os.path.relpath(fp, g.ROOT)}")
    print(f"\nmodified {modified} files, wrapped {total_imgs} <img> tags, skipped {skipped}")


if __name__ == "__main__":
    main()
