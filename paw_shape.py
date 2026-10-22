"""Geometry of the BairView bear tracks, in the bear logo's language: straight edges and sharp facets.
FRONT print: wide faceted pad cut by two claw slashes, five blade toes, long curved claw marks.
HIND print: longer and narrower: a smaller slashed pad, a short wide heel pad cut by the same slashes, shorter claws.
Upright, toes up, left foot. Shared by make_paws.py (SVG for the site), make_paw_psd.py and make_paw_png.py.
Width and height of each print are measured from the drawing, with a margin."""
import math

RED = "#850026"  # the red of assets/bear.png (the logo file), not the palette-image red 800E13
MARGIN = 10
SLIT_ANGLE = 17    # degrees from vertical: the cuts lean like "/" on a left foot
SLIT_AT = (-36, 36)  # offsets of the two cuts from the pad centre, across the cut direction
SLIT_GAP = 9

# each kind: pad outline, optional heel, toes (center x, center y, angle from straight up, width, height), claw length and width,
# shift = how far the two cuts are moved across the pad (to the right on a left foot)
KINDS = {
    "front": dict(
        pad=[(200, 176), (302, 214), (336, 304), (270, 378), (200, 424), (130, 378), (64, 304), (98, 214)],
        heel=None,
        toes=[(40, 216, -36, 50, 90), (115, 124, -16, 58, 104), (200, 94, 0, 62, 110), (285, 124, 16, 58, 104), (360, 216, 36, 50, 90)],
        claw=(54, 7.5), shift=0),
    "hind": dict(
        pad=[(200, 196), (284, 226), (314, 290), (266, 352), (200, 382), (134, 352), (86, 290), (116, 226)],
        heel=[(126, 392), (274, 392), (292, 430), (266, 486), (200, 508), (134, 486), (108, 430)],
        toes=[(62, 222, -30, 42, 78), (122, 146, -12, 50, 92), (200, 116, 0, 54, 98), (278, 146, 12, 50, 92), (338, 222, 30, 42, 78)],
        claw=(32, 6), shift=18),
}


def rot(x, y, deg):
    a = math.radians(deg)
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


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


def _area(poly):
    return abs(sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(poly, poly[1:] + poly[:1]))) / 2


def pad_pieces(pad, cy=None, shift=0):
    """The pad cut into up to three pieces by two parallel slashes. cy is the height the cuts are centred on, so a
    second piece (the hind heel) can be cut by the same two lines."""
    a = math.radians(SLIT_ANGLE)
    nx, ny = math.cos(a), math.sin(a)             # across the cuts
    if cy is None:
        cy = (min(p[1] for p in pad) + max(p[1] for p in pad)) / 2
    mid = nx * 200 + ny * cy + shift
    edges = [-1e9] + [mid + o for o in SLIT_AT] + [1e9]
    pieces = []
    for i in range(3):
        poly = pad
        if i > 0:
            poly = clip(poly, nx, ny, edges[i] + SLIT_GAP / 2, True)
        if i < 2:
            poly = clip(poly, nx, ny, edges[i + 1] - SLIT_GAP / 2, False)
        if len(poly) >= 3 and _area(poly) > 1:  # keep the small slivers a cut leaves at the edge
            pieces.append(poly)
    return pieces


def toe(cx, cy, ang, w, h):
    """A blade: sharp tip, slightly wider below it, cut off flat at the base."""
    local = [(-w / 2, h * 0.18), (-w * 0.36, -h * 0.3), (0, -h / 2), (w * 0.36, -h * 0.3), (w / 2, h * 0.18),
             (w * 0.24, h / 2), (-w * 0.24, h / 2)]
    return [(cx + rot(x, y, ang)[0], cy + rot(x, y, ang)[1]) for x, y in local]


def claw(cx, cy, ang, w, h, length, width):
    """A curved slash above the toe, sharp at both ends and widest near its start."""
    n = 18
    base = h / 2 + 9
    bend = 5 if ang == 0 else (7 if ang > 0 else -7)
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        lx = bend * math.sin(math.pi * t / 2) ** 2
        ly = -(base + length * t)
        wd = width * min(1, t * 6) * (1 - t) ** 0.85
        left.append((lx - wd, ly))
        right.append((lx + wd, ly))
    pts = left + right[::-1]
    return [(cx + rot(x, y, ang)[0], cy + rot(x, y, ang)[1]) for x, y in pts]


def _raw(kind, with_claws=True):
    k = KINDS[kind]
    cy = (min(p[1] for p in k["pad"]) + max(p[1] for p in k["pad"])) / 2
    out = [(f"Pad {i + 1}", p) for i, p in enumerate(pad_pieces(k["pad"], cy, k["shift"]))]
    if k["heel"]:  # cut by the same two lines as the pad, so the slashes run on through the heel
        out += [(f"Heel {i + 1}", p) for i, p in enumerate(pad_pieces(k["heel"], cy, k["shift"]))]
    out += [(f"Toe {i + 1}", toe(*t)) for i, t in enumerate(k["toes"])]
    if with_claws:
        out += [(f"Claw {i + 1}", claw(*t, *k["claw"])) for i, t in enumerate(k["toes"])]
    return out


_bounds = {}
for _kind in KINDS:
    _pts = [p for _, poly in _raw(_kind) for p in poly]
    _x0 = min(x for x, _ in _pts) - MARGIN
    _y0 = min(y for _, y in _pts) - MARGIN
    _bounds[_kind] = (_x0, _y0, math.ceil(max(x for x, _ in _pts) + MARGIN - _x0), math.ceil(max(y for _, y in _pts) + MARGIN - _y0))


def dims(kind):
    """(width, height) of a print."""
    return _bounds[kind][2], _bounds[kind][3]


def shapes(kind="front", with_claws=True):
    """[(name, polygon)] from back to front, moved so the drawing sits inside 0..W, 0..H."""
    x0, y0 = _bounds[kind][:2]
    return [(n, [(x - x0, y - y0) for x, y in poly]) for n, poly in _raw(kind, with_claws)]


def mirrored(poly, kind="front"):
    return [(dims(kind)[0] - x, y) for x, y in poly]


def d(poly):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in poly) + "Z"
