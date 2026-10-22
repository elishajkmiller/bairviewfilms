"""Write transparent PNGs of the bear tracks (front and hind, left and right) into a folder.
Needs Pillow:  python3 make_paw_png.py <out folder>   (run from the folder holding paw_shape.py)"""
import os
import sys

from PIL import Image, ImageDraw

from paw_shape import RED, dims, mirrored, shapes

SCALE, SS = 5, 3  # 5 px per unit, supersampled for smooth edges
rgb = tuple(int(RED[i:i + 2], 16) for i in (1, 3, 5))
out = sys.argv[1]
for kind in ("front", "hind"):
    w, h = dims(kind)
    size = (w * SCALE, h * SCALE)
    for side, flip in (("left", False), ("right", True)):
        big = Image.new("L", (size[0] * SS, size[1] * SS), 0)
        dr = ImageDraw.Draw(big)
        for _, poly in shapes(kind):
            poly = mirrored(poly, kind) if flip else poly
            dr.polygon([(x * SCALE * SS, y * SCALE * SS) for x, y in poly], fill=255)
        img = Image.new("RGBA", size, rgb + (0,))
        img.putalpha(big.resize(size, Image.LANCZOS))
        path = os.path.join(out, f"bairview-paw-{kind}-{side}.png")
        img.save(path, optimize=True)
        print(path, size)
