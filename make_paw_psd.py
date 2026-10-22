"""Write a layered PSD of the paw print (pixel layers: Pad, Toe 1-4, Claw 1-4, plus a mirrored right paw group).
Needs Pillow and psd-tools:  python3 make_paw_psd.py out.psd   (run from the folder holding paw_shape.py)"""
import sys

from PIL import Image, ImageDraw
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer

from paw_shape import H, RED, W, mirrored, shapes

SCALE = 5          # PSD pixels per unit: 2000 x 2200
SS = 3             # supersampling for smooth edges
size = (W * SCALE, H * SCALE)
rgb = tuple(int(RED[i:i + 2], 16) for i in (1, 3, 5))


def render(poly):
    big = Image.new("L", (size[0] * SS, size[1] * SS), 0)
    ImageDraw.Draw(big).polygon([(x * SCALE * SS, y * SCALE * SS) for x, y in poly], fill=255)
    mask = big.resize(size, Image.LANCZOS)
    img = Image.new("RGBA", size, rgb + (0,))
    img.putalpha(mask)
    return img


psd = PSDImage.new("RGB", size)
for label, flip in (("Right paw", True), ("Left paw", False)):
    layers = []
    for name, poly in shapes():
        layers.append(PixelLayer.frompil(render(mirrored(poly) if flip else poly), psd, name, 0, 0))
    grp = psd.create_group(layer_list=layers, name=label) if hasattr(psd, "create_group") else None
    if grp is None:
        for l in layers:
            l.name = f"{label} - {l.name}"
            psd.append(l)
    elif flip:
        grp.visible = False
psd.save(sys.argv[1])
print("saved", sys.argv[1], size)
