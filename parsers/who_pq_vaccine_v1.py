"""who-pq-vaccine.v1 — WHO's list of prequalified vaccines, one row per product.

WHAT THIS ARCHIVE IS FOR. The page says who holds prequalification TODAY. WHO
removes products from it -- its own procedures page has a section headed
"Withdrawal from the list of WHO-prequalified vaccines" -- and records the
removal nowhere. So the only question this parser has to serve well is
PRESENCE: which product ids were on the list on which date. Everything else is
an attribute of a row that happens to be there.

THE KEY IS THE SLUG, NOT THE NAME. Each row links to /prequal/vaccines/p/<slug>
-- `abrysvo`, `pneubevax-14r`, and `bevacr-0` / `bevacr-1` for two presentations
of one brand. That is publisher-minted and it distinguishes presentations, which
a name would not. Hashing commercial name + manufacturer was the alternative and
it makes a rename look like a departure, which is the one event this archive
exists to catch.

THE HTML IS FULL OF THEME DEBUG. This Drupal build ships
`<!-- THEME DEBUG -->`, `FILE NAME SUGGESTIONS` and `BEGIN OUTPUT from ...`
comments INSIDE every cell. Strip comments before tags or the cell text comes
out as a paragraph of template paths.

`<time datetime>` CARRIES A SPURIOUS TIME. The attribute reads
`2025-01-16T17:37:05+01:00` while the cell displays `16/01/2025`. The
time-of-day is a record-editing timestamp, not an hour of prequalification.
Only the date part is meaningful and only the date part is emitted.

NEVER GREP THIS PAGE FOR STATUS WORDS. "withdraw" appears twelve times in the
HTML and every one is the EU cookie banner's "Withdraw consent" button. A
status read that way would invent withdrawals on every capture.

GRAIN. One endpoint is one PAGE of fifty, not the feed. So the page-level
metrics below are keyed on the page and never claim a list total -- a per-file
parser that emits a feed total is wrong the moment one page fails its gate.
"""

import re

from wss import derive

PARSER_VERSION = "1"

COMMENT = re.compile(r"<!--.*?-->", re.S)
ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
TAGS = re.compile(r"<[^>]*>")
SLUG = re.compile(r'href="/prequal/vaccines/p/([^"#?]+)"')
ISO = re.compile(r'<time[^>]+datetime="(\d{4}-\d{2}-\d{2})')
PAGE = re.compile(r"[?&]page=(\d+)")
# Drupal's pager. `rel="next"` is the machine-readable half; the visible
# "Next page" text is themed and would move with a theme change.
NEXT = re.compile(r'rel="next"', re.I)

# The seven columns, in the order the view renders them.
COLUMNS = ("prequalification_date", "vaccine_type", "commercial_name",
           "presentation", "doses", "manufacturer", "responsible_nra")


def _text(cell: str) -> str:
    return re.sub(r"\s+", " ", TAGS.sub(" ", COMMENT.sub("", cell))).strip()


def parse(body: bytes, ctx: derive.ParseContext):
    html = body.decode("utf-8", errors="replace")
    page = PAGE.search(ctx.url)
    page_id = f"page-{page.group(1)}" if page else "page-0"

    rows = 0
    for match in ROW.finditer(html):
        block = match.group(1)
        cells = CELL.findall(block)
        if len(cells) < len(COLUMNS):
            continue
        slug = SLUG.search(block)
        if not slug:
            # No product link means no stable identity. Skipping is the honest
            # choice: a hashed name would enter the archive as a new entity on
            # the next rename and read as one departure plus one arrival.
            continue
        entity = slug.group(1)
        rows += 1

        values = [_text(c) for c in cells[:len(COLUMNS)]]
        iso = ISO.search(block)

        yield derive.Observation(entity_id=entity, metric="listed", value=1,
                                 unit="presence")
        if iso:
            yield derive.Observation(entity_id=entity,
                                     metric="prequalification_date",
                                     value=iso.group(1), unit="date")
        for name, value in zip(COLUMNS[1:], values[1:]):
            if value:
                yield derive.Observation(entity_id=entity, metric=name,
                                         value=value, unit="text")

    # Page-level, keyed on the page. `next_page_present` on the LAST configured
    # page is the truncation alarm: the list grew past the endpoints in the
    # registry and a product is being missed silently.
    yield derive.Observation(entity_id=page_id, metric="rows_on_page",
                             value=rows, unit="count")
    yield derive.Observation(entity_id=page_id, metric="next_page_present",
                             value=1 if NEXT.search(html) else 0, unit="bool")


derive.register("who-pq-vaccine.v1", parse, PARSER_VERSION)
