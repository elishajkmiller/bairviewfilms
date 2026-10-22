"""Geometry of the BairView paw print, drawn in the bear logo's language: straight edges, chamfered corners, a notch
in the top of the pad (like the notch in the bear's head). Upright, toes up, left paw; 400 x 440 units.
Shared by make_paws.py (SVG for the site) and make_paw_psd.py (layered PSD)."""
import math

RED = "#850026"  # the red of assets/bear.png (the logo file), not the palette-image red 800E13
W, H = 400, 440

PAD = [(200, 222), (262, 206), (318, 262), (302, 340), (252, 392), (200, 410), (148, 392), (98, 340), (82, 262), (138, 206)]
# (center x, center y, angle in degrees from straight up, width, height)
TOES = [(52, 214, -34, 50, 76), (118, 130, -16, 58, 86), (200, 100, 0, 62, 92), (282, 130, 16, 58, 86), (348, 214, 34, 50, 76)]


def rot(x, y, deg):
    a = math.radians(deg)
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


def toe(cx, cy, ang, w, h):
    local = [(-w / 2, -h * 0.12), (-w * 0.32, -h / 2), (w * 0.32, -h / 2), (w / 2, -h * 0.12),
             (w * 0.42, h * 0.32), (0, h / 2), (-w * 0.42, h * 0.32)]
    return [(cx + rot(x, y, ang)[0], cy + rot(x, y, ang)[1]) for x, y in local]


def claw(cx, cy, ang, w, h):
    """Small sharp triangle above a toe, pointing away from the pad."""
    local = [(-w * 0.2, -h / 2 - 9), (0, -h / 2 - 38), (w * 0.2, -h / 2 - 9)]
    return [(cx + rot(x, y, ang)[0], cy + rot(x, y, ang)[1]) for x, y in local]


def shapes(with_claws=True):
    """[(name, polygon)] from back to front."""
    out = [("Pad", PAD)]
    out += [(f"Toe {i + 1}", toe(*t)) for i, t in enumerate(TOES)]
    if with_claws:
        out += [(f"Claw {i + 1}", claw(*t)) for i, t in enumerate(TOES)]
    return out


def mirrored(poly):
    return [(W - x, y) for x, y in poly]


def d(poly):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in poly) + "Z"
