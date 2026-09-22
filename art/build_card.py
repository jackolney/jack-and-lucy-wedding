#!/usr/bin/env python3
"""
Redraws Jack & Lucy's save-the-date as resolution-independent vector art.

The original was a 1135x1600 JPEG, too compressed to enlarge. This rebuilds it:
Lucy's barn as clean line art (geometry measured off her drawing), the
watercolour wildflower frame generated procedurally in her palette, and the
lettering set in real type.

Usage:
    python3 build_card.py                 # writes save-the-date.svg
    python3 build_card.py --no-type       # frame and barn only, no lettering
    python3 build_card.py --frame-only    # just the floral frame, transparent

Renders to PNG/PDF via render.mjs.
"""

import argparse
import base64
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Canvas. 1000 x 1414 is the A-series ratio, so it prints to A6/A5/A4 with no
# cropping. Everything below is in these units.
# ---------------------------------------------------------------------------
W, H = 1000.0, 1414.0

# ---------------------------------------------------------------------------
# Palette, sampled from Lucy's card
# ---------------------------------------------------------------------------
PAPER       = "#f8f6f2"
PENCIL      = "#8d8679"   # the barn's graphite line
LETTER      = "#8a8076"   # her lettering colour
STEM        = "#a79c74"
STEM_DEEP   = "#8e8659"

ROSE        = ("#f4d3ce", "#dd928a")   # (centre, edge) of each petal
CORAL       = ("#f9dcc2", "#e59870")
BLUSH       = ("#f8ded2", "#eaa98a")
BLUE        = ("#cfdcec", "#8aa8ce")
CENTRE      = "#a8813c"
CENTRE_DEEP = "#8a6526"
LEAF        = ("#c2c28d", "#8f965d")
POD         = ("#d8d3a4", "#a8a06a")
FERN        = "#4e4f38"

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def f(x):
    """Trim floats so the SVG stays readable and small."""
    return f"{x:.2f}".rstrip("0").rstrip(".")


def rot(px, py, deg):
    a = math.radians(deg)
    return px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)


def smooth_path(pts):
    """A Catmull-Rom spline through pts, emitted as cubic beziers."""
    if len(pts) < 2:
        return ""
    d = [f"M{f(pts[0][0])},{f(pts[0][1])}"]
    ext = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d.append(f"C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}")
    return " ".join(d)


# ===========================================================================
# THE BARN
# Coordinates measured from Lucy's drawing by scanning its silhouette: the
# roof rises from (0,152) to a ridge at y=23 running x=128..390, then falls
# away to (576,172); eaves band at y=139..153; ground at y=242.
# Drawn in that 576 x 274 space and scaled into the card.
# ===========================================================================

# Silhouette sampled off Lucy's drawing. The left side steps down sharply from
# the ridge then sweeps out in a long cat-slide; the right runs at a steady
# pitch and eases at the very end. That asymmetry is the barn's character, so
# it is traced point for point rather than idealised into two straight slopes.
LEFT_SWEEP = [(0, 153), (16, 147), (32, 135), (48, 123), (64, 109),
              (80, 93), (96, 77), (112, 50)]
RIGHT_SWEEP = [(390, 28), (408, 50), (432, 72), (456, 93), (480, 113),
               (504, 133), (528, 157), (552, 166), (576, 173)]
RIDGE_Y = 23.0
RIDGE_X0, RIDGE_X1 = 120.0, 390.0
GROUND = 242.0
EAVE = 146.0
WALL_L, WALL_R = 34.0, 504.0
DL, DR, DT = 150.0, 382.0, 100.0     # door opening
SPLIT = 268.0


def _slope_at(sweep, t):
    """Point a fraction t along one of the measured roof sweeps."""
    i = min(len(sweep) - 2, int(t * (len(sweep) - 1)))
    u = t * (len(sweep) - 1) - i
    (x0, y0), (x1, y1) = sweep[i], sweep[i + 1]
    return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u


def barn():
    g = []

    def L(d, w=1.5, o=1.0):
        g.append(f'<path d="{d}" fill="none" stroke="{PENCIL}" stroke-width="{f(w)}" '
                 f'stroke-linecap="round" stroke-linejoin="round" opacity="{f(o)}"/>')

    def tone(pts, o):
        d = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + " Z"
        g.append(f'<path d="{d}" fill="{PENCIL}" opacity="{f(o)}" stroke="none"/>')

    # --- graphite tone, laid in before the linework so the barn reads as a
    #     solid building rather than an outline ------------------------------
    tone(LEFT_SWEEP + [(112, 50), (112, EAVE - 4), (14, EAVE + 3), (0, 153)], 0.075)
    tone([(RIDGE_X0, RIDGE_Y), (RIDGE_X1, RIDGE_Y + 5), (400, EAVE - 2),
          (112, EAVE - 4), (112, 50)], 0.055)
    tone([(RIDGE_X1, RIDGE_Y + 5)] + RIGHT_SWEEP[1:] + [(536, EAVE + 4), (400, EAVE - 2)], 0.10)
    tone([(WALL_L, EAVE), (DL, EAVE), (DL, GROUND), (WALL_L, GROUND)], 0.05)
    tone([(DR, EAVE), (WALL_R, EAVE), (WALL_R, GROUND), (DR, GROUND)], 0.07)
    tone([(DL, DT + 22), (DR, DT + 22), (DR, GROUND), (DL, GROUND)], 0.085)
    # the dark line of shade the roof throws along the eaves
    tone([(14, EAVE + 3), (536, EAVE + 4), (536, EAVE + 11), (14, EAVE + 10)], 0.16)
    # the low outer bays sit in shade
    tone([(0, 153), (14, EAVE + 3), (WALL_L, EAVE), (WALL_L, GROUND), (4, GROUND)], 0.05)
    tone([(536, EAVE + 4), (576, 173), (572, GROUND), (WALL_R, GROUND), (WALL_R, EAVE)], 0.06)

    # --- the roof ----------------------------------------------------------
    L(smooth_path(LEFT_SWEEP), 1.8)
    L(f"M112,50 L{f(RIDGE_X0)},{RIDGE_Y}", 1.6)                  # the step up
    L(f"M{f(RIDGE_X0)},{RIDGE_Y} L292,{RIDGE_Y + 1} L{f(RIDGE_X1)},{RIDGE_Y + 5}", 1.8)
    L(smooth_path(RIGHT_SWEEP), 1.8)

    # eaves, carried across the front under the raised centre
    L(f"M14,{f(EAVE + 3)} L{f(WALL_L - 4)},{f(EAVE)} L{f(WALL_R + 6)},{f(EAVE - 1)} "
      f"L536,{f(EAVE + 4)}", 1.6)
    # the raised centre's own eaves and its left gable
    L(f"M112,52 L112,{f(EAVE - 4)}", 1.1, 0.7)
    L(f"M{f(RIDGE_X1)},{f(RIDGE_Y + 5)} L400,{f(EAVE - 2)}", 1.1, 0.6)
    # deep shadow band under the centre roof, y 100-121 in the original
    for i in range(5):
        y = DT + 2 + i * 4.6
        L(f"M{f(DL - 10 + i)},{f(y)} L{f(DR + 26 - i)},{f(y + 1)}", 1.5, 0.30)

    # roof courses, following each measured sweep
    for k in range(14):
        t = 0.06 + k * 0.069
        x0, y0 = _slope_at(LEFT_SWEEP, t)
        L(f"M{f(x0 + 2)},{f(y0 + 4)} L{f(x0 + 12)},{f(EAVE - 3)}", 0.5, 0.30)
        x1, y1 = _slope_at(RIGHT_SWEEP, t)
        L(f"M{f(x1 - 2)},{f(y1 + 4)} L{f(x1 - 12)},{f(EAVE - 3)}", 0.5, 0.30)
    # horizontal tile courses across all three roof planes
    for i in range(11):
        y = 32 + i * 10.4
        inset = 6 + i * 1.6
        L(f"M{f(RIDGE_X0 + inset)},{f(y)} L{f(RIDGE_X1 - inset * 0.7)},{f(y + 2)}", 0.5, 0.26)
    for i in range(9):
        u = (i + 1) / 10.0
        xl, yl = _slope_at(LEFT_SWEEP, 1.0 - u)
        L(f"M{f(xl)},{f(yl + 4)} L{f(xl + 9 + u * 6)},{f(yl + 6 + u * 3)}", 0.45, 0.22)
        xr, yr = _slope_at(RIGHT_SWEEP, u)
        L(f"M{f(xr)},{f(yr + 4)} L{f(xr - 9 - u * 6)},{f(yr + 6 + u * 3)}", 0.45, 0.22)

    # --- walls -------------------------------------------------------------
    L(f"M{f(WALL_L)},{f(EAVE + 2)} L{f(WALL_L)},{GROUND}", 1.4)
    L(f"M{f(WALL_R)},{f(EAVE + 2)} L{f(WALL_R)},{GROUND}", 1.4)
    L(f"M6,{GROUND} L570,{GROUND}", 1.5)
    # the low outer bays, where the cat-slide comes down past the eaves
    L(f"M4,{f(EAVE + 8)} L4,{f(GROUND - 2)}", 1.1, 0.7)
    L(f"M552,{f(EAVE + 22)} L552,{f(GROUND - 2)}", 1.1, 0.7)
    L(f"M572,{f(EAVE + 30)} L572,{f(GROUND - 2)}", 1.0, 0.55)

    # --- doors -------------------------------------------------------------
    L(f"M{f(DL)},{GROUND} L{f(DL)},{f(DT + 22)} L{f(DR)},{f(DT + 22)} L{f(DR)},{GROUND}", 1.6)
    L(f"M{f(SPLIT)},{f(DT + 22)} L{f(SPLIT)},{GROUND}", 1.3)
    x = DL + 7
    while x < DR - 4:
        if abs(x - SPLIT) > 5:
            L(f"M{f(x)},{f(DT + 27)} L{f(x)},{f(GROUND - 1)}", 0.5, 0.30)
        x += 10.5
    # braces, each leaf from its outer foot up to the meeting stiles
    L(f"M{f(DL + 5)},{f(GROUND - 5)} L{f(SPLIT - 5)},{f(DT + 44)}", 1.2, 0.85)
    L(f"M{f(DR - 5)},{f(GROUND - 5)} L{f(SPLIT + 5)},{f(DT + 44)}", 1.2, 0.85)
    for y in (DT + 40, GROUND - 38):
        L(f"M{f(DL + 3)},{f(y)} L{f(SPLIT - 3)},{f(y)}", 0.85, 0.5)
        L(f"M{f(SPLIT + 3)},{f(y)} L{f(DR - 3)},{f(y)}", 0.85, 0.5)

    # --- weatherboarding, either side of the doors -------------------------
    y = EAVE + 8
    while y < GROUND - 3:
        L(f"M{f(WALL_L + 3)},{f(y)} L{f(DL - 3)},{f(y - 1)}", 0.55, 0.34)
        L(f"M{f(DR + 3)},{f(y - 1)} L{f(WALL_R - 3)},{f(y)}", 0.55, 0.34)
        y += 9.0

    g.append(bicycle(cx=SPLIT + 4, ground=GROUND))

    # --- grass along the foot ----------------------------------------------
    rnd = random.Random(11)
    x = 4.0
    while x < 572:
        if 208 < x < 330:        # the bicycle stands here
            x += 7
            continue
        hgt = rnd.uniform(4, 12)
        lean = rnd.uniform(-3.5, 3.5)
        L(f"M{f(x)},{GROUND} Q{f(x + lean * 0.5)},{f(GROUND - hgt * 0.6)} "
          f"{f(x + lean)},{f(GROUND - hgt)}", 0.7, rnd.uniform(0.3, 0.68))
        x += rnd.uniform(4.0, 8.0)

    return '<g id="barn">' + "".join(g) + "</g>"


def bicycle(cx, ground):
    """A step-through frame, seen side-on, propped against the doors."""
    g = []
    R = 20.5
    cy = ground - R + 1
    rear_x, front_x = cx - 43, cx + 43

    def L(d, w=1.4, o=1.0):
        g.append(f'<path d="{d}" fill="none" stroke="{PENCIL}" stroke-width="{f(w)}" '
                 f'stroke-linecap="round" opacity="{f(o)}"/>')

    # wheels, with a few spokes each
    for wx in (rear_x, front_x):
        g.append(f'<circle cx="{f(wx)}" cy="{f(cy)}" r="{f(R)}" fill="none" '
                 f'stroke="{PENCIL}" stroke-width="1.6"/>')
        g.append(f'<circle cx="{f(wx)}" cy="{f(cy)}" r="{f(R - 4.5)}" fill="none" '
                 f'stroke="{PENCIL}" stroke-width="0.6" opacity="0.5"/>')
        for k in range(8):
            a = math.radians(k * 45 + 11)
            g.append(f'<line x1="{f(wx)}" y1="{f(cy)}" x2="{f(wx + math.cos(a) * (R - 2))}" '
                     f'y2="{f(cy + math.sin(a) * (R - 2))}" stroke="{PENCIL}" '
                     f'stroke-width="0.45" opacity="0.4"/>')
        g.append(f'<circle cx="{f(wx)}" cy="{f(cy)}" r="1.5" fill="{PENCIL}" opacity="0.7"/>')

    bb_x, bb_y = cx - 5, cy - 3            # bottom bracket
    seat_x, seat_y = cx - 22, cy - 40      # top of seat tube
    head_x, head_y = cx + 27, cy - 36      # top of head tube

    L(f"M{f(rear_x)},{f(cy)} L{f(bb_x)},{f(bb_y)}", 1.3)            # chainstay
    L(f"M{f(rear_x)},{f(cy)} L{f(seat_x)},{f(seat_y)}", 1.3)        # seat stay
    L(f"M{f(bb_x)},{f(bb_y)} L{f(seat_x)},{f(seat_y)}", 1.3)        # seat tube
    # step-through down tube, curved
    L(f"M{f(bb_x)},{f(bb_y)} Q{f(cx + 6)},{f(cy - 26)} {f(head_x)},{f(head_y)}", 1.3)
    L(f"M{f(seat_x)},{f(seat_y)} Q{f(cx + 3)},{f(cy - 44)} {f(head_x)},{f(head_y - 2)}", 1.1, 0.9)
    L(f"M{f(head_x)},{f(head_y)} L{f(front_x)},{f(cy)}", 1.3)       # fork

    # saddle
    L(f"M{f(seat_x - 7)},{f(seat_y - 4)} Q{f(seat_x)},{f(seat_y - 7)} "
      f"{f(seat_x + 7)},{f(seat_y - 3)}", 2.1)
    # handlebars, swept back
    L(f"M{f(head_x)},{f(head_y)} L{f(head_x + 1)},{f(head_y - 9)}", 1.2)
    L(f"M{f(head_x - 9)},{f(head_y - 11)} Q{f(head_x + 2)},{f(head_y - 13)} "
      f"{f(head_x + 8)},{f(head_y - 8)}", 1.6)
    # basket on the front
    L(f"M{f(head_x - 1)},{f(head_y - 9)} l-9,1 l1,9 l10,-1 z", 1.1, 0.85)
    for k in range(3):
        L(f"M{f(head_x - 9 + k * 3)},{f(head_y - 8)} l0.6,8.5", 0.5, 0.45)
    # chainring and pedal
    g.append(f'<circle cx="{f(bb_x)}" cy="{f(bb_y)}" r="6.5" fill="none" '
             f'stroke="{PENCIL}" stroke-width="0.8" opacity="0.8"/>')
    L(f"M{f(bb_x)},{f(bb_y)} l6,4 M{f(bb_x + 6)},{f(bb_y + 4)} l4.5,0", 1.0, 0.85)
    return '<g id="bicycle">' + "".join(g) + "</g>"


# ===========================================================================
# THE FLORAL FRAME
# Everything hangs off one ellipse. Stems sweep along it from the bottom
# upward on both sides, and each carries a head: a bloom, a bud, a seed
# sprig, leaves or a dark fern.
# ===========================================================================

CX, CY = 500.0, 790.0
RX, RY = 386.0, 600.0


def on_ellipse(theta_deg, r=1.0):
    """
    A point on the wreath. The oval is pinched toward the top so the two arcs
    lean in above the barn, the way Lucy's columns converge there.
    """
    a = math.radians(theta_deg)
    lean = (1.0 - math.sin(a)) * 0.5            # 0 at the bottom, 1 at the top
    rx = RX * (1.0 - 0.20 * lean ** 1.5)
    # a slow irregular swell, so the wreath bulges and thins the way a hand
    # drawn one does instead of sitting on a perfect oval
    swell = 1.0 + 0.05 * math.sin(2.3 * a + 1.1) + 0.032 * math.sin(3.7 * a + 2.4)
    return CX + rx * r * swell * math.cos(a), CY + RY * r * swell * math.sin(a)


def petal_path(length, width):
    """One broad, round-tipped petal pointing up from the origin."""
    lw, ll = width, length
    return (
        f"M0,0 C{f(0.46 * lw)},{f(-0.14 * ll)} {f(0.62 * lw)},{f(-0.58 * ll)} "
        f"{f(0.29 * lw)},{f(-0.91 * ll)} C{f(0.13 * lw)},{f(-1.02 * ll)} "
        f"{f(-0.13 * lw)},{f(-1.02 * ll)} {f(-0.29 * lw)},{f(-0.91 * ll)} "
        f"C{f(-0.62 * lw)},{f(-0.58 * ll)} {f(-0.46 * lw)},{f(-0.14 * ll)} 0,0 Z"
    )


def bloom(x, y, radius, palette, rnd, petals=5, spin=None):
    grad = {ROSE: "gRose", CORAL: "gCoral", BLUSH: "gBlush", BLUE: "gBlue"}[palette]
    spin = rnd.uniform(0, 72) if spin is None else spin
    out = [f'<g transform="translate({f(x)},{f(y)}) rotate({f(spin)})">']
    for i in range(petals):
        a = i * (360.0 / petals) + rnd.uniform(-7, 7)
        ln = radius * rnd.uniform(0.88, 1.12)
        wd = radius * rnd.uniform(0.80, 1.00)
        out.append(
            f'<path d="{petal_path(ln, wd)}" fill="url(#{grad})" '
            f'opacity="{f(rnd.uniform(0.52, 0.74))}" transform="rotate({f(a)})"/>'
        )
    # centre: a soft disc with a few seed specks
    out.append(f'<circle r="{f(radius * 0.23)}" fill="{CENTRE}" opacity="0.5"/>')
    out.append(f'<circle r="{f(radius * 0.12)}" fill="{CENTRE_DEEP}" opacity="0.62"/>')
    for _ in range(rnd.randint(3, 5)):
        a = rnd.uniform(0, 360)
        d = radius * rnd.uniform(0.18, 0.34)
        px, py = rot(d, 0, a)
        out.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="{f(radius * 0.05)}" '
                   f'fill="{CENTRE_DEEP}" opacity="0.5"/>')
    out.append("</g>")
    return "".join(out)


def bud(x, y, angle, length, rnd):
    """A soft tapered bud, the pale pink capsules dotted round her frame."""
    wd = length * rnd.uniform(0.24, 0.32)
    d = (f"M0,0 C{f(wd * 0.62)},{f(-length * 0.22)} {f(wd * 0.52)},{f(-length * 0.74)} "
         f"0,{f(-length)} C{f(-wd * 0.52)},{f(-length * 0.74)} "
         f"{f(-wd * 0.62)},{f(-length * 0.22)} 0,0 Z")
    return (f'<path d="{d}" fill="url(#gBlush)" opacity="{f(rnd.uniform(0.6, 0.8))}" '
            f'transform="translate({f(x)},{f(y)}) rotate({f(angle)})"/>')


def leaf(x, y, angle, length, rnd, palette=LEAF):
    grad = "gLeaf" if palette is LEAF else "gPod"
    wd = length * rnd.uniform(0.30, 0.40)
    d = (f"M0,0 C{f(wd * 0.55)},{f(-length * 0.26)} {f(wd * 0.48)},{f(-length * 0.72)} "
         f"0,{f(-length)} C{f(-wd * 0.48)},{f(-length * 0.72)} "
         f"{f(-wd * 0.55)},{f(-length * 0.26)} 0,0 Z")
    return (f'<path d="{d}" fill="url(#{grad})" opacity="{f(rnd.uniform(0.55, 0.8))}" '
            f'transform="translate({f(x)},{f(y)}) rotate({f(angle)})"/>')


def leaf_sprig(pts, rnd, n=6, size=14.0):
    """Almond leaves in opposite pairs up the last stretch of a stem."""
    out = []
    m = len(pts)
    for i in range(n):
        t = 0.10 + 0.88 * (i / max(1, n - 1.0))
        k = min(m - 2, int(t * (m - 1)))
        px, py = pts[k]
        dx, dy = pts[k + 1][0] - px, pts[k + 1][1] - py
        base = math.degrees(math.atan2(dy, dx)) + 90
        taper = size * (1.0 - 0.45 * t)
        for side in (-1, 1):
            out.append(leaf(px, py, base + side * rnd.uniform(28, 46),
                            taper * rnd.uniform(0.82, 1.15), rnd))
    return "".join(out)


def seed_sprig(pts, rnd, n=9):
    """Tiny pods alternating along the stem — her dried grass heads."""
    out = []
    m = len(pts)
    for i in range(n):
        t = 0.12 + 0.86 * (i / max(1, n - 1.0))
        k = min(m - 2, int(t * (m - 1)))
        px, py = pts[k]
        dx, dy = pts[k + 1][0] - px, pts[k + 1][1] - py
        base = math.degrees(math.atan2(dy, dx)) + 90
        side = -1 if i % 2 else 1
        out.append(leaf(px, py, base + side * rnd.uniform(38, 62),
                        rnd.uniform(5.5, 9.0), rnd, palette=POD))
    return "".join(out)


def fern_sprig(pts, rnd, n=11):
    """The dark olive fern: minute paired leaflets, the frame's deepest note."""
    out = []
    m = len(pts)
    for i in range(n):
        t = 0.10 + 0.88 * (i / max(1, n - 1.0))
        k = min(m - 2, int(t * (m - 1)))
        px, py = pts[k]
        dx, dy = pts[k + 1][0] - px, pts[k + 1][1] - py
        base = math.degrees(math.atan2(dy, dx)) + 90
        ln = 7.5 * (1.0 - 0.5 * t)
        for side in (-1, 1):
            a = math.radians(base + side * 52)
            out.append(
                f'<path d="M{f(px)},{f(py)} l{f(math.cos(a) * ln)},{f(math.sin(a) * ln)}" '
                f'stroke="{FERN}" stroke-width="1.5" stroke-linecap="round" '
                f'opacity="{f(rnd.uniform(0.5, 0.78))}" fill="none"/>'
            )
    return "".join(out)


def stem_points(t0, t1, r0, r1, wobble, rnd, n=16):
    """Sample a stem sweeping along the ellipse from t0 to t1."""
    pts = []
    for i in range(n):
        u = i / (n - 1.0)
        th = t0 + (t1 - t0) * u
        r = r0 + (r1 - r0) * u
        r += wobble * math.sin(u * math.pi * rnd.uniform(0.8, 1.6)) * 0.055
        pts.append(on_ellipse(th, r))
    return pts


def density(theta):
    """
    How thick the planting is at a given angle. Heaviest at the foot, easing
    off toward the top where Lucy leaves the card open.
    """
    a = math.radians(theta)
    return 0.34 + 0.66 * (0.5 + 0.5 * math.sin(a)) ** 0.8


def frame():
    rnd = random.Random(20270605)
    stems, foliage, flowers = [], [], []

    def add_stem(t0, t1, r0, r1, weight, wob=0.7):
        pts = stem_points(t0, t1, r0, r1, rnd.uniform(-wob, wob), rnd)
        stems.append(
            f'<path d="{smooth_path(pts)}" fill="none" stroke="{STEM}" '
            f'stroke-width="{f(weight)}" stroke-linecap="round" '
            f'opacity="{f(rnd.uniform(0.45, 0.8))}"/>'
        )
        return pts

    # -----------------------------------------------------------------------
    # 1. The foliage mass. Short sprigs of leaves and seed pods packed round
    #    the oval — in her card this is the bulk of the drawing, with the
    #    flowers sitting on top of it.
    # -----------------------------------------------------------------------
    for side in (+1, -1):
        theta = 90.0
        limit = 236.0 if side > 0 else -56.0
        while (theta < limit) if side > 0 else (theta > limit):
            d = density(theta)
            if rnd.random() < 0.34 + 0.52 * d:
                span = rnd.uniform(10, 28)
                r0 = rnd.uniform(0.92, 1.03)
                r1 = r0 + rnd.uniform(-0.12, 0.16)
                pts = add_stem(theta, theta + side * span, r0, r1,
                               rnd.uniform(0.6, 1.3), wob=0.5)
                roll = rnd.random()
                if roll < 0.46:
                    foliage.append(leaf_sprig(pts, rnd, n=rnd.randint(5, 10),
                                              size=rnd.uniform(12, 21)))
                elif roll < 0.80:
                    foliage.append(seed_sprig(pts, rnd, n=rnd.randint(7, 13)))
                else:
                    foliage.append(fern_sprig(pts, rnd, n=rnd.randint(9, 14)))
                # a tapered bud riding on some of the foliage stems
                if rnd.random() < 0.3:
                    tip = pts[-1]
                    ang = math.degrees(math.atan2(tip[1] - pts[-2][1],
                                                  tip[0] - pts[-2][0])) + 90
                    foliage.append(bud(tip[0], tip[1], ang + 180 + rnd.uniform(-18, 18),
                                       rnd.uniform(26, 44), rnd))
            theta += side * rnd.uniform(2.8, 5.4)

    # -----------------------------------------------------------------------
    # 2. The reaching sprigs: longer stems that carry the frame upward and
    #    give the top of the card its thin, airy finish.
    # -----------------------------------------------------------------------
    for side in (+1, -1):
        for i in range(11):
            start = 90.0 + side * (10.0 + i * 12.5 + rnd.uniform(-4, 4))
            span = rnd.uniform(26, 46)
            end = start + side * span
            if side > 0:
                end = min(end, 234.0)
            else:
                end = max(end, -54.0)
            pts = add_stem(start, end, rnd.uniform(0.95, 1.03),
                           rnd.uniform(0.86, 1.14), rnd.uniform(0.8, 1.6), wob=0.6)
            if rnd.random() < 0.6:
                foliage.append(leaf_sprig(pts, rnd, n=rnd.randint(3, 6),
                                          size=rnd.uniform(8, 13)))
            else:
                foliage.append(seed_sprig(pts, rnd, n=rnd.randint(5, 9)))
            # a bud or small bloom right at the tip
            tip = pts[-1]
            ang = math.degrees(math.atan2(tip[1] - pts[-2][1], tip[0] - pts[-2][0])) + 90
            if rnd.random() < 0.55:
                foliage.append(bud(tip[0], tip[1], ang + 180 + rnd.uniform(-16, 16),
                                   rnd.uniform(30, 48), rnd))
            else:
                flowers.append(bloom(tip[0], tip[1], rnd.uniform(8, 15),
                                     rnd.choice([ROSE, BLUSH, BLUE]), rnd))

    # -----------------------------------------------------------------------
    # 3. The flowers, placed round the oval rather than one per stem, so they
    #    read as scattered through the planting the way hers do.
    # -----------------------------------------------------------------------
    MIX = ([ROSE] * 11 + [BLUE] * 8 + [BLUSH] * 5 + [CORAL] * 3)
    for side in (+1, -1):
        theta = 90.0
        limit = 232.0 if side > 0 else -52.0
        while (theta < limit) if side > 0 else (theta > limit):
            d = density(theta)
            pal = rnd.choice(MIX)
            r = rnd.uniform(0.86, 1.12)
            x, y = on_ellipse(theta + rnd.uniform(-5, 5), r)
            size = {id(ROSE): (13, 24), id(BLUE): (9, 16),
                    id(BLUSH): (10, 18), id(CORAL): (15, 25)}[id(pal)]
            # a wide scatter of scales: a few large blooms carry the frame,
            # plenty of small ones fill between them
            scale = rnd.choice([0.55, 0.7, 0.85, 1.0, 1.0, 1.15])
            flowers.append(bloom(x, y, rnd.uniform(*size) * scale * (0.85 + 0.26 * d),
                                 pal, rnd))
            # an occasional pair, the way blooms cluster on one stem
            if rnd.random() < 0.38:
                x2, y2 = on_ellipse(theta + side * rnd.uniform(2, 7),
                                    r + rnd.uniform(-0.09, 0.09))
                flowers.append(bloom(x2, y2, rnd.uniform(*size) * scale * 0.68, pal, rnd))
            theta += side * rnd.uniform(6.0, 19.0) / (0.5 + d)

    # -----------------------------------------------------------------------
    # 4. The coral cluster gathered at the foot of the card
    # -----------------------------------------------------------------------
    cluster, feed = [], []
    for i in range(9):
        x = 398 + i * 26 + rnd.uniform(-8, 8)
        feed.append(
            f'<path d="M{f(x)},{f(H + 10)} Q{f(x + rnd.uniform(-14, 14))},1392 '
            f'{f(x + rnd.uniform(-24, 24))},{f(rnd.uniform(1330, 1352))}" fill="none" '
            f'stroke="{STEM}" stroke-width="{f(rnd.uniform(0.8, 1.5))}" '
            f'opacity="0.55" stroke-linecap="round"/>'
        )
    for i in range(6):
        u = i / 5.0
        x = 404 + u * 192 + rnd.uniform(-10, 10)
        y = 1356 - math.sin(u * math.pi) * 14 + rnd.uniform(-8, 8)
        cluster.append(bloom(x, y, rnd.uniform(24, 31), CORAL, rnd))
    for i in range(9):
        x = 352 + rnd.uniform(0, 296)
        y = 1372 + rnd.uniform(-10, 14)
        cluster.append(bloom(x, y, rnd.uniform(13, 20),
                             rnd.choice([BLUSH, BLUSH, CORAL]), rnd))

    return ('<g id="frame" filter="url(#wc)">'
            + "".join(stems) + "".join(feed) + "".join(foliage)
            + "".join(flowers) + "".join(cluster) + "</g>")


# ===========================================================================
# DEFS: gradients, the watercolour filter, the paper grain, embedded fonts
# ===========================================================================

def radial(gid, inner, outer):
    return (f'<radialGradient id="{gid}" cx="42%" cy="78%" r="82%">'
            f'<stop offset="0%" stop-color="{inner}"/>'
            f'<stop offset="62%" stop-color="{inner}" stop-opacity="0.82"/>'
            f'<stop offset="100%" stop-color="{outer}"/></radialGradient>')


def font_faces():
    p = os.path.join(HERE, "fonts.json")
    if not os.path.exists(p):
        return ""
    data = json.load(open(p))
    css = []
    for key, b64 in data.items():
        fam, wt = key.split("|")
        weight = "300 400" if fam == "Cormorant Garamond" else wt
        css.append(
            f"@font-face{{font-family:'{fam}';font-style:normal;"
            f"font-weight:{weight};src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )
    return "".join(css)


def defs(with_fonts=True):
    grads = (radial("gRose", *ROSE) + radial("gCoral", *CORAL) +
             radial("gBlush", *BLUSH) + radial("gBlue", *BLUE) +
             radial("gLeaf", *LEAF) + radial("gPod", *POD))
    # Watercolour: warp the edges with low-frequency noise, then soften them.
    wc = (
        '<filter id="wc" x="-8%" y="-8%" width="116%" height="116%" '
        'color-interpolation-filters="sRGB">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.028" numOctaves="3" '
        'seed="7" result="n"/>'
        '<feDisplacementMap in="SourceGraphic" in2="n" scale="4.2" '
        'xChannelSelector="R" yChannelSelector="G" result="d"/>'
        '<feGaussianBlur in="d" stdDeviation="0.55"/>'
        "</filter>"
    )
    # Paper: a faint warm tooth over the whole card.
    grain = (
        '<filter id="grain" x="0" y="0" width="100%" height="100%" '
        'color-interpolation-filters="sRGB">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.72 0.14" '
        'numOctaves="4" seed="3" result="t"/>'
        '<feColorMatrix in="t" type="matrix" values="'
        '0 0 0 0 0.55  0 0 0 0 0.52  0 0 0 0 0.46  0 0 0 0.055 0"/>'
        "</filter>"
    )
    style = f"<style>{font_faces()}</style>" if with_fonts else ""
    return "<defs>" + grads + wc + grain + "</defs>" + style


# ===========================================================================
# LETTERING
# ===========================================================================

SERIF = "'Cormorant Garamond', Cormorant, Garamond, 'Times New Roman', serif"
SCRIPT = "'Italianno', 'Snell Roundhand', cursive"


def lettering():
    def t(y, size, tracking, content, family=SERIF, weight=300, fill=LETTER, op=1.0):
        return (f'<text x="{f(W / 2)}" y="{f(y)}" text-anchor="middle" '
                f'font-family="{family}" font-size="{f(size)}" font-weight="{weight}" '
                f'letter-spacing="{f(tracking)}" fill="{fill}" opacity="{f(op)}">{content}</text>')

    g = [
        t(614, 44, 12.5, "SAVE THE DATE"),
        t(731, 108, 9.0, "JACK", weight=300),
        t(786, 76, 0, "and", family=SCRIPT, weight=400, op=0.85),
        t(872, 108, 9.0, "LUCY", weight=300),
        # 5th June 2027, with a raised ordinal as on her card
        f'<text x="{f(W / 2)}" y="925" text-anchor="middle" font-family="{SERIF}" '
        f'font-size="42" font-weight="300" letter-spacing="7" fill="{LETTER}">'
        f'5<tspan font-size="24" dy="-14">TH</tspan><tspan dy="14"> JUNE 2027</tspan></text>',
        t(996, 27, 11.0, "SUSSEX", op=0.82),
        t(1098, 62, 0, "formal invitation to follow", family=SCRIPT, weight=400, op=0.8),
    ]
    return '<g id="lettering">' + "".join(g) + "</g>"


# ===========================================================================
# ASSEMBLY
# ===========================================================================

def build(with_type=True, with_paper=True, with_barn=True):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(W)} {f(H)}" '
        f'width="{f(W)}" height="{f(H)}">',
        defs(with_fonts=with_type),
    ]
    if with_paper:
        parts.append(f'<rect width="{f(W)}" height="{f(H)}" fill="{PAPER}"/>')
        parts.append(f'<rect width="{f(W)}" height="{f(H)}" filter="url(#grain)" '
                     f'style="mix-blend-mode:multiply"/>')
    if with_barn:
        parts.append(f'<g transform="translate(263,291) scale(0.845)">{barn()}</g>')
    parts.append(frame())
    if with_type:
        parts.append(lettering())
    parts.append("</svg>")
    return "".join(parts)


def build_barn_only():
    """Just the barn, on a transparent ground, at its own aspect ratio."""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 274" '
            'width="576" height="274">' + barn() + "</svg>")


def build_frame_half(side):
    """One column of the wreath, cropped tight, for the page edges."""
    box = "0 0 300 1414" if side == "left" else "700 0 300 1414"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{box}" '
            f'width="300" height="1414">' + defs(False) + frame() + "</svg>")


def build_spray():
    """The coral cluster at the foot, cropped out on its own."""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="318 1286 364 128" '
            'width="364" height="128">' + defs(False) + frame() + "</svg>")


TARGETS = {
    "card":        ("save-the-date.svg", lambda: build()),
    "card-blank":  ("card-blank.svg",    lambda: build(with_type=False)),
    "frame":       ("floral-frame.svg",  lambda: build(with_type=False, with_paper=False,
                                                       with_barn=False)),
    "frame-left":  ("floral-left.svg",   lambda: build_frame_half("left")),
    "frame-right": ("floral-right.svg",  lambda: build_frame_half("right")),
    "barn":        ("barn.svg",          build_barn_only),
    "spray":       ("floral-spray.svg",  build_spray),
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", default="all", choices=list(TARGETS) + ["all"])
    ap.add_argument("--no-type", action="store_true", help="alias for card-blank")
    ap.add_argument("--frame-only", action="store_true", help="alias for frame")
    ap.add_argument("-o", "--out", default=None)
    a = ap.parse_args()

    if a.frame_only:
        keys = ["frame"]
    elif a.no_type:
        keys = ["card-blank"]
    elif a.target == "all":
        keys = list(TARGETS)
    else:
        keys = [a.target]

    for k in keys:
        name, fn = TARGETS[k]
        out = a.out if (a.out and len(keys) == 1) else os.path.join(HERE, name)
        svg = fn()
        with open(out, "w") as fh:
            fh.write(svg)
        print(f"{out}  {len(svg) / 1024:.0f} KB")
