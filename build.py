"""Static site generator. Run: python3 build.py
Reads content.json, writes index.html, bts.html, about.html, contact.html and films/*.html.
Images come from assets/ (see prep_assets.py):
  <slug>-still.jpg, posters/<slug>.jpg, stills/<slug>-NN.jpg, laurels/<slug>--<award>.png, bts/ (prep_bts.py)"""
import glob
import json
import os
import re
from html import escape as esc
from datetime import date

c = json.load(open("content.json", encoding="utf-8"))
colors = json.load(open("assets/colors.json")) if os.path.exists("assets/colors.json") else {}
site, films = c["site"], c["films"]
os.makedirs("films", exist_ok=True)


def exists(path):
    return path if os.path.exists(path) else None


def rich(text):
    """Escape text, then turn [label](https://...) into a link."""
    return re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" rel="noopener">\1</a>', esc(text))


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
    {link('bts.html', 'BTS', 'bts')}
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
  <div class="foot-small"><span>&copy; {date.today().year} Bairview Films.</span><a href="https://elishajkmiller.com" rel="noopener">Website by EJKM</a></div>
</footer>
</body>
</html>
"""


def facts(f):
    return " &middot; ".join(esc(str(f[k])) for k in ("genre", "runtime", "year") if f.get(k))


def card(f):
    real = exists(f"assets/posters/{f['slug']}.jpg")
    poster = real or exists(f"assets/{f['slug']}-still.jpg")
    art = (
        f'<img{" class=\"whole\"" if real else ""} src="{poster}" alt="{esc(f["title"])} poster" loading="lazy">'
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

    if f.get("synopsis"):
        parts.append(f'<p>{esc(f["synopsis"])}</p>')
    elif f.get("logline"):
        parts.append(f'<p class="logline">{esc(f["logline"])}</p>')

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
    row = ""
    if poster or shots:
        ext = f'<p class="ext">{link_list(f["links"])}</p>' if f.get("links") else ""
        art = (f'<div class="poster-col"><img class="poster" src="../{poster}" alt="{esc(f["title"])} poster">{ext}</div>'
               if poster else "")
        reel = ""
        if shots:
            def tiles(dup):
                extra = ' aria-hidden="true" tabindex="-1"' if dup else ""
                return "\n".join(
                    f'        <button type="button" class="rail-t" data-i="{i}"{extra if dup else f" aria-label=\"Open still {i}\""}>'
                    f'<img src="../{p}" alt="" loading="lazy"></button>'
                    for i, p in enumerate(shots))
            reel = f"""<div class="rail" style="--dur:{len(shots) * 6}s;--avg:{colors.get(slug, "#2a2a2a")}" role="region" aria-label="{esc(f['title'])} stills">
      <div class="rail-track">
{tiles(False)}
{tiles(True)}
      </div>
    </div>"""
        row = f"""<section class="wrap strip">
  <div class="strip-row">
    {art}
    {reel}
  </div>
  {"" if poster else ext}
  <script src="../carousel.js" defer></script>
</section>"""

    write(f"films/{slug}.html", page(
        f"{f['title']} | Bairview Films", f.get("logline") or f"{f['title']}, a Bairview Films production.",
        f"""<section class="hero short"{bg}>
  <div class="hero-inner">
    {f'<span class="status">{esc(f["status"])}</span>' if f.get("status") else ""}
    <h1>{esc(f['title'])}</h1>
    <p class="facts">{facts(f)}</p>
  </div>
</section>
{row}
<section class="wrap narrow">
  {chr(10).join(parts)}
</section>
<div class="wrap back"><a class="btn ghost" href="../index.html">Back to Films</a></div>""", depth=1, active="films"))

# About
paras = "\n".join(f"    <p>{rich(p)}</p>" for p in c["about"])
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

# Behind the scenes: one row per film like the film pages, with its BTS video(s) on the left and a scrolling
# strip of set photos on the right (bts.js: click-to-play video, tabs for more videos, photo lightbox).
sizes = json.load(open("assets/bts/sizes.json")) if os.path.exists("assets/bts/sizes.json") else {}
titles = {f["slug"]: f["title"] for f in films}
blocks = []
for s in c.get("bts", {}).get("sections", []):
    slug = s["slug"]
    shots = sorted(glob.glob(f"assets/bts/{slug}-*.jpg"))
    vids = s.get("videos", [])
    if not (shots or vids or s.get("links")):
        continue
    row = []
    if vids:
        v = vids[0]
        tabs = ""
        if len(vids) > 1:
            tabs = '<div class="vtabs">' + "".join(
                f'<button type="button" data-id="{esc(x["id"])}" data-title="{esc(x["title"])}"'
                f'{" class=\"on\"" if i == 0 else ""}>{esc(x.get("label", str(i + 1)))}</button>'
                for i, x in enumerate(vids)) + "</div>"
        row.append(
            f'<div class="vid-col"><button type="button" class="vthumb" data-id="{esc(v["id"])}" data-title="{esc(v["title"])}" '
            f'aria-label="Play {esc(v["title"])}"><img src="https://i.ytimg.com/vi/{esc(v["id"])}/hqdefault.jpg" alt="" loading="lazy"><i></i></button>'
            f'{tabs}<p class="vcap">{esc(v["title"])}</p></div>')
    if shots:
        def tiles(dup):
            out = []
            for i, p in enumerate(shots):
                key = os.path.basename(p)[:-4]
                label = ' aria-hidden="true" tabindex="-1"' if dup else f' aria-label="Open photo {i + 1}"'
                out.append(
                    f'        <button type="button" class="rail-t" data-i="{i}" data-full="{p}"{label}>'
                    f'<img src="assets/bts/thumb/{key}.jpg" alt="" loading="lazy"></button>')
            return "\n".join(out)
        row.append(f'''<div class="rail" style="--dur:{len(shots) * 6}s;--avg:{colors.get(slug, "#2a2a2a")}" role="region" aria-label="{esc(titles[slug])} behind the scenes photos">
      <div class="rail-track">
{tiles(False)}
{tiles(True)}
      </div>
    </div>''')
    ext = f'<p class="ext">{link_list(s["links"])}</p>' if s.get("links") else ""
    blocks.append(
        f'<h2 id="{slug}"><a href="films/{slug}.html">{esc(titles[slug])}</a></h2>\n  <div class="strip-row">\n    ' +
        "\n    ".join(row) + f"\n  </div>\n  {ext}")
more = ""
if c["bts"].get("playlist"):
    more = (f'<p class="ext"><a href="https://www.youtube.com/playlist?list={esc(c["bts"]["playlist"])}" rel="noopener">'
            "Full playlist on YouTube</a></p>")
write("bts.html", page("Behind the Scenes | Bairview Films", c["bts"]["intro"], f"""<section class="wrap bts">
  <h1>Behind the Scenes</h1>
  {more}
  {chr(10).join(blocks)}
  <script src="bts.js" defer></script>
</section>""", active="bts"))

# Contact: one form, the button picked decides which extra fields show (contact.js). Submissions go to the
# Google Apps Script web app in site.form_endpoint (apps-script/Code.gs); without one the form opens an email.
def field(name, label, kind="text", required=False, opts=None, hint=""):
    req = " required" if required else ""
    star = "" if required else ' <span class="opt">optional</span>'
    if opts:
        body = f'<select name="{name}" id="f-{name}"{req}><option value="">Choose one</option>' + "".join(
            f"<option>{esc(o)}</option>" for o in opts) + "</select>"
    elif kind == "textarea":
        body = f'<textarea name="{name}" id="f-{name}" rows="5"{req}></textarea>'
    else:
        body = f'<input type="{kind}" name="{name}" id="f-{name}"{req}>'
    note = f'<small>{hint}</small>' if hint else ""
    return f'<div class="f"><label for="f-{name}">{esc(label)}{star}</label>\n    {body}{note}</div>'


TYPES = [
    ("hire", "Hire me", [
        field("project_type", "Project type", required=True, opts=[
            "Narrative film", "Commercial", "Music video", "Documentary", "Event or corporate", "Other"]),
        field("timeline", "Timeline"),
        field("budget", "Budget range", opts=[
            "Under $1,000", "$1,000 to $5,000", "$5,000 to $15,000", "$15,000 to $50,000", "$50,000 and up", "Not sure yet"]),
        field("heard", "How did you hear about me", opts=[
            "Instagram", "YouTube", "A film festival", "A friend or colleague", "POW417", "Search", "Other"]),
    ]),
    ("join", "Join a project", [
        field("role", "Role", required=True, opts=[
            "Actor", "Director of photography", "Camera operator", "Sound", "Gaffer or grip", "Production design or art",
            "Makeup or SFX", "Editor", "Composer", "Production assistant", "Other"]),
        field("link", "Reel or portfolio link", kind="url"),
        field("location", "Location"),
    ]),
    ("pow417", "POW417", [
        field("pow_role", "How do you want to be involved", required=True, opts=["Volunteer", "Sponsor", "Compete"]),
        '<p class="note">Want to compete? Register on <a href="https://pow417.com" rel="noopener">pow417.com</a>.</p>',
    ]),
    ("press", "Press or screenings", [
        field("outlet", "Outlet or venue", required=True),
        field("event_date", "Date", kind="date"),
    ]),
    ("reach", "Just reaching out", []),
]
type_btns = "\n".join(
    f'    <label class="pick"><input type="radio" name="type" value="{esc(label)}" data-key="{key}" required>'
    f"<span>{esc(label)}</span></label>" for key, label, _ in TYPES)
type_sets = "\n".join(
    f'  <fieldset class="extra" data-key="{key}" hidden disabled>\n    ' + "\n    ".join(fs) + "\n  </fieldset>"
    for key, _, fs in TYPES if fs)
write("contact.html", page("Contact | Bairview Films",
    "Hire Bairview Films, join a project, volunteer or sponsor for POW417, or just say hello.", f"""<section class="wrap narrow">
  <h1>Contact</h1>
  <p>Hire me to direct or produce, join a future project, get involved with POW417, or just say hello. Pick what fits and fill in the rest.</p>
  <form id="contact" class="cform" method="post" action="{esc(site.get('form_endpoint', ''))}" data-endpoint="{esc(site.get('form_endpoint', ''))}" data-email="{esc(site['email'])}">
  <div class="row2">
    {field("name", "Name", required=True)}
    {field("email", "Email", kind="email", required=True)}
  </div>
  <fieldset class="types"><legend>What brings you here</legend>
{type_btns}
  </fieldset>
{type_sets}
  <div class="msg" hidden>
    {field("message", "Message", kind="textarea")}
  </div>
  <input class="hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
  <button class="btn" type="submit" hidden>Send</button>
  <p class="status-line" role="status" aria-live="polite"></p>
  </form>
  <noscript><p>This form needs JavaScript. Email <a href="mailto:{esc(site['email'])}">{esc(site['email'])}</a> instead.</p></noscript>
  <script src="contact.js" defer></script>
</section>""", active="contact"))

print("built")
