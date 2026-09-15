#!/usr/bin/env python3
"""The single-supplier exposures are not seventeen independent risks.

    python examples/correlated_exposure.py

Reads the latest derived partition and writes
examples/charts/correlated-exposure.svg.

MUST BE READ WITH single-supplier-exposure.svg. That chart says 17 of 56
vaccine types rest on one manufacturer, and a reader will take those as
seventeen separate things that could go wrong. They are not: one company is the
sole maker for six of them, and two regulators sign off sixteen of the
seventeen. This chart is the correction, and without it the first one overstates
how diversified the failure modes are.

One dot per exposed vaccine type, grouped by its sole manufacturer and coloured
by the regulator responsible for it -- both columns the capture already has,
neither needing the archive.
"""
from __future__ import annotations

import collections
import csv
import glob
import gzip
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples/charts/correlated-exposure.svg"

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8880"
GRID, RULE = "#f0efe9", "#e3e2db"
A, B, OTHER = "#1b4f8a", "#d17b00", "#8a8880"   # validated pair + neutral
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'
W, H = 1020, 580
L, T = 330, 190


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def short(n):
    for long, s in (("Central Drugs Standard Control Organization", "CDSCO (India)"),
                    ("European Medicines Agency", "EMA"),
                    ("Federal Agency for Medicines and Health Products", "FAMHP (Belgium)")):
        if n.startswith(long):
            return s
    return n[:24]


def main() -> int:
    f = sorted(glob.glob(str(ROOT / "derived/observations/*.csv.gz")))[-1]
    prod = collections.defaultdict(dict)
    for r in csv.DictReader(gzip.open(f, "rt")):
        if r["metric"] in ("rows_on_page", "next_page_present"):
            continue
        prod[r["entity_id"]][r["metric"]] = r["value"]
    mfr, nra = collections.defaultdict(set), collections.defaultdict(set)
    for p in prod.values():
        t = p.get("vaccine_type") or "(unstated)"
        mfr[t].add(p.get("manufacturer") or "?")
        nra[t].add(p.get("responsible_nra") or "?")
    exposed = [t for t, v in mfr.items() if len(v) == 1]
    by = collections.defaultdict(list)
    for t in exposed:
        by[list(mfr[t])[0]].append(t)
    order = sorted(by, key=lambda m: (-len(by[m]), m))
    reg = collections.Counter(n for t in exposed for n in nra[t])
    top2 = [r for r, _ in reg.most_common(2)]
    colour = {top2[0]: A, top2[1]: B}

    lane = (H - T - 74) / len(order)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family=\'{FONT}\'>',
         f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>']
    o.append(f'<text x="34" y="44" font-size="21" font-weight="600" fill="{INK}">'
             f'Those {len(exposed)} exposed types are really about '
             f'{len(order)} &#8212; one firm is sole maker for {len(by[order[0]])}'
             f'</text>')
    o.append(f'<text x="34" y="70" font-size="13.5" fill="{INK2}">'
             f'The {len(exposed)} vaccine types with a single prequalified '
             f'manufacturer, grouped by who that manufacturer is. One dot per '
             f'type.</text>')
    o.append(f'<text x="34" y="89" font-size="13.5" fill="{INK2}">'
             f'<tspan font-weight="600" fill="{INK}">Read this with the exposure '
             f'chart, never instead of it.</tspan> That one counts {len(exposed)} '
             f'risks; this one shows they are not independent.</text>')
    o.append(f'<text x="34" y="112" font-size="13.5" fill="{INK2}">'
             f'Colour is the regulator responsible. Two of the twenty-two cover '
             f'{reg[top2[0]] + reg[top2[1]]} of {len(exposed)}, so a '
             f'REGULATOR-level problem is not a product-level problem.</text>')

    lx = 34
    for i, (name, col) in enumerate([(short(top2[0]), A), (short(top2[1]), B),
                                     ("other", OTHER)]):
        o.append(f'<circle cx="{lx + 6}" cy="{T - 38}" r="6" fill="{col}" '
                 f'fill-opacity="0.75"/>')
        o.append(f'<text x="{lx + 18}" y="{T - 33}" font-size="12" fill="{INK2}">'
                 f'{esc(name)}</text>')
        lx += 34 + len(name) * 7.2

    for i, m in enumerate(order):
        cy = T + lane * (i + 0.5)
        o.append(f'<line x1="{L}" y1="{cy:.1f}" x2="{W - 60}" y2="{cy:.1f}" '
                 f'stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{L - 16}" y="{cy + 5:.1f}" font-size="13" '
                 f'fill="{INK}" text-anchor="end">{esc(m[:38])}</text>')
        for j, t in enumerate(sorted(by[m])):
            c = colour.get(list(nra[t])[0], OTHER)
            o.append(f'<circle cx="{L + 20 + j * 30:.0f}" cy="{cy:.1f}" r="9.5" '
                     f'fill="{c}" fill-opacity="0.75" stroke="{SURFACE}" '
                     f'stroke-width="1.5"/>')
        o.append(f'<text x="{L + 20 + len(by[m]) * 30 + 14:.0f}" y="{cy + 5:.1f}" '
                 f'font-size="12.5" font-weight="600" fill="{MUTED}">'
                 f'{len(by[m])}</text>')

    o.append(f'<text x="34" y="{H - 40}" font-size="12" fill="{MUTED}">'
             f'A problem at the top firm removes {len(by[order[0]])} vaccine '
             f'types that have no other prequalified supplier &#8212; not one.'
             f'</text>')
    o.append(f'<text x="34" y="{H - 23}" font-size="12" fill="{MUTED}">'
             f'One capture. WHO records no withdrawals, so the date any of these '
             f'dots disappears exists only in this archive.</text>')
    o.append("</svg>")
    OUT.write_text("\n".join(o))
    print(f"wrote {OUT}  ({len(exposed)} types across {len(order)} manufacturers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
