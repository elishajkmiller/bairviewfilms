"""Write assets/paw.svg (one paw, for editing) and assets/paws.html (the paw-print trail for the About page).
Two trails in one fragment: a wide one (along the bottom and right edges) and a tall one for portrait screens (up the
right edge). Each is a fixed SVG scaled like a cover image; the prints fade in one after another (style.css).
Run: python3 make_paws.py"""
import math

from paw_shape import H, RED, W, d, mirrored, shapes

left = "".join(f'<path d="{d(p)}"/>' for _, p in shapes())
right = "".join(f'<path d="{d(mirrored(p))}"/>' for _, p in shapes())
open("assets/paw.svg", "w").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><g fill="{RED}">{left}</g></svg>\n')


def trail(cls, view, p0, p1, p2, n, size, side, first_id):
    """Prints along a quadratic curve, left and right feet alternating, each facing the way it is heading."""
    vw, vh = view
    s = size / H
    items = []
    for i in range(n):
        t = 0.03 + 0.94 * i / (n - 1)
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
        dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
        k = math.hypot(dx, dy)
        off = side if i % 2 else -side
        x, y = x - dy / k * off, y + dx / k * off
        ang = math.degrees(math.atan2(dx, -dy))
        items.append(
            f'<g class="paw" style="--d:{0.4 + i * 0.65:.2f}s" transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) '
            f'scale({s:.4f}) translate({-W / 2} {-H / 2})"><use href="#paw-{"r" if i % 2 else "l"}"/></g>')
    return (f'<svg class="{cls}" viewBox="0 0 {vw} {vh}" preserveAspectRatio="xMidYMid slice" width="100%" height="100%" '
            f'fill="{RED}">\n' + "\n".join(items) + "\n</svg>")


# wide: along the bottom and up the right edge, inside y 130..870 so wide screens do not crop it
wide = trail("trail-wide", (1600, 1000), (150, 850), (1560, 960), (1450, 150), 12, 92, 24, 0)
# tall: up the right edge of a phone, prints half off the screen so they stay out of the text
tall = trail("trail-tall", (400, 1000), (392, 930), (440, 600), (396, 90), 10, 72, 16, 0)
open("assets/paws.html", "w").write(
    f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><g id="paw-l">{left}</g><g id="paw-r">{right}</g></defs></svg>\n'
    + wide + "\n" + tall + "\n")
print("trails written")
