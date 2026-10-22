"""Write assets/claws.svg: a tile of claw-mark scratches (groups of 3 or 4 tapered slashes) in the BairView red.
Run: python3 make_claws.py   (fixed seed, so the pattern does not change between runs)"""
import math
import random

RED = "#800E13"  # from the Drive palette image
W, H = 1000, 1500
rnd = random.Random(417)

# group origins spread across the tile so any phone-width strip of it holds a few marks
ORIGINS = [(60, 80), (870, 160), (640, 640), (110, 1010), (790, 1020), (430, 1330)]


def slash(x, y, ang, length, wmax, bend):
    """Polygon for one scratch: sharp at the start, widest near the start, tapering to a point."""
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx
    n = 28
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        bx = x + dx * length * t + nx * bend * math.sin(math.pi * t)
        by = y + dy * length * t + ny * bend * math.sin(math.pi * t)
        w = wmax * min(1, t * 7) * (1 - t) ** 0.7
        left.append((bx + nx * w, by + ny * w))
        right.append((bx - nx * w, by - ny * w))
    pts = left + right[::-1]
    return "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts) + "Z"


paths = []
for ox, oy in ORIGINS:
    base = math.radians(rnd.uniform(50, 78))        # slanted down to the right
    if rnd.random() < 0.35:
        base = math.pi - base                         # a few lean the other way
    count = rnd.choice((3, 3, 4))
    gap = rnd.uniform(15, 24)
    length = rnd.uniform(230, 400)
    bend = rnd.uniform(-14, 14)
    nx, ny = -math.sin(base), math.cos(base)
    for k in range(count):
        off = (k - (count - 1) / 2) * gap
        paths.append(slash(
            ox + nx * off + rnd.uniform(-4, 4), oy + ny * off + rnd.uniform(-6, 6),
            base + math.radians(rnd.uniform(-2.5, 2.5)),
            length * rnd.uniform(0.78, 1.0), rnd.uniform(2.2, 3.4), bend * rnd.uniform(0.7, 1.2)))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<path fill="{RED}" d="{" ".join(paths)}"/>\n</svg>\n')
open("assets/claws.svg", "w").write(svg)
print(len(paths), "scratches,", len(svg), "bytes")
