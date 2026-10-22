"""Write a layered PSD of the bear tracks: groups Front left, Front right, Hind left, Hind right (the right ones start
hidden), each with its pixel layers (Pad 1-3, Heel 1-2, Toe 1-5, Claw 1-5). Front and hind sit side by side.
Needs Pillow and psd-tools:  python3 make_paw_psd.py out.psd   (run from the folder holding paw_shape.py)"""
import sys

from PIL import Image, ImageDraw
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer

from paw_shape import RED, dims, mirrored, shapes

SCALE = 5          # PSD pixels per unit
SS = 3             # supersampling for smooth edges
GAP = 100          # pixels between the two prints
rgb = tuple(int(RED[i:i + 2], 16) for i in (1, 3, 5))
fw, fh = dims("front")
hw, hh = dims("hind")
psd = PSDImage.new("RGB", ((fw + hw) * SCALE + GAP, max(fh, hh) * SCALE))


def render(poly, size):
    big = Image.new("L", (size[0] * SS, size[1] * SS), 0)
    ImageDraw.Draw(big).polygon([(x * SCALE * SS, y * SCALE * SS) for x, y in poly], fill=255)
    img = Image.new("RGBA", size, rgb + (0,))
    img.putalpha(big.resize(size, Image.LANCZOS))
    return img


for kind, left in (("front", 0), ("hind", fw * SCALE + GAP)):
    w, h = dims(kind)
    for side, flip in (("left", False), ("right", True)):
        layers = [PixelLayer.frompil(render(mirrored(p, kind) if flip else p, (w * SCALE, h * SCALE)), psd, name, 0, left)
                  for name, p in shapes(kind)]
        grp = psd.create_group(layer_list=layers, name=f"{kind.title()} {side}")
        grp.visible = not flip
psd.save(sys.argv[1])
print("saved", sys.argv[1], psd.size)
