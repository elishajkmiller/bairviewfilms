"""Resize behind-the-scenes photos into assets/bts/ (full size) and assets/bts/thumb/ (grid) plus sizes.json (thumb width, height).
Run: python3 -I prep_bts.py <extracted "BairView Assets " folder>
Files are taken in file-name order so the numbering is stable."""
import glob
import json
import os
import sys

from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None
src = sys.argv[1]
SETS = {
    "the-lost-place": ("THE LOST PLACE/BTS", ()),
    "roadkill": ("ROADKILL/Set Photos", (26,)),  # index 26 is a blurry shadow frame
    "room-10": ("ROOM 10/Set Photos", ()),
}
for sub in ("bts", "bts/thumb"):
    os.makedirs(f"assets/{sub}", exist_ok=True)


def save(im, dest, width, q):
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dest, "JPEG", quality=q, optimize=True, progressive=True)


sizes = {}
for slug, (d, skip) in SETS.items():
    files = sorted(glob.glob(os.path.join(src, d, "*")))
    n = 0
    for i, f in enumerate(files):
        if i in skip:
            continue
        n += 1
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        save(im, f"assets/bts/{slug}-{n:02d}.jpg", 1600, 78)
        save(im, f"assets/bts/thumb/{slug}-{n:02d}.jpg", 640, 72)
        t = Image.open(f"assets/bts/thumb/{slug}-{n:02d}.jpg")
        sizes[f"{slug}-{n:02d}"] = [t.width, t.height]
    print(slug, n, "photos")
json.dump(sizes, open("assets/bts/sizes.json", "w"))
