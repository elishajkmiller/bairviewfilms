"""Write assets/paw-front.svg and assets/paw-hind.svg (one print each, for editing) and assets/paws.html: the hidden SVG
symbols (front/hind, left/right) that about.js draws the bear-track trail from. about.js lays the trail across the About
text and opens a gap in the text around each print.
Run: python3 make_paws.py"""
from paw_shape import RED, d, dims, mirrored, shapes


def paths(kind, flip):
    return "".join(f'<path d="{d(mirrored(p, kind) if flip else p)}"/>' for _, p in shapes(kind))


for kind in ("front", "hind"):
    w, h = dims(kind)
    open(f"assets/paw-{kind}.svg", "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><g fill="{RED}">{paths(kind, False)}</g></svg>\n')

defs = "".join(f'<g id="paw-{k[0]}{s[0]}">{paths(k, s == "right")}</g>' for k in ("front", "hind") for s in ("left", "right"))
fw, fh = dims("front")
hw, hh = dims("hind")
open("assets/paws.html", "w").write(
    f'<svg id="paw-defs" width="0" height="0" style="position:absolute" aria-hidden="true" data-front="{fw},{fh}" '
    f'data-hind="{hw},{hh}" data-red="{RED}"><defs>{defs}</defs></svg>\n')
print("symbols written")
