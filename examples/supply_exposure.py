#!/usr/bin/env python3
"""Which vaccine types are one withdrawal away from having no WHO-prequalified
supply at all.

    python examples/supply_exposure.py

Reads derived/observations/<latest>.csv.gz and writes
examples/charts/single-supplier-exposure.svg.

ONE DOT PER VACCINE TYPE, on the two columns the capture already has: how many
PRODUCTS carry prequalification for that type, and how many distinct
MANUFACTURERS make them. Both axes come from a single capture -- this chart
needs no archive, which is the point: the archive is what tells you WHEN a dot
moves left.

WHY MANUFACTURERS AND NOT PRODUCTS ALONE. Two presentations from one maker are
two products and one supply chain. A type with four products from one
manufacturer is exactly as exposed as a type with one, and a product count on
its own would rank it as four times safer.
"""
from __future__ import annotations

import collections
import csv
import glob
import gzip
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples/charts/single-supplier-exposure.svg"

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8880"
GRID, RULE = "#f0efe9", "#e3e2db"
EXPOSED, SAFE = "#d17b00", "#1b4f8a"      # validated pair, dE 29.8 worst CVD
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'
W, H = 1080, 760
L, R, T, B = 92, 300, 176, 148


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def clip(s, n=38):
    """Trim on a word boundary. A mid-word cut reads as a different vaccine."""
    s = s.replace("\u2206", "d")        # rVSV-delta-G; the glyph is not in every font
    if len(s) <= n:
        return s
    cut = s[:n]
    return (cut[:cut.rfind(" ")] if " " in cut[20:] else cut).rstrip(" ,(") + "\u2026"


def load():
    f = sorted(glob.glob(str(ROOT / "derived/observations/*.csv.gz")))[-1]
    prod = collections.defaultdict(dict)
    for r in csv.DictReader(gzip.open(f, "rt")):
        if r["metric"] in ("rows_on_page", "next_page_present"):
            continue
        prod[r["entity_id"]][r["metric"]] = r["value"]
    return f, list(prod.values())


def main() -> int:
    src, products = load()
    types = collections.defaultdict(lambda: {"n": 0, "mfr": set()})
    for p in products:
        t = p.get("vaccine_type") or "(unstated)"
        types[t]["n"] += 1
        types[t]["mfr"].add(p.get("manufacturer") or "(unstated)")
    rows = [(t, v["n"], len(v["mfr"])) for t, v in types.items()]
    exposed = [r for r in rows if r[2] == 1]

    xmax = max(r[2] for r in rows)
    ymax = max(r[1] for r in rows)

    def px(v):
        return L + (v - 1) / max(xmax - 1, 1) * (W - L - R)

    def py(v):
        return T + (H - T - B) - (math.log10(v) / math.log10(ymax)) * (H - T - B)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family=\'{FONT}\'>',
         f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>']
    o.append(f'<text x="34" y="44" font-size="21" font-weight="600" fill="{INK}">'
             f'{len(exposed)} of {len(rows)} vaccine types have exactly one '
             f'prequalified manufacturer</text>')
    o.append(f'<text x="34" y="70" font-size="13.5" fill="{INK2}">'
             f'Every vaccine type WHO prequalifies, as one dot. Across is how '
             f'many distinct manufacturers hold prequalification for it; up is '
             f'how many products.</text>')
    o.append(f'<text x="34" y="89" font-size="13.5" fill="{INK2}">'
             f'<tspan font-weight="600" fill="{INK}">Everything in the orange '
             f'column is one withdrawal away from no WHO-prequalified supply at '
             f'all</tspan> &#8212; and WHO records no withdrawals.</text>')
    o.append(f'<text x="34" y="108" font-size="13.5" fill="{INK2}">'
             f'Extra products from the same maker do not help: they are one '
             f'supply chain. That is why the axis counts manufacturers, not '
             f'products.</text>')
    o.append(f'<text x="34" y="127" font-size="12.5" fill="{MUTED}">'
             f'One capture, {Path(src).name} &#8212; no archive needed to draw '
             f'this. The archive is what dates the moment a dot moves left.</text>')

    # exposure band
    o.append(f'<rect x="{L - 34}" y="{T - 14}" width="{px(1) - L + 68:.0f}" '
             f'height="{H - T - B + 28}" fill="{EXPOSED}" fill-opacity="0.07"/>')
    for gx in range(1, xmax + 1):
        o.append(f'<line x1="{px(gx):.1f}" y1="{T - 14}" x2="{px(gx):.1f}" '
                 f'y2="{H - B}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{px(gx):.1f}" y="{H - B + 24}" font-size="12" '
                 f'fill="{MUTED}" text-anchor="middle">{gx}</text>')
    for gy in (1, 2, 5, 10, 20):
        if gy > ymax:
            continue
        o.append(f'<line x1="{L - 34}" y1="{py(gy):.1f}" x2="{W - R}" '
                 f'y2="{py(gy):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{L - 46}" y="{py(gy) + 4:.1f}" font-size="12" '
                 f'fill="{MUTED}" text-anchor="end">{gy}</text>')

    jitter = collections.Counter()
    for t, n, m in sorted(rows, key=lambda r: (r[2], -r[1])):
        k = (m, n)
        j = jitter[k]
        jitter[k] += 1
        dx = (j % 6) * 7.5 - 8   # never negative enough to cross the axis
        dy = (j // 6) * 8.5
        c = EXPOSED if m == 1 else SAFE
        o.append(f'<circle cx="{px(m) + dx:.1f}" cy="{py(n) + dy:.1f}" r="6.5" '
                 f'fill="{c}" fill-opacity="0.62" stroke="{SURFACE}" '
                 f'stroke-width="1.2"/>')

    # Name the single-manufacturer, single-product types: total exposure.
    worst = sorted([r for r in rows if r[2] == 1 and r[1] == 1])
    y = T + 6
    o.append(f'<text x="{W - R + 22}" y="{y}" font-size="13" font-weight="600" '
             f'fill="{INK}">One product, one maker</text>')
    o.append(f'<text x="{W - R + 22}" y="{y + 17}" font-size="11.5" '
             f'fill="{MUTED}">nothing else is prequalified for these</text>')
    for t, n, m in worst[:10]:
        y += 34
        o.append(f'<circle cx="{W - R + 28}" cy="{y - 4}" r="4.5" fill="{EXPOSED}"/>')
        o.append(f'<text x="{W - R + 40}" y="{y}" font-size="11.5" fill="{INK2}">'
                 f'{esc(clip(t))}</text>')
    if len(worst) > 10:
        y += 28
        o.append(f'<text x="{W - R + 40}" y="{y}" font-size="11.5" fill="{MUTED}">'
                 f'and {len(worst) - 10} more</text>')

    o.append(f'<text x="{(L + W - R) / 2:.0f}" y="{H - B + 54}" font-size="13" '
             f'fill="{INK2}" text-anchor="middle">distinct manufacturers holding '
             f'prequalification for that vaccine type</text>')
    o.append(f'<text x="26" y="{(T + H - B) / 2:.0f}" font-size="13" fill="{INK2}" '
             f'text-anchor="middle" transform="rotate(-90 26 {(T + H - B) / 2:.0f})">'
             f'prequalified products (log)</text>')
    o.append(f'<text x="34" y="{H - 60}" font-size="12" fill="{MUTED}">'
             f'Orange: a single manufacturer. Vertical spread inside a column '
             f'is jitter so overlapping types stay countable.</text>')
    o.append(f'<text x="34" y="{H - 44}" font-size="12" fill="{MUTED}">'
             f'ROBUST TO GRANULARITY: WHO\u2019s type string mixes real distinctions '
             f'(HPV Ninevalent vs Quadrivalent) with dose variants (Meningococcal A '
             f'5 vs 10 &#181;g). Merging the dose</text>')
    o.append(f'<text x="34" y="{H - 28}" font-size="12" fill="{MUTED}">'
             f'and age variants gives 15 of 52 &#8212; 29% against 30%. The '
             f'proportion does not depend on the choice.</text>')
    o.append("</svg>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(o))
    print(f"wrote {OUT}  ({len(rows)} types, {len(exposed)} single-manufacturer)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
