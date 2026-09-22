#!/usr/bin/env python3
"""
Packs the whole site into one self-contained .html file.

Stylesheet, fonts, artwork and photographs all go inside the single file, so it
works with no internet connection and nothing else alongside it — for sending
to someone to look at before the site is live.

    python3 build_standalone.py

Writes art/out/jack-and-lucy-website.html
"""

import base64
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")

# Photographs are never shown wider than ~350px, so shrink them for this file.
PHOTO_MAX = 760


def data_uri(path, mime):
    with open(path, "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode()


def photo_uri(path):
    try:
        from PIL import Image
        import io
        im = Image.open(path)
        im.thumbnail((PHOTO_MAX, PHOTO_MAX), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except ImportError:
        return data_uri(path, "image/jpeg")


def font_css():
    data = json.load(open(os.path.join(HERE, "fonts.json")))
    out = []
    for key, b64 in data.items():
        fam, wt = key.split("|")
        weight = "300 400" if fam == "Cormorant Garamond" else wt
        out.append(
            f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{weight};"
            f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )
    return "".join(out)


def main():
    os.makedirs(OUT, exist_ok=True)
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    css = open(os.path.join(ROOT, "styles.css"), encoding="utf-8").read()

    # Fold the background-image urls in the stylesheet into data URIs
    for name in ("floral-left.svg", "floral-right.svg"):
        uri = data_uri(os.path.join(ROOT, "images", name), "image/svg+xml")
        css = css.replace(f'url("images/{name}")', f'url("{uri}")')

    # Drop the Google Fonts link and the stylesheet link; inline both instead
    html = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", html)
    html = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis[^>]*>\s*', "", html)
    html = html.replace('<link rel="stylesheet" href="styles.css">',
                        f"<style>{font_css()}\n{css}</style>")

    # Inline every <img src="images/...">
    def swap(m):
        src = m.group(1)
        path = os.path.join(ROOT, src)
        if src.endswith(".svg"):
            return f'src="{data_uri(path, "image/svg+xml")}"'
        return f'src="{photo_uri(path)}"'

    html = re.sub(r'src="(images/[^"]+)"', swap, html)

    # A standalone file needs the document wrapper the published page gets free
    html = ('<!doctype html>\n<html lang="en-GB">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, '
            'viewport-fit=cover">\n' + html + "\n</head>\n</html>\n")

    left = re.findall(r'src="(images/[^"]+)"', html) + \
        re.findall(r'url\("images/', html)
    assert not left, f"still referencing external files: {left}"

    dest = os.path.join(OUT, "jack-and-lucy-website.html")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"{dest}  {len(html.encode()) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
