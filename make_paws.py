"""Write assets/paw-front.svg and assets/paw-hind.svg (one print each, for editing) and assets/paws.html (the bear-track
trail for the About page). A walking bear puts its hind foot down just behind its front foot on the same side, so the
trail is pairs of front and hind prints, left and right alternating. Two trails in one fragment: a wide one (along the
bottom and right edges) and a tall one for portrait screens (up the right edge). Each is a fixed SVG scaled like a cover
image; the prints fade in one after another, front then hind (style.css).
Run: python3 make_paws.py"""
import math

from paw_shape import RED, d, dims, mirrored, shapes


def paths(kind, flip):
    return "".join(f'<path d="{d(mirrored(p, kind) if flip else p)}"/>' for _, p in shapes(kind))


for kind in ("front", "hind"):
    w, h = dims(kind)
    open(f"assets/paw-{kind}.svg", "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><g fill="{RED}">{paths(kind, False)}</g></svg>\n')

defs = "".join(f'<g id="paw-{k[0]}{s[0]}">{paths(k, s == "right")}</g>' for k in ("front", "hind") for s in ("left", "right"))


def trail(cls, view, p0, p1, p2, size, stride, behind, side):
    """Front and hind prints along a quadratic curve. size = height of a front print in canvas units, stride = distance
    between one pair and the next, behind = how far the hind print lands behind its front print, side = sideways offset."""
    vw, vh = view
    s = size / dims("front")[1]
    pts = []
    n = 400
    for i in range(n + 1):
        t = i / n
        pts.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))

    def at(dist):
        dist = max(0.0, min(cum[-1] - 1e-6, dist))
        j = max(1, next(i for i, c in enumerate(cum) if c >= dist))
        a, b = pts[j - 1], pts[j]
        f = (dist - cum[j - 1]) / ((cum[j] - cum[j - 1]) or 1)
        return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1])))

    items = []
    k = 0
    pos = behind + 10
    while pos < cum[-1] - 10:
        right = k % 2
        off = side if right else -side
        for kind, back in (("front", 0), ("hind", behind)):
            x, y, ang = at(pos - back)
            r = math.radians(ang)
            x, y = x + math.cos(r) * off, y + math.sin(r) * off  # sideways = perpendicular to the heading
            w, h = dims(kind)
            items.append(
                f'<g class="paw" style="--d:{0.4 + len(items) * 0.55:.2f}s" transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) '
                f'scale({s:.4f}) translate({-w / 2:.1f} {-h / 2:.1f})"><use href="#paw-{kind[0]}{"r" if right else "l"}"/></g>')
        pos += stride
        k += 1
    return (f'<svg class="{cls}" viewBox="0 0 {vw} {vh}" preserveAspectRatio="xMidYMid slice" width="100%" height="100%" '
            f'fill="{RED}">\n' + "\n".join(items) + "\n</svg>")


# wide: across the lower right of the page, over the text, and up the right edge, inside y 130..870 so wide screens do not crop it
wide = trail("trail-wide", (1600, 1000), (150, 850), (1000, 950), (1450, 150), 88, 310, 120, 26)
# tall: up the right edge of a phone, prints half off the screen so they stay out of the text
tall = trail("trail-tall", (400, 1000), (392, 930), (440, 600), (396, 90), 66, 240, 90, 18)
open("assets/paws.html", "w").write(
    f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>{defs}</defs></svg>\n' + wide + "\n" + tall + "\n")
print("trails written:", wide.count('class="paw"'), "wide,", tall.count('class="paw"'), "tall")
