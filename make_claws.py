"""Write assets/claws.svg: a tile of claw-mark scratches (groups of 3 or 4 tapered slashes) in the BairView red.
Each group scratches in slash by slash, holds with a pulsing glow, fades and repeats (CSS animation inside the SVG,
off when the visitor prefers reduced motion). Run: python3 make_claws.py   (fixed seed, the pattern is stable)"""
import math
import random

RED = "#800E13"  # from the Drive palette image
W, H = 1000, 1500
CYCLE = 12  # seconds per scratch/hold/fade loop
rnd = random.Random(417)

# group origins spread across the tile so any phone-width strip of it holds a few marks
ORIGINS = [(60, 80), (870, 160), (640, 640), (110, 1010), (790, 1020), (430, 1330)]
DELAYS = [0.3, 1.4, 2.8, 4.2, 5.6, 7.0]


def slash(x, y, ang, length, wmax, bend):
    """(outline, spine) of one scratch: sharp at the start, widest near the start, tapering to a point."""
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx
    n = 28
    left, right, spine = [], [], []
    for i in range(n + 1):
        t = i / n
        bx = x + dx * length * t + nx * bend * math.sin(math.pi * t)
        by = y + dy * length * t + ny * bend * math.sin(math.pi * t)
        w = wmax * min(1, t * 7) * (1 - t) ** 0.7
        left.append((bx + nx * w, by + ny * w))
        right.append((bx - nx * w, by - ny * w))
        spine.append((bx, by))
    pts = left + right[::-1]
    poly = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts) + "Z"
    line = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in spine)
    return poly, line


masks, glow, crisp = [], [], []
uid = 0
for gi, (ox, oy) in enumerate(ORIGINS):
    base = math.radians(rnd.uniform(50, 78))        # slanted down to the right
    if rnd.random() < 0.35:
        base = math.pi - base                         # a few lean the other way
    count = rnd.choice((3, 3, 4))
    gap = rnd.uniform(12, 19)
    length = rnd.uniform(130, 230)
    bend = rnd.uniform(-14, 14)
    nx, ny = -math.sin(base), math.cos(base)
    polys = []
    for k in range(count):
        off = (k - (count - 1) / 2) * gap
        poly, line = slash(
            ox + nx * off + rnd.uniform(-4, 4), oy + ny * off + rnd.uniform(-6, 6),
            base + math.radians(rnd.uniform(-2.5, 2.5)),
            length * rnd.uniform(0.78, 1.0), rnd.uniform(2.2, 3.4), bend * rnd.uniform(0.7, 1.2))
        # the mask stroke is drawn along the spine, so the scratch is revealed from its start to its tip
        masks.append(
            f'<mask id="m{uid}" maskUnits="userSpaceOnUse" x="-100" y="-100" width="{W + 200}" height="{H + 200}">'
            f'<path class="m" style="animation-delay:{DELAYS[gi] + k * 0.18:.2f}s" d="{line}" pathLength="1"/></mask>')
        polys.append(f'<path mask="url(#m{uid})" d="{poly}"/>')
        uid += 1
    body = "".join(polys)
    delay = f"animation-delay:{DELAYS[gi]:.2f}s"
    glow.append(f'<g class="g" style="{delay}"><g class="glow" style="{delay}" filter="url(#blur)">{body}</g></g>')
    crisp.append(f'<g class="g" style="{delay}">{body}</g>')

css = f"""
.m {{ fill:none; stroke:#fff; stroke-width:30; stroke-dasharray:1; stroke-dashoffset:1; animation:draw {CYCLE}s infinite; }}
.g {{ animation:fade {CYCLE}s infinite; }}
.glow {{ animation:pulse 3s ease-in-out infinite alternate; }}
@keyframes draw {{ 0% {{ stroke-dashoffset:1; animation-timing-function:cubic-bezier(.2,.7,.3,1); }} 6% {{ stroke-dashoffset:0; }} 96% {{ stroke-dashoffset:0; }} 97%,100% {{ stroke-dashoffset:1; }} }}
@keyframes fade {{ 0%,76% {{ opacity:1; }} 94%,100% {{ opacity:0; }} }}
@keyframes pulse {{ from {{ opacity:.35; }} to {{ opacity:1; }} }}
@media (prefers-reduced-motion:reduce) {{
  .m {{ animation:none; stroke-dashoffset:0; }}
  .g {{ animation:none; opacity:1; }}
  .glow {{ animation:none; opacity:.6; }}
}}
"""
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<style>{css}</style>\n'
       f'<defs><filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="7"/><feComponentTransfer><feFuncA type="linear" slope="3"/></feComponentTransfer></filter>'
       f'{"".join(masks)}</defs>\n'
       f'<g fill="{RED}">{"".join(glow)}{"".join(crisp)}</g>\n</svg>\n')
open("assets/claws.svg", "w").write(svg)
print(uid, "scratches,", len(svg), "bytes")
