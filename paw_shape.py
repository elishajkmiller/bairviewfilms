"""Geometry of the BairView paw print, in the bear logo's language: straight edges and sharp facets. A wide faceted pad
cut by two claw slashes, five blade-shaped toes fanned over it, and a long curved claw mark above each toe.
Upright, toes up, left paw. Shared by make_paws.py (SVG for the site), make_paw_psd.py and make_paw_png.py.
W, H are measured from the drawing, with a margin."""
import math

RED = "#850026"  # the red of assets/bear.png (the logo file), not the palette-image red 800E13
MARGIN = 10


def rot(x, y, deg):
    a = math.radians(deg)
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


# wide shield pad: crest on top, chamfered sides, point at the bottom (like the bear's head outline turned over)
PAD = [(200, 176), (302, 214), (336, 304), (270, 378), (200, 424), (130, 378), (64, 304), (98, 214)]
# claw slashes through the pad: two parallel cuts, leaning like "/"
SLIT_ANGLE = 17    # degrees from vertical
SLIT_AT = (-36, 36)  # offsets of the two cuts from the pad centre, across the cut direction
SLIT_GAP = 9

# (center x, center y, angle from straight up, width, height)
TOES = [(40, 216, -36, 50, 90), (115, 124, -16, 58, 104), (200, 94, 0, 62, 110), (285, 124, 16, 58, 104), (360, 216, 36, 50, 90)]


def clip(poly, nx, ny, c, keep_ge):
    """Keep the part of a convex polygon where nx*x + ny*y >= c (or <= c)."""
    sgn = 1 if keep_ge else -1
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        dp = sgn * (nx * p[0] + ny * p[1] - c)
        dq = sgn * (nx * q[0] + ny * q[1] - c)
        if dp >= 0:
            out.append(p)
        if (dp >= 0) != (dq >= 0):
            t = dp / (dp - dq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def pad_pieces():
    a = math.radians(SLIT_ANGLE)
    nx, ny = math.cos(a), math.sin(a)             # across the cuts
    mid = nx * 200 + ny * 300
    cuts = [mid + o for o in SLIT_AT]
    edges = [-1e9] + [c for c in cuts] + [1e9]
    pieces = []
    for i in range(3):
        poly = PAD
        lo, hi = edges[i], edges[i + 1]
        if i > 0:
            poly = clip(poly, nx, ny, lo + SLIT_GAP / 2, True)
        if i < 2:
            poly = clip(poly, nx, ny, hi - SLIT_GAP / 2, False)
        pieces.append(poly)
    return pieces


def toe(cx, cy, ang, w, h):
    """A blade: sharp tip, slightly wider below it, cut off flat at the base."""
    local = [(-w / 2, h * 0.18), (-w * 0.36, -h * 0.3), (0, -h / 2), (w * 0.36, -h * 0.3), (w / 2, h * 0.18),
             (w * 0.24, h / 2), (-w * 0.24, h / 2)]
    return [(cx + rot(x, y, ang)[0], cy + rot(x, y, ang)[1]) for x, y in local]


def claw(cx, cy, ang, w, h):
    """A long curved slash above the toe, sharp at both ends and widest near its start."""
    n = 18
    base = h / 2 + 9
    length = 54
    bend = 7 if ang >= 0 else -7
    if ang == 0:
        bend = 5
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        lx = bend * math.sin(math.pi * t / 2) ** 2
        ly = -(base + length * t)
        wd = 7.5 * min(1, t * 6) * (1 - t) ** 0.85
        left.append((lx - wd, ly))
        right.append((lx + wd, ly))
    pts = left + right[::-1]
    return [(cx + rot(x, y, ang)[0], cy + rot(x, y, ang)[1]) for x, y in pts]


def _raw(with_claws=True):
    out = [(f"Pad {i + 1}", p) for i, p in enumerate(pad_pieces())]
    out += [(f"Toe {i + 1}", toe(*t)) for i, t in enumerate(TOES)]
    if with_claws:
        out += [(f"Claw {i + 1}", claw(*t)) for i, t in enumerate(TOES)]
    return out


_all = [p for _, poly in _raw(True) for p in poly]
_x0 = min(x for x, _ in _all) - MARGIN
_y0 = min(y for _, y in _all) - MARGIN
W = math.ceil(max(x for x, _ in _all) + MARGIN - _x0)
H = math.ceil(max(y for _, y in _all) + MARGIN - _y0)


def shapes(with_claws=True):
    """[(name, polygon)] from back to front, moved so the drawing sits inside 0..W, 0..H."""
    return [(n, [(x - _x0, y - _y0) for x, y in poly]) for n, poly in _raw(with_claws)]


def mirrored(poly):
    return [(W - x, y) for x, y in poly]


def d(poly):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in poly) + "Z"
