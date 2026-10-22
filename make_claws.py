"""Write assets/claws.html: the claw marks for the BTS page, one small inline SVG per group of 3 or 4 tapered
slashes in the BairView red. build.py inserts the fragment; style.css animates it (a fixed layer, so only the
small SVGs repaint, not the page). Run: python3 make_claws.py   (fixed seed, the pattern is stable)"""
import math
import random

rnd = random.Random(417)

# (x %, y %) of the viewport for each group; the group's own drawing starts at ox, oy in local units
GROUPS = [(6, 6), (87, 12), (62, 44), (10, 66), (80, 70), (42, 90)]
DELAYS = [0.2 + 0.25 * sorted(g[0] for g in GROUPS).index(g[0]) for g in GROUPS]  # sweep left to right


def slash(x, y, ang, length, wmax, bend):
    """Outline of one scratch: sharp at the start, widest near the start, tapering to a point."""
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
    return left + right[::-1]


svgs = []
for (px, py), delay in zip(GROUPS, DELAYS):
    base = math.radians(rnd.uniform(50, 78))        # slanted down to the right
    if rnd.random() < 0.35:
        base = math.pi - base                         # a few lean the other way
    count = rnd.choice((3, 3, 4))
    gap = rnd.uniform(12, 19)
    length = rnd.uniform(130, 230)
    bend = rnd.uniform(-14, 14)
    nx, ny = -math.sin(base), math.cos(base)
    shapes = []
    for k in range(count):
        off = (k - (count - 1) / 2) * gap
        shapes.append(slash(
            nx * off + rnd.uniform(-4, 4), ny * off + rnd.uniform(-6, 6),
            base + math.radians(rnd.uniform(-2.5, 2.5)),
            length * rnd.uniform(0.78, 1.0), rnd.uniform(2.2, 3.4), bend * rnd.uniform(0.7, 1.2)))
    xs = [p[0] for s in shapes for p in s]
    ys = [p[1] for s in shapes for p in s]
    x0, y0 = min(xs) - 2, min(ys) - 2
    w, h = max(xs) + 2 - x0, max(ys) + 2 - y0
    shapes.sort(key=lambda s: sum(p[0] for p in s) / len(s))
    paths = "".join(
        f'<path style="animation-delay:{delay + k * 0.12:.2f}s" d="M' +
        " L".join(f"{a:.1f},{b:.1f}" for a, b in s) + 'Z"/>' for k, s in enumerate(shapes))
    svgs.append(
        f'<svg class="claw" style="left:{px}%;top:{py}%;animation-delay:{delay:.2f}s" width="{w:.0f}" height="{h:.0f}" '
        f'viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}">{paths}</svg>')

open("assets/claws.html", "w").write("\n".join(svgs) + "\n")
print(len(svgs), "groups")
