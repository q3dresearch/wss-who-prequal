#!/usr/bin/env python3
"""How often does WHO change a product's slug without the product changing?

    python examples/rename_rate.py --out rename.csv

WHY THIS BLOCKS EVERYTHING ELSE. This archive keys on the product slug from
/prequal/vaccines/p/<slug>. On 2026-09-15 that key was shown to be unstable:
`engerix` became `engerix-b` while the product stayed listed under the same
commercial name. A rename is indistinguishable from a departure followed by an
arrival, and departures are the only thing this archive exists to record. So the
rename RATE decides whether the departure measurement is possible at all, and it
has to be measured before any departure count is believed.

THE SOURCE IS SOMEBODY ELSE'S ARCHIVE. web.archive.org holds roughly monthly
captures of this list from October 2023. They are PAGE 1 OF 6 -- the
alphabetical head, about 50 of 285 products -- which is useless for counting
departures but fine for counting renames, because a rename is visible in any
sample that contains the product before and after.

THE MATCH KEY WAS COUNTED BEFORE IT WAS USED, and the obvious one fails.
Commercial name + manufacturer + prequalification date sounds like an identity
and is not: on the 2026-09 capture it gives 205 distinct keys for 285 products,
with 140 rows sitting in a collision. Two presentations of one brand,
prequalified the same day, are different products sharing a triple -- and a
non-unique key manufactures renames, which is precisely the error being
measured. Adding fields until the collisions stop:

    name+maker+date                       205 / 285   140 rows colliding
    + presentation                        210 / 285   133
    + doses                               282 / 285     6
    + vaccine_type                        285 / 285     0

So the key is all six. Every one is already emitted by the parser. Uniqueness is
re-counted on each capture rather than assumed, and ambiguous rows are dropped
and reported -- an archived page may not be as clean as today's.
"""
from __future__ import annotations

import argparse
import collections
import csv
import re
import subprocess
import time
from html import unescape
from pathlib import Path

RECIPE = Path(__file__).resolve().parents[1]
UA = "wss/0.6.49 (contact: https://github.com/q3dresearch/wss-who-prequal)"
LIST = "https://extranet.who.int/prequal/vaccines/prequalified-vaccines"
CDX = ("https://web.archive.org/cdx/search/cdx?url=extranet.who.int/prequal/"
       "vaccines/prequalified-vaccines*&output=text&fl=timestamp,statuscode"
       "&collapse=timestamp:6&limit=60")

COMMENT = re.compile(r"<!--.*?-->", re.S)
ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
TAGS = re.compile(r"<[^>]*>")
SLUG = re.compile(r'href="[^"]*?/prequal/vaccines/p/([^"#?]+)"')
ISO = re.compile(r'<time[^>]+datetime="(\d{4}-\d{2}-\d{2})')


def _text(cell: str) -> str:
    return re.sub(r"\s+", " ", unescape(TAGS.sub(" ", COMMENT.sub("", cell)))).strip()


def fetch(url: str, tries: int = 3) -> str:
    for i in range(tries):
        p = subprocess.run(["curl", "-sSL", "--max-time", "150", "-A", UA, url],
                           capture_output=True, text=True)
        if len(p.stdout) > 2000:
            return p.stdout
        time.sleep(4 * (i + 1))
    return ""


def products(html: str) -> dict:
    """triple -> slug, for every row that parses. Ambiguous triples dropped."""
    seen, dupes = {}, set()
    for m in ROW.finditer(html):
        block = m.group(1)
        cells = [_text(c) for c in CELL.findall(block)]
        if len(cells) < 7:
            continue
        s = SLUG.search(block)
        iso = ISO.search(block)
        if not s or not iso:
            continue
        # cells: date, type, commercial name, presentation, doses, manufacturer, NRA
        key = (cells[2].lower(), cells[5].lower(), iso.group(1),
               cells[3].lower(), cells[4].lower(), cells[1].lower())
        if key in seen:
            dupes.add(key)
        seen[key] = s.group(1)
    for k in dupes:
        seen.pop(k, None)
    return seen, len(dupes)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(RECIPE / "rename.csv"))
    ap.add_argument("--max", type=int, default=24)
    a = ap.parse_args()

    cdx = fetch(CDX)
    # web.archive.org goes down. It was serving on 2026-09-15 and returning
    # "Temporarily Offline" HTML on 2026-09-16. An HTML body where CDX text is
    # expected parses to zero captures, which looks identical to "this page was
    # never archived" -- so say which it is rather than letting the caller
    # assume the page has no history.
    if "<html" in cdx[:400].lower():
        print("  web.archive.org returned HTML, not CDX -- it is offline or "
              "rate-limiting.\n  This is NOT 'no captures exist'. Retry later.")
        return 2
    stamps = [l.split()[0] for l in cdx.strip().splitlines()
              if l.split()[1:2] == ["200"]][: a.max]
    print(f"  {len(stamps)} archived captures with status 200")
    if not stamps:
        print("  nothing archived for this URL -- the rename rate cannot be "
              "measured from someone else's archive, only from our own captures "
              "once two exist.")
        return 1

    snaps = []
    for ts in stamps:
        html = fetch(f"https://web.archive.org/web/{ts}id_/{LIST}")
        if not html:
            print(f"    {ts}  unfetchable, skipped")
            continue
        p, amb = products(html)
        snaps.append((ts, p))
        print(f"    {ts}  {len(p):>3} products keyed"
              + (f"  ({amb} ambiguous triple(s) dropped)" if amb else ""))
        time.sleep(1.5)

    # today, from the live archive's own derived table
    import glob, gzip
    latest = sorted(glob.glob(str(RECIPE / "derived/observations/*.csv.gz")))[-1]
    cur = collections.defaultdict(dict)
    for r in csv.DictReader(gzip.open(latest, "rt")):
        if r["series_id"] == "who.pq.vaccines":
            cur[r["entity_id"]][r["metric"]] = r["value"]
    today = {}
    for slug, v in cur.items():
        k = (v.get("commercial_name", "").lower(), v.get("manufacturer", "").lower(),
             v.get("prequalification_date", ""), v.get("presentation", "").lower(),
             v.get("doses", "").lower(), v.get("vaccine_type", "").lower())
        today[k] = slug
    snaps.append(("today", today))
    print(f"    today      {len(today):>3} products keyed (full 6 pages)")

    rows, renames = [], []
    for (t1, A), (t2, B) in zip(snaps, snaps[1:]):
        both = set(A) & set(B)
        ch = [k for k in both if A[k] != B[k]]
        rows.append({"from": t1, "to": t2, "matched": len(both),
                     "slug_changed": len(ch),
                     "rate": round(len(ch) / len(both), 4) if both else ""})
        for k in ch:
            renames.append({"from": t1, "to": t2, "commercial_name": k[0],
                            "manufacturer": k[1], "prequalification_date": k[2],
                            "old_slug": A[k], "new_slug": B[k]})
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    if renames:
        rp = Path(a.out).with_name("renames.csv")
        with open(rp, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(renames[0]))
            w.writeheader()
            w.writerows(renames)

    tm = sum(r["matched"] for r in rows)
    tc = sum(r["slug_changed"] for r in rows)
    print(f"\n  {tc} slug change(s) across {tm} matched product-intervals "
          f"= {tc / tm:.2%}" if tm else "\n  nothing matched")
    for r in renames[:12]:
        print(f"    {r['from']}->{r['to']}  {r['old_slug'][:28]:<30} -> {r['new_slug'][:28]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
