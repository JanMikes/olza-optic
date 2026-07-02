# OLZA OPTIC — statický web

Statický web oční optiky **OLZAOPTIC s.r.o.** (Český Těšín), hostovaný na GitHub Pages
na adrese <https://janmikes.github.io/olza-optic/>.

## Původ

Stránky jsou 1:1 předrenderované z návrhových sekcí design systému
(`ui_kits/sections/` — `Landing.html`, `O-nas.html`, `Mereni-zraku.html`,
`Bryle.html`, `Diagnostika-sucheho-oka.html`). Původní sekce jsou React komponenty
renderované design systémem; zde jsou zachyceny do čistého statického HTML
(bez Reactu/Babelu za běhu) s doplněnou responzivní vrstvou pro mobil.

## Struktura

- `index.html` — úvodní one-page (Landing) s kotvami `#o-nas`, `#sluzby`, `#cocky`, `#suche-oko`, `#galerie`, `#kontakt`
- `o-nas.html`, `mereni-zraku.html`, `bryle.html`, `diagnostika-sucheho-oka.html` — podstránky
- `404.html` — chybová stránka
- `assets/css/` — design tokeny (`styles.css` + `tokens/`) a responzivní vrstva (`responsive.css`)
- `assets/js/site.js` — mobilní menu, „načíst další" v galerii, potvrzení formuláře
- `assets/*.jpg` — optimalizované fotografie
- `sitemap.xml`, `robots.txt`, `.nojekyll`

Web funguje i bez JavaScriptu; JS pouze doplňuje interakce.
