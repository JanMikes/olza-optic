#!/usr/bin/env python3
"""Bake the client-editable opening hours into the static pages.

The client maintains a small table per branch in the BiteIT micro-content
admin. This pulls those tables and writes them straight into the HTML —
the visible footer block and the JSON-LD openingHoursSpecification — so
the published pages stay fully static: crawlers, rich results and users
without JS all see the real hours. Run from CI (see
.github/workflows/sync-opening-hours.yml); safe to run locally too.

Exits non-zero on any problem so a broken feed can never publish empty
or half-written hours.
"""

import html
import json
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

CUSTOMER = "538b6d648927b777cd75e266dcefe85d"
API = "https://job3.biteit.cz/fapi/content/{customer}/{entry}"

# data-microcontent hash -> human label, used only for log output
BRANCHES = {
    "6574c4d9487f787a79d1a0684447b8b9bfc45853": "Český Těšín",
    "873c81d179db429f4f0bf1efa3ca39e520ae613e": "Třinec",
}

# The branch the structured data on index.html describes (Dukelská 1305/1)
SCHEMA_BRANCH = "6574c4d9487f787a79d1a0684447b8b9bfc45853"
SCHEMA_PAGE = "index.html"

DAYS = {
    "pondělí": "Monday", "pondeli": "Monday", "po": "Monday",
    "úterý": "Tuesday", "utery": "Tuesday", "út": "Tuesday", "ut": "Tuesday",
    "středa": "Wednesday", "streda": "Wednesday", "st": "Wednesday",
    "čtvrtek": "Thursday", "ctvrtek": "Thursday", "čt": "Thursday", "ct": "Thursday",
    "pátek": "Friday", "patek": "Friday", "pá": "Friday", "pa": "Friday",
    "sobota": "Saturday", "so": "Saturday",
    "neděle": "Sunday", "nedele": "Sunday", "ne": "Sunday",
}

CLOSED = {"zavřeno", "zavreno", "closed", "-", "–", "—", ""}

ROOT = Path(__file__).resolve().parent.parent


class TableReader(HTMLParser):
    """Collect the (label, value) pairs of a two-column CMS table."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag == "td" and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag == "td" and self._cell is not None:
            self._row.append("".join(self._cell).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if len(self._row) >= 2:
                self.rows.append((self._row[0], self._row[1]))
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def fetch(entry):
    url = API.format(customer=CUSTOMER, entry=entry)
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, ValueError, OSError) as exc:
        sys.exit("error: cannot read %s from the CMS (%s)" % (entry, exc))

    content = (payload.get("data") or {}).get("content")
    if not isinstance(content, str) or "<td" not in content:
        sys.exit("error: CMS entry %s has no usable table" % entry)
    return content


def read_rows(entry):
    parser = TableReader()
    parser.feed(fetch(entry))
    rows = [(label, value) for label, value in parser.rows if label or value]
    if not rows:
        sys.exit("error: CMS entry %s produced no rows" % entry)
    return rows


def normalise(label, value):
    """Keep the client's wording, apply the site's typography."""
    label = re.sub(r"[\s:]+$", "", label.replace("\xa0", " ")).strip()
    value = re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()
    value = re.sub(r"\s*[-–—]\s*", "–", value)
    return label + ":", value


def render_table(rows):
    cells = "".join(
        "<tr><td>%s</td><td>%s</td></tr>" % (html.escape(label), html.escape(value))
        for label, value in rows
    )
    return '<table class="opening-hours"><tbody>%s</tbody></table>' % cells


def to_schema(rows):
    """Group the rows into schema.org OpeningHoursSpecification entries."""
    specs = []
    for label, value in rows:
        day = DAYS.get(label.rstrip(":").strip().lower())
        if not day:
            print("  note: %r is not a single weekday, left out of JSON-LD" % label)
            continue
        if value.strip().lower() in CLOSED:
            continue
        times = re.match(r"^(\d{1,2})[:.](\d{2})–(\d{1,2})[:.](\d{2})$", value)
        if not times:
            print("  note: %r is not a plain time range, left out of JSON-LD" % value)
            continue
        opens = "%02d:%s" % (int(times.group(1)), times.group(2))
        closes = "%02d:%s" % (int(times.group(3)), times.group(4))
        if specs and specs[-1]["opens"] == opens and specs[-1]["closes"] == closes:
            specs[-1]["dayOfWeek"].append(day)
        else:
            specs.append({
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [day],
                "opens": opens,
                "closes": closes,
            })
    if not specs:
        sys.exit("error: no opening hours could be read for the structured data")
    return specs


def replace_container(page, source, entry, table):
    pattern = re.compile(
        r'(<div class="opening-hours-container" data-microcontent="%s"[^>]*>)(.*?)(</div>)' % entry,
        re.S,
    )
    if not pattern.search(source):
        sys.exit("error: %s has no container for CMS entry %s" % (page, entry))
    return pattern.sub(lambda m: m.group(1) + table + m.group(3), source, count=1)


def replace_schema(page, source, specs):
    start = source.find('"openingHoursSpecification":')
    if start == -1:
        sys.exit("error: %s has no openingHoursSpecification to update" % page)

    cursor = source.index("[", start)
    depth = 0
    for end, char in enumerate(source[cursor:], cursor):
        depth += (char == "[") - (char == "]")
        if depth == 0:
            break
    else:
        sys.exit("error: %s has a malformed openingHoursSpecification" % page)

    rendered = json.dumps(specs, ensure_ascii=False, separators=(",", ":"))
    return source[:cursor] + rendered + source[end + 1:]


def main():
    tables = {}
    schema = None
    for entry, label in BRANCHES.items():
        rows = [normalise(*row) for row in read_rows(entry)]
        print("%s: %s" % (label, ", ".join("%s %s" % row for row in rows)))
        tables[entry] = render_table(rows)
        if entry == SCHEMA_BRANCH:
            schema = to_schema(rows)

    changed = []
    for page in sorted(ROOT.glob("*.html")):
        source = original = page.read_text(encoding="utf-8")
        for entry, table in tables.items():
            if 'data-microcontent="%s"' % entry in source:
                source = replace_container(page.name, source, entry, table)
        if page.name == SCHEMA_PAGE:
            source = replace_schema(page.name, source, schema)
        if source != original:
            page.write_text(source, encoding="utf-8")
            changed.append(page.name)

    print("updated: %s" % (", ".join(changed) if changed else "nothing, already current"))


if __name__ == "__main__":
    main()
