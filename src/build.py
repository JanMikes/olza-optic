#!/usr/bin/env python3
"""
OLZA OPTIC — static site generator.

Assembles fully self-contained static HTML pages from the partials in
src/partials/ and the page bodies in src/pages/, writing the result to the
repository root. The output is plain static HTML that GitHub Pages serves
directly — no build step is required at serve time. Run this only when you
edit a source file:

    python3 src/build.py

Everything (icons, header, footer) is inlined so each page works on its own,
including from the local filesystem (file://) for quick previews.
"""
from __future__ import annotations
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PARTIALS = SRC / "partials"
PAGES_DIR = SRC / "pages"

# Production location (GitHub Pages project site). Used for canonical / OG /
# sitemap absolute URLs. Change here if the deploy URL changes.
SITE_BASE = "https://janmikes.github.io/olza-optic"
BASE_PATH = "/olza-optic"  # path the 404 page uses for absolute asset links
YEAR = str(datetime.date.today().year)

# Active-nav markers used in src/partials/header.html
NAV_MARKERS = ["a_onas", "a_mereni", "a_bryle", "a_suche"]
NAV_FOR = {
    "onas": "a_onas",
    "mereni": "a_mereni",
    "bryle": "a_bryle",
    "suche": "a_suche",
}

# slug, title, description, nav-key, og image (file in assets/photos), body_class
PAGES = [
    dict(
        slug="index",
        title="OLZA OPTIC — Optika v srdci Českého Těšína",
        desc="Moderní a kreativní optika v Českém Těšíně. Měření zraku přístrojem "
        "Visionix VX 120+, kvalitní brýlové čočky, široký výběr obrub i profesionální "
        "aplikace kontaktních čoček.",
        nav="",
        og="store-interior.jpg",
        body_class="page-home",
    ),
    dict(
        slug="o-nas",
        title="O nás — OLZA OPTIC",
        desc="OLZAOPTIC s.r.o. je moderní a kreativní optika v srdci Českého Těšína. "
        "Již řadu let se komplexně zaměřujeme na péči o zrak s individuálním "
        "a profesionálním přístupem.",
        nav="onas",
        og="founder-renata.jpg",
        body_class="page-onas",
    ),
    dict(
        slug="mereni-zraku",
        title="Měření zraku — OLZA OPTIC",
        desc="Měříme zrak jedním z nejmodernějších přístrojů Visionix VX 120+, který "
        "během několika sekund zjistí desítky parametrů vašich očí. Celé vyšetření "
        "zabere 30 minut.",
        nav="mereni",
        og="visionix-vysetreni.jpg",
        body_class="page-mereni",
    ),
    dict(
        slug="bryle",
        title="Brýle — zhotovení, opravy a čištění — OLZA OPTIC",
        desc="Zhotovení brýlí do jedné hodiny, opravy ve vlastní dílně a šetrné "
        "ultrazvukové čištění. S výběrem rámků a skel vám odborně poradí zkušené "
        "optičky.",
        nav="bryle",
        og="bryle-zhotoveni.jpg",
        body_class="page-bryle",
    ),
    dict(
        slug="suche-oko",
        title="Diagnostika suchého oka — OLZA OPTIC",
        desc="Pálení, řezání nebo unavené oči? Provedeme komplexní diagnostiku "
        "slzného filmu, zjistíme přesnou příčinu vašich potíží a doporučíme řešení "
        "přímo pro vás.",
        nav="suche",
        og="dry-eye-diagnostics.jpg",
        body_class="page-suche",
    ),
]

LOCAL_BUSINESS_SCHEMA = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Optician",
  "name": "OLZA OPTIC (OLZAOPTIC s.r.o.)",
  "image": "%(base)s/assets/photos/store-interior.jpg",
  "url": "%(base)s/",
  "telephone": "+420730171228",
  "email": "info@olzoptic.cz",
  "priceRange": "$$",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Dukelská 1305/1",
    "addressLocality": "Český Těšín",
    "postalCode": "737 01",
    "addressCountry": "CZ"
  },
  "openingHoursSpecification": [
    {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "07:30", "closes": "17:00"},
    {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "08:00", "closes": "12:00"}
  ],
  "areaServed": "Český Těšín, Třinec, Karviná",
  "sameAs": ["https://www.mojecocky.cz/"]
}
</script>""" % {"base": SITE_BASE}


def read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def build():
    layout = read(PARTIALS / "layout.html")
    sprite = read(PARTIALS / "sprite.html").strip()
    header_tpl = read(PARTIALS / "header.html").strip()
    footer = read(PARTIALS / "footer.html").strip()

    written = []
    for page in PAGES:
        slug = page["slug"]
        body = read(PAGES_DIR / f"{slug}.html")

        # Header with the correct nav link marked active
        header = header_tpl
        active_marker = NAV_FOR.get(page["nav"])
        for m in NAV_MARKERS:
            header = header.replace("{{%s}}" % m, "is-active" if m == active_marker else "")

        canonical = SITE_BASE + ("/" if slug == "index" else f"/{slug}.html")
        og_image = f"{SITE_BASE}/assets/photos/{page['og']}"
        schema = LOCAL_BUSINESS_SCHEMA if slug == "index" else ""

        html = layout
        repl = {
            "title": page["title"],
            "description": page["desc"],
            "canonical": canonical,
            "og_type": "website",
            "og_image": og_image,
            "body_class": page["body_class"],
            "sprite": sprite,
            "header": header,
            "content": body.strip(),
            "footer": footer,
            "head_extra": "",
            "schema": schema,
        }
        for k, v in repl.items():
            html = html.replace("{{%s}}" % k, v)
        html = html.replace("{{year}}", YEAR)

        # Safety: no unresolved placeholders should remain
        leftover = re.findall(r"\{\{[a-z_]+\}\}", html)
        if leftover:
            print(f"WARNING [{slug}]: unresolved placeholders: {set(leftover)}", file=sys.stderr)

        out = ROOT / f"{slug}.html"
        out.write_text(html, encoding="utf-8")
        written.append(out.name)

    write_404(sprite)
    write_sitemap()
    write_robots()
    print("Built:", ", ".join(written) + ", 404.html, sitemap.xml, robots.txt")


def write_404(sprite: str):
    body = read(PAGES_DIR / "404.html").strip()
    html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stránka nenalezena — OLZA OPTIC</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#6b6840">
<link rel="icon" href="{BASE_PATH}/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{BASE_PATH}/assets/css/tokens.css">
<link rel="stylesheet" href="{BASE_PATH}/assets/css/site.css">
</head>
<body>
{sprite}
{body}
</body>
</html>
"""
    (ROOT / "404.html").write_text(html, encoding="utf-8")


def write_sitemap():
    today = datetime.date.today().isoformat()
    urls = []
    for page in PAGES:
        loc = SITE_BASE + ("/" if page["slug"] == "index" else f"/{page['slug']}.html")
        pri = "1.0" if page["slug"] == "index" else "0.8"
        urls.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>monthly</changefreq>\n    <priority>{pri}</priority>\n  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")


def write_robots():
    txt = f"User-agent: *\nAllow: /\n\nSitemap: {SITE_BASE}/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(txt, encoding="utf-8")


if __name__ == "__main__":
    build()
