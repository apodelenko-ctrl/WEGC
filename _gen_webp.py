#!/usr/bin/env python3
"""Generate .webp siblings for referenced raster images and wrap <img> in <picture> + webp source.

- Scans live HTML files (excludes backups/archives/redirect stubs).
- For every local <img> with .jpg/.jpeg/.png src, generates a sibling .webp (quality 82).
- Rewrites the <img> into <picture><source srcset=".webp" type="image/webp">{img}</picture>.
- Ensures `picture{display:contents}` exists in each modified file so layout is unchanged.
"""
import os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
QUALITY = 82
METHOD = 6

EXCLUDE_SUBSTR = ("backup", "_archive", "archive", "wet-agency", "yandex_")

IMG_RE = re.compile(r"<img\b[^>]*?>", re.IGNORECASE)
SRC_RE = re.compile(r"""\bsrc\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
RASTER_RE = re.compile(r"\.(jpe?g|png)(\?[^\"']*)?$", re.IGNORECASE)


def is_live(path):
    name = os.path.basename(path).lower()
    return not any(s in name for s in EXCLUDE_SUBSTR)


def collect_html():
    out = []
    for dirpath, _dirs, files in os.walk(ROOT):
        # skip hidden/git/node dirs
        if "/." in dirpath or "/node_modules" in dirpath:
            continue
        for f in files:
            if f.lower().endswith(".html") and is_live(os.path.join(dirpath, f)):
                out.append(os.path.join(dirpath, f))
    return out


def resolve(src):
    """Map an html src to a filesystem path under ROOT (None if remote/data)."""
    s = src.split("?")[0].split("#")[0]
    if s.startswith(("http://", "https://", "data:", "//")):
        return None
    if s.startswith("/"):
        return os.path.join(ROOT, s.lstrip("/"))
    return None  # only handle root-absolute paths (the site uses these)


def webp_src(src):
    s = src.split("?")[0].split("#")[0]
    return re.sub(r"\.(jpe?g|png)$", ".webp", s, flags=re.IGNORECASE)


def gen_webp(fs_path):
    out = re.sub(r"\.(jpe?g|png)$", ".webp", fs_path, flags=re.IGNORECASE)
    if os.path.exists(out):
        return ("exists", out)
    if not os.path.exists(fs_path):
        return ("missing-src", out)
    try:
        im = Image.open(fs_path)
        if im.mode in ("P", "LA"):
            im = im.convert("RGBA")
        elif im.mode == "CMYK":
            im = im.convert("RGB")
        im.save(out, "WEBP", quality=QUALITY, method=METHOD)
        return ("ok", out)
    except Exception as e:  # noqa
        return (f"error:{e}", out)


def main():
    files = collect_html()
    targets = {}  # fs_path of source raster -> set of (file) referencing
    print(f"Scanning {len(files)} html files...")
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            html = f.read()
        for m in IMG_RE.finditer(html):
            sm = SRC_RE.search(m.group(0))
            if not sm:
                continue
            src = sm.group(1)
            if not RASTER_RE.search(src):
                continue
            fs = resolve(src)
            if fs:
                targets.setdefault(fs, set()).add(fp)

    print(f"Unique raster sources referenced: {len(targets)}")
    stats = {"ok": 0, "exists": 0, "missing-src": 0, "error": 0}
    total_jpg = total_webp = 0
    for fs in sorted(targets):
        status, out = gen_webp(fs)
        key = status if status in stats else "error"
        stats[key] += 1
        if status in ("ok", "exists") and os.path.exists(out):
            total_jpg += os.path.getsize(fs) if os.path.exists(fs) else 0
            total_webp += os.path.getsize(out)
        if status.startswith("error") or status == "missing-src":
            print(f"  {status}: {fs}")
    print("webp gen stats:", stats)
    if total_jpg:
        print(f"size (referenced, jpg+png -> webp): {total_jpg/1e6:.2f} MB -> {total_webp/1e6:.2f} MB "
              f"({100*(1-total_webp/total_jpg):.0f}% smaller)")
    return targets


if __name__ == "__main__":
    main()
