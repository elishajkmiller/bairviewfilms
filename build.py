"""Static site generator. Run: python3 build.py
Reads content.json, writes index.html, about.html, contact.html and films/*.html.
Drop images in assets/ as <slug>-poster.jpg and <slug>-still.jpg to use them."""
import json
import os
from html import escape as esc
from datetime import date

c = json.load(open("content.json", encoding="utf-8"))
site, films = c["site"], c["films"]
os.makedirs("films", exist_ok=True)


def img(slug, kind):
    path = f"assets/{slug}-{kind}.jpg"
    return path if os.path.exists(path) else None


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def page(title, desc, body, depth=0, active=""):
    r = "../" if depth else ""

    def link(href, label, key):
        cur = ' aria-current="page"' if active == key else ""
        return f'<a href="{r}{href}"{cur}>{label}</a>'

    socials = "".join(
        f'<a href="{esc(s["url"])}" rel="noopener">{esc(s["label"])}</a>'
        for s in site["socials"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<link rel="stylesheet" href="{r}style.css">
</head>
<body>
<header class="top">
  <a class="brand" href="{r}index.html">Bairview Films</a>
  <nav>
    {link('index.html#films', 'Films', 'films')}
    {link('about.html', 'About', 'about')}
    {link('contact.html', 'Contact', 'contact')}
  </nav>
</header>
<main>
{body}
</main>
<footer>
  <div class="foot-brand">Bairview Films</div>
  <div class="foot-links">{socials}<a href="mailto:{esc(site['email'])}">Email</a></div>
  <div class="foot-small">&copy; {date.today().year} Bairview Films. {esc(site['roles'])}.</div>
</footer>
</body>
</html>
"""


def card(f):
    poster = img(f["slug"], "poster")
    art = (
        f'<img src="{poster}" alt="{esc(f["title"])} poster" loading="lazy">'
        if poster
        else f'<div class="ph"><span>{esc(f["title"])}</span></div>'
    )
    return f"""<a class="card" href="films/{f['slug']}.html">
  <div class="art">{art}</div>
  <div class="meta"><span class="status">{esc(f['status'])}</span>
  <h3>{esc(f['title'])}</h3>
  <p>{esc(f['genre'])} &middot; {esc(f['runtime'])} &middot; {f['year']}</p></div>
</a>"""


# Home
hero = films[0]
still = img(hero["slug"], "still")
bg = f" style=\"background-image:url('{still}')\"" if still else ""
write("index.html", page(
    "Bairview Films", site["tagline"], f"""<section class="hero"{bg}>
  <div class="hero-inner">
    <span class="status">Latest</span>
    <h1>{esc(hero['title'])}</h1>
    <p>{esc(hero['logline'])}</p>
    <a class="btn" href="films/{hero['slug']}.html">View Film</a>
  </div>
</section>
<section id="films" class="wrap">
  <h2>All Films</h2>
  <div class="grid">
{chr(10).join(card(f) for f in films)}
  </div>
</section>""", active="films"))

# Film pages
for f in films:
    still = img(f["slug"], "still")
    bg = f" style=\"background-image:url('../{still}')\"" if still else ""
    cast = ", ".join(esc(x) for x in f["cast"])
    laurels = "\n".join(f"    <li>{esc(x)}</li>" for x in f["laurels"])
    write(f"films/{f['slug']}.html", page(
        f"{f['title']} | Bairview Films", f["logline"], f"""<section class="hero short"{bg}>
  <div class="hero-inner">
    <span class="status">{esc(f['status'])}</span>
    <h1>{esc(f['title'])}</h1>
    <p class="facts">{esc(f['genre'])} &middot; {esc(f['runtime'])} &middot; {f['year']}</p>
  </div>
</section>
<section class="wrap narrow">
  <p class="logline">{esc(f['logline'])}</p>
  <h2>Starring</h2>
  <p>{cast}</p>
  <h2>Official Selections</h2>
  <ul class="laurels">
{laurels}
  </ul>
  <p><a class="btn ghost" href="../index.html#films">All Films</a></p>
</section>""", depth=1, active="films"))

# About
paras = "\n".join(f"  <p>{esc(p)}</p>" for p in c["about"])
write("about.html", page("About | Bairview Films", c["about"][0], f"""<section class="wrap narrow">
  <h1>About</h1>
{paras}
  <p class="facts">{esc(site['owner'])}<br>{esc(site['roles'])}</p>
</section>""", active="about"))

# Contact
write("contact.html", page("Contact | Bairview Films", "Contact Bairview Films.", f"""<section class="wrap narrow">
  <h1>Contact</h1>
  <p>For screenings, festival inquiries and collaboration.</p>
  <p><a class="btn" href="mailto:{esc(site['email'])}">{esc(site['email'])}</a></p>
</section>""", active="contact"))

print("built")
