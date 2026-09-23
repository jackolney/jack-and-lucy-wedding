#!/usr/bin/env python3
"""
Derives the site's images from Lucy's two master artworks in art/source/.

    python3 build_assets.py

Masters (keep these; everything else is regenerated):
    source/card.png           the save-the-date, 1056x1489
    source/floral-sides.png   the two flower columns, transparent, 1536x1024

Produces, into ../images/:
    save-the-date.jpg   the card, sized for the page
    barn.webp           the barn lifted off the card, transparent
    floral-spray.webp   the coral cluster from the foot of the card
    floral-left.webp    the left flower column
    floral-right.webp   the right flower column

The barn and the spray are cut out of the card, so the paper behind them has
to go. Rather than masking to a flat cream — which leaves a faint rectangle
wherever the page cream and the card's paper differ — the paper is turned into
transparency and divided back out of the ink, which keeps the pencil its own
colour and lets the artwork sit on the page.
"""

import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source")
DEST = os.path.join(os.path.dirname(HERE), "images")

# Where each piece sits on the card, in its own 1056x1489 pixels
BARN_BOX = (246, 292, 806, 550)
SPRAY_BOX = (296, 1272, 764, 1448)

CARD_WIDTH = 900          # the page never shows it wider than ~350px
WEBP_QUALITY = 88


def lift(card, box, out, paper=245.5, spread=46.0, gamma=0.9, drop_colour=False):
    """
    Cut a piece out of the card and turn its paper into transparency.

    drop_colour also removes anything coloured. The wreath overlaps the barn at
    both ends, so no rectangle around the barn is free of flowers — but the barn
    is neutral pencil and the flowers are not, so saturation separates them.
    """
    reg = np.asarray(card.crop(box)).astype(float)
    lum = reg @ [0.299, 0.587, 0.114]
    alpha = np.clip((paper - lum) / spread, 0, 1) ** gamma
    if drop_colour:
        hi = reg.max(axis=2)
        sat = (hi - reg.min(axis=2)) / np.maximum(hi, 1.0)
        alpha *= np.clip((0.17 - sat) / 0.07, 0, 1)   # soft edge, no hard cut
    a3 = alpha[..., None]
    # divide the paper back out, so the ink keeps its own tone
    ink = np.where(a3 > 0.02,
                   np.clip((reg - paper * (1 - a3)) / np.maximum(a3, 0.02), 0, 255),
                   reg)
    im = Image.fromarray(
        np.dstack([ink.astype("uint8"), (alpha * 255).astype("uint8")]), "RGBA")
    path = os.path.join(DEST, out)
    im.save(path, "WEBP", quality=WEBP_QUALITY, method=6)
    report(out, im.size, path)


def split_columns(sides):
    """Halve the flower artwork and crop each column to its own content."""
    w, h = sides.size
    for name, box in (("floral-left.webp", (0, 0, w // 2, h)),
                      ("floral-right.webp", (w // 2, 0, w, h))):
        half = sides.crop(box)
        a = np.asarray(half)[..., 3]
        cols = np.where((a > 24).any(axis=0))[0]
        rows = np.where((a > 24).any(axis=1))[0]
        if not len(cols) or not len(rows):
            raise SystemExit(f"{name}: no artwork found in this half")
        tight = half.crop((cols.min(), rows.min(), cols.max() + 1, rows.max() + 1))
        path = os.path.join(DEST, name)
        tight.save(path, "WEBP", quality=WEBP_QUALITY, method=6)
        report(name, tight.size, path)


def report(name, size, path):
    print(f"  {name:20s} {size[0]}x{size[1]}  {os.path.getsize(path) // 1024}KB")


def main():
    card_path = os.path.join(SRC, "card.png")
    sides_path = os.path.join(SRC, "floral-sides.png")
    for p in (card_path, sides_path):
        if not os.path.exists(p):
            raise SystemExit(f"missing master artwork: {p}")

    card = Image.open(card_path).convert("RGB")
    sides = Image.open(sides_path).convert("RGBA")
    print(f"card {card.size[0]}x{card.size[1]}, "
          f"flower sides {sides.size[0]}x{sides.size[1]}")

    small = card.copy()
    small.thumbnail((CARD_WIDTH, CARD_WIDTH), Image.LANCZOS)
    out = os.path.join(DEST, "save-the-date.jpg")
    small.save(out, quality=88, optimize=True, progressive=True)
    report("save-the-date.jpg", small.size, out)

    lift(card, BARN_BOX, "barn.webp", drop_colour=True)
    lift(card, SPRAY_BOX, "floral-spray.webp", paper=247.0, spread=58.0)
    split_columns(sides)
    print("\nIf you replace a master, re-run this and the site picks up the change.")


if __name__ == "__main__":
    main()
