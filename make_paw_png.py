"""Write transparent PNGs of the paw print (left and right, with and without claws) into a folder.
Needs Pillow:  python3 make_paw_png.py <out folder>   (run from the folder holding paw_shape.py)"""
import os
import sys

from PIL import Image, ImageDraw

from paw_shape import H, RED, W, mirrored, shapes

SCALE, SS = 5, 3  # 2000 x 2200 px, supersampled for smooth edges
size = (W * SCALE, H * SCALE)
rgb = tuple(int(RED[i:i + 2], 16) for i in (1, 3, 5))
out = sys.argv[1]
for side, flip in (("left", False), ("right", True)):
    for tag, claws in (("", True), ("-no-claws", False)):
        big = Image.new("L", (size[0] * SS, size[1] * SS), 0)
        dr = ImageDraw.Draw(big)
        for _, poly in shapes(claws):
            poly = mirrored(poly) if flip else poly
            dr.polygon([(x * SCALE * SS, y * SCALE * SS) for x, y in poly], fill=255)
        img = Image.new("RGBA", size, rgb + (0,))
        img.putalpha(big.resize(size, Image.LANCZOS))
        path = os.path.join(out, f"bairview-paw-{side}{tag}.png")
        img.save(path, optimize=True)
        print(path)
