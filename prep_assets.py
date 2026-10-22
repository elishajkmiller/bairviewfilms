"""Resize the source asset folders into web-sized files under assets/.
Run: python3 -I prep_assets.py <extracted "BairView Assets " folder> <folder with reel.mp4 and reel-poster.jpg>
Selection lists are by timestamp or name fragment so the originals can stay untouched."""
import glob
import json
import os
import re
import shutil
import sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
src, extra = sys.argv[1], sys.argv[2]
out = "assets"
for sub in ("stills", "laurels", "posters"):
    os.makedirs(f"{out}/{sub}", exist_ok=True)


def find(pattern):
    hits = sorted(glob.glob(os.path.join(src, pattern)))
    if len(hits) != 1:
        sys.exit(f"{pattern!r} matched {len(hits)} files")
    return hits[0]


def save_jpg(path, dest, width, q=80):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", im.size, (10, 10, 10))
        bg.paste(im, mask=im.getchannel("A"))
        im = bg
    im = im.convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dest, "JPEG", quality=q, optimize=True, progressive=True)


def save_png(path, dest, width):
    im = Image.open(path).convert("RGBA")
    box = im.getchannel("A").getbbox()
    if box:
        im = im.crop(box)
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dest, "PNG", optimize=True)


# Logos
save_png(find("BairView Logos/BairView Logo 1.png"), f"{out}/logo.png", 900)
# Logo 2 carries dark text beside the bear: keep only the red bear
_b = Image.open(find("BairView Logos/BairView Logo 2.png")).convert("RGBA")
_red = Image.eval(_b.getchannel("R"), lambda v: 255 if v > 90 else 0)
_b = _b.crop(_red.getbbox())
_b.save(f"{out}/bear-src.png")
save_png(f"{out}/bear-src.png", f"{out}/bear.png", 400)
os.remove(f"{out}/bear-src.png")
bear = Image.open(f"{out}/bear.png")
side = max(bear.size)
icon = Image.new("RGBA", (side, side), (0, 0, 0, 0))
icon.paste(bear, ((side - bear.width) // 2, (side - bear.height) // 2), bear)
icon.resize((128, 128), Image.LANCZOS).save(f"{out}/favicon.png", optimize=True)

# Reel video and its poster frame
shutil.copy(os.path.join(extra, "reel.mp4"), f"{out}/reel.mp4")
save_jpg(os.path.join(extra, "reel-poster.jpg"), f"{out}/reel-poster.jpg", 1600)

# Posters (2:3)
save_jpg(find("THE LOST PLACE/4BC8FF70*.jpeg"), f"{out}/posters/the-lost-place.jpg", 800)
save_jpg(find("ROADKILL/ROADKILL POSTER.PNG"), f"{out}/posters/roadkill.jpg", 800)
save_jpg(find("SOLUS/Solus Official Poster*.PNG"), f"{out}/posters/solus.jpg", 800)
# The Room 10 poster file has a white margin around the black poster: crop to the poster
_p = Image.open(find("ROOM 10/ROOM 10 Poster.jpeg")).convert("RGB")
_box = Image.eval(_p.convert("L"), lambda v: 255 if v < 235 else 0).getbbox()
_p.crop(_box).save(f"{out}/posters/room-10-src.jpg", quality=92)
save_jpg(f"{out}/posters/room-10-src.jpg", f"{out}/posters/room-10.jpg", 800)
os.remove(f"{out}/posters/room-10-src.jpg")

# Portrait
save_jpg(find("Photos of Kaleb/*Pic 2.jpg"), f"{out}/kaleb.jpg", 900)

# Hero stills (wide), one per film
HERO = {
    "the-lost-place": "THE LOST PLACE/Stills/AACEDFE6*.jpeg",
    "roadkill": "ROADKILL/Film Stills/*8.56*.jpeg",
    "room-10": "ROOM 10/Film Stills/*3.44*.jpeg",
    "solus": "SOLUS/Stills/Solus Basment Still 2.png",
}
for slug, pat in HERO.items():
    save_jpg(find(pat), f"{out}/{slug}-still.jpg", 2000, q=78)

# Galleries
GALLERY = {
    "the-lost-place": [
        "THE LOST PLACE/Stills/*.jpeg", "THE LOST PLACE/Stills/IMG_2617.PNG",
    ],
    "room-10": ["ROOM 10/Film Stills/*.jpeg"],
    "roadkill": [
        f"ROADKILL/Film Stills/*{t}*.jpeg"
        for t in ("8.37", "8.40", "8.41", "8.42", "8.44", "8.45", "8.46", "8.49", "8.56", "8.58", "9.00", "9.03", "9.04")
    ],
    "solus": ["SOLUS/Stills/*.png"],
}
for slug, pats in GALLERY.items():
    seen, n = set(), 0
    for pat in pats:
        for f in sorted(glob.glob(os.path.join(src, pat))):
            if f in seen or "(1)" in os.path.basename(f):
                continue
            seen.add(f)
            n += 1
            save_jpg(f, f"{out}/stills/{slug}-{n:02d}.jpg", 1400, q=76)
    print(slug, n, "stills")

# Laurels: black/white PNGs with alpha, shrunk
LAUREL_DIRS = {
    "the-lost-place": "THE LOST PLACE/Laurels",
    "roadkill": "ROADKILL/Laurels",
    "room-10": "ROOM 10/Laurels ",
}
for slug, d in LAUREL_DIRS.items():
    for f in sorted(glob.glob(os.path.join(src, d, "*.png"))):
        stem = re.sub(r"\(\d+\)|_edited", "", os.path.splitext(os.path.basename(f))[0])
        name = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
        save_png(f, f"{out}/laurels/{slug}--{name}.png", 360)
        print(slug, name)

# Average color of each film's stills, used for the reel border
colors = {}
for slug in GALLERY:
    px = [Image.open(f).convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
          for f in sorted(glob.glob(f"{out}/stills/{slug}-*.jpg"))]
    avg = tuple(round(sum(c[i] for c in px) / len(px)) for i in range(3))
    colors[slug] = "#%02x%02x%02x" % avg
json.dump(colors, open(f"{out}/colors.json", "w"), indent=2)
print(colors)
