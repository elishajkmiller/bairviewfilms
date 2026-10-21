"""Static site generator. Run: python3 build.py
Reads content.json, writes index.html, about.html, contact.html and films/*.html.
Images come from assets/ (see prep_assets.py):
  <slug>-still.jpg, posters/<slug>.jpg, stills/<slug>-NN.jpg, laurels/<slug>--<award>.png"""
import glob
import json
import os
from html import escape as esc
from datetime import date

c = json.load(open("content.json", encoding="utf-8"))
site, films = c["site"], c["films"]
os.makedirs("films", exist_ok=True)


def exists(path):
    return path if os.path.exists(path) else None


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def link_list(items):
    return "".join(f'<a href="{esc(x["url"])}" rel="noopener">{esc(x["label"])}</a>' for x in items)


def page(title, desc, body, depth=0, active=""):
    r = "../" if depth else ""

    def link(href, label, key):
        cur = ' aria-current="page"' if active == key else ""
        return f'<a href="{r}{href}"{cur}>{label}</a>'

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{site['url']}/assets/reel-poster.jpg">
<link rel="icon" type="image/png" href="{r}assets/favicon.png">
<link rel="stylesheet" href="{r}style.css">
<script>if ("scrollRestoration" in history) history.scrollRestoration = "manual";</script>
</head>
<body>
<header class="top">
  <a class="brand" href="{r}index.html"><img src="{r}assets/logo.png" alt="Bairview Films"></a>
  <nav>
    {link('index.html', 'Films', 'films')}
    {link('about.html', 'About', 'about')}
    {link('contact.html', 'Contact', 'contact')}
  </nav>
</header>
<main>
{body}
</main>
<footer>
  <img class="foot-bear" src="{r}assets/bear.png" alt="">
  <div class="foot-links">{link_list(site['socials'])}<a href="mailto:{esc(site['email'])}">Email</a></div>
  <div class="foot-small">&copy; {date.today().year} Bairview Films.</div>
</footer>
</body>
</html>
"""


def facts(f):
    return " &middot; ".join(esc(str(f[k])) for k in ("genre", "runtime", "year") if f.get(k))


def card(f):
    poster = exists(f"assets/posters/{f['slug']}.jpg") or exists(f"assets/{f['slug']}-still.jpg")
    art = (
        f'<img src="{poster}" alt="{esc(f["title"])} poster" loading="lazy">'
        if poster
        else f'<div class="ph"><span>{esc(f["title"])}</span></div>'
    )
    status = f'<span class="status">{esc(f["status"])}</span>\n  ' if f.get("status") else ""
    return f"""<a class="card" href="films/{f['slug']}.html">
  <div class="art">{art}</div>
  <div class="meta">{status}<h3>{esc(f['title'])}</h3>
  <p>{facts(f)}</p></div>
</a>"""


# Home: the reel plays behind the films
write("index.html", page(
    "Bairview Films", site["tagline"], f"""<section class="reel">
  <video autoplay muted loop playsinline preload="auto" aria-hidden="true">
    <source src="assets/reel.mp4" type="video/mp4">
  </video>
</section>
<section id="films" class="wrap over">
  <h2>Films</h2>
  <div class="grid">
{chr(10).join(card(f) for f in films)}
  </div>
</section>
<script>
if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {{
  var v = document.querySelector(".reel video");
  v.removeAttribute("autoplay");
  v.pause();
}}
</script>""", active="films"))

# Film pages
for f in films:
    slug = f["slug"]
    still = exists(f"assets/{slug}-still.jpg")
    bg = f" style=\"background-image:url('../{still}')\"" if still else ""
    poster = exists(f"assets/posters/{slug}.jpg")
    parts = []

    top = []
    if poster:
        top.append(f'<img class="poster" src="../{poster}" alt="{esc(f["title"])} poster">')
    info = []
    if f.get("logline"):
        info.append(f'<p class="logline">{esc(f["logline"])}</p>')
    if f.get("links"):
        info.append(f'<p class="ext">{link_list(f["links"])}</p>')
    if top or info:
        parts.append(f'<div class="film-top">{"".join(top)}<div>{"".join(info)}</div></div>')

    for label, key in (("Trailer", "trailer_video"), ("Watch the Film", "film_video")):
        if f.get(key):
            parts.append(
                f'<h2>{label}</h2>\n  <div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{f[key]}" '
                f'title="{esc(f["title"])} {label}" loading="lazy" allowfullscreen></iframe></div>')

    if f.get("cast"):
        parts.append(f'<h2>Starring</h2>\n  <p>{", ".join(esc(x) for x in f["cast"])}</p>')

    laurel_files = sorted(glob.glob(f"assets/laurels/{slug}--*.png"))
    if laurel_files:
        imgs = "\n".join(
            f'    <img src="../{p}" alt="{esc(os.path.basename(p)[len(slug) + 2:-4].replace("-", " ").title())}" loading="lazy">'
            for p in laurel_files)
        parts.append(f'<h2>Official Selections</h2>\n  <div class="laurels">\n{imgs}\n  </div>')
    elif f.get("laurels"):
        items = "\n".join(f"    <li>{esc(x)}</li>" for x in f["laurels"])
        parts.append(f'<h2>Official Selections</h2>\n  <ul class="laurel-list">\n{items}\n  </ul>')

    shots = sorted(glob.glob(f"assets/stills/{slug}-*.jpg"))
    gallery = ""
    if shots:
        slides = "\n".join(
            f'      <img{" class=\"on\"" if i == 1 else ""} src="../{p}" alt="{esc(f["title"])} still {i}" loading="{"eager" if i == 1 else "lazy"}">'
            for i, p in enumerate(shots, 1))
        dots = "<i class=\"on\"></i>" + "<i></i>" * (len(shots) - 1)
        arrows = (
            '<button type="button" class="car-nav car-prev" aria-label="Previous still">&lsaquo;</button>'
            '<button type="button" class="car-nav car-next" aria-label="Next still">&rsaquo;</button>'
            f'<span class="car-dots">{dots}</span>') if len(shots) > 1 else ""
        gallery = f"""<section class="wrap car-sec"><h2>Stills</h2>
  <div class="car" role="region" aria-roledescription="carousel" aria-label="{esc(f['title'])} stills">
    <div class="car-frame" tabindex="0">
      <div class="car-bg" style="background-image:url('../{shots[0]}')"></div>
{slides}
      {arrows}
    </div>
  </div>
  <script src="../carousel.js" defer></script></section>"""

    write(f"films/{slug}.html", page(
        f"{f['title']} | Bairview Films", f.get("logline") or f"{f['title']}, a Bairview Films production.",
        f"""<section class="hero short"{bg}>
  <div class="hero-inner">
    {f'<span class="status">{esc(f["status"])}</span>' if f.get("status") else ""}
    <h1>{esc(f['title'])}</h1>
    <p class="facts">{facts(f)}</p>
  </div>
</section>
<section class="wrap narrow">
  {chr(10).join(parts)}
  <p><a class="btn ghost" href="../index.html">All Films</a></p>
</section>
{gallery}""", depth=1, active="films"))

# About
paras = "\n".join(f"    <p>{esc(p)}</p>" for p in c["about"])
portrait = exists("assets/kaleb.jpg")
photo = f'<img class="portrait" src="{portrait}" alt="{esc(site["owner"])}">' if portrait else ""
write("about.html", page("About | Bairview Films", c["about"][0], f"""<section class="wrap about">
  {photo}
  <div>
    <h1>About</h1>
{paras}
    <p class="facts">{esc(site['owner'])}<br>{esc(site['roles'])}</p>
    <p class="ext">{link_list(site['owner_links'])}</p>
  </div>
</section>""", active="about"))

# Contact
write("contact.html", page("Contact | Bairview Films", "Contact Bairview Films.", f"""<section class="wrap narrow">
  <h1>Contact</h1>
  <p>For screenings, festival inquiries and collaboration.</p>
  <p><a class="btn" href="mailto:{esc(site['email'])}">{esc(site['email'])}</a></p>
</section>""", active="contact"))

print("built")
