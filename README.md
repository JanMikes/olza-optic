# OLZA OPTIC — webové stránky

Statický web optiky **OLZAOPTIC s.r.o.** v Českém Těšíně, hostovaný na GitHub Pages.

Moderní, vzdušný, boutique vzhled podle značkového design systému OLZA OPTIC:
olivová moss `#6b6840`, okrová `#cf8d32`, sage a camel nad teplými neutrály, písmo
Open Sans, organický „blob" motiv a teplá fotografie prodejny.

## Stránky

| Soubor | Stránka |
| --- | --- |
| `index.html` | Úvod — hero, o nás, služby, kontaktní čočky, suché oko, fotogalerie, recenze, kontakt |
| `o-nas.html` | O nás — příběh, zakladatelka, čísla, hodnoty |
| `mereni-zraku.html` | Měření zraku — průběh vyšetření + jak měří Visionix VX 120+ |
| `bryle.html` | Brýle — zhotovení, opravy, čištění ultrazvukem |
| `suche-oko.html` | Diagnostika suchého oka — příznaky, vyšetření, rezervace |
| `404.html` | Chybová stránka |

Sekce kontaktu (`#kontakt`) je v patičce na každé stránce.

## Struktura

```
.
├── index.html, o-nas.html, …      # vygenerované statické stránky (servíruje GitHub Pages)
├── 404.html, sitemap.xml, robots.txt
├── assets/
│   ├── css/tokens.css             # design tokeny (barvy, typografie, spacing, stíny)
│   ├── css/site.css               # styly komponent a responzivita
│   ├── js/site.js                 # mobilní menu, fotogalerie, formulář (progresivní vylepšení)
│   ├── logos/  brand/  photos/    # SVG loga, blob grafika, optimalizované fotografie
│   └── favicon.svg
└── src/                           # zdroje generátoru (nejsou servírovány)
    ├── build.py                   # generátor statických stránek
    ├── partials/                  # layout, hlavička, patička, ikonový sprite
    └── pages/                     # obsah jednotlivých stránek (<main>)
```

Web je **plně statický** — žádný runtime, žádné externí JS závislosti. Funguje i bez
JavaScriptu (ten jen přidává mobilní menu, „načíst další fotografie" a potvrzení formuláře).
Jediná externí závislost je Open Sans z Google Fonts (na přání značky).

## Úprava obsahu / přegenerování

Stránky jsou složené ze sdílených partials, aby se hlavička/patička/ikony nemusely
opakovat ručně. Po úpravě čehokoli v `src/` web přegenerujete:

```bash
python3 src/build.py
```

Skript složí `src/partials/layout.html` + `src/partials/*` + `src/pages/<stránka>.html`
do hotových `*.html` v kořeni a zároveň vytvoří `404.html`, `sitemap.xml` a `robots.txt`.
Vygenerované HTML je samostatné (ikonový sprite je vložen inline), takže funguje i při
otevření přes `file://`.

> Pouze upravujete-li styly v `assets/css/*` nebo skripty v `assets/js/*`, generátor
> spouštět nemusíte — ty se servírují přímo.

### Lokální náhled

```bash
python3 -m http.server 8000
# otevřete http://localhost:8000/
```

## Nasazení na GitHub Pages

Repozitář `JanMikes/olza-optic`, web běží jako *project page* na
`https://janmikes.github.io/olza-optic/`.

1. V **Settings → Pages** zvolte **Deploy from a branch**, branch `main`, složka `/ (root)`.
2. Soubor `.nojekyll` zajistí, že GitHub Pages servíruje soubory beze změn.
3. Všechny odkazy mezi stránkami jsou **relativní**, takže fungují i v podadresáři `/olza-optic/`.

Pokud později nasadíte na vlastní doménu, upravte `SITE_BASE` v `src/build.py`
(ovlivňuje `canonical`, Open Graph, `sitemap.xml`) a přegenerujte.

## Fotografie a obsah

Fotografie pocházejí z dodaných materiálů a jsou optimalizované pro web (zmenšené,
komprimované). Veškerá in-world česká kopie (názvy služeb, CTA, recenze) vychází
ze zadání a je reprezentativní — **přesné znění a kontaktní údaje potvrďte s týmem OLZA OPTIC**.
