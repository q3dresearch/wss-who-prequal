#!/usr/bin/env python3
"""Which vaccine types you cannot get in a small vial.

    python examples/vial_sizes.py

Writes examples/charts/vial-sizes.svg.

WHY THIS MATTERS OPERATIONALLY. A multi-dose vial must be used within hours of
opening or discarded, so a programme vaccinating scattered or low-turnout
populations throws away most of a 20-dose vial to give one child. WHO's
open-vial policy exists precisely because of this. A vaccine type with no
single-dose presentation prequalified anywhere leaves a programme no way out of
that trade.

THE FORM IS A RANGE, NOT A SCATTER. Doses per vial is a small discrete set --
1, 2, 3, 4, 5, 10, 17, 20, 50 -- and each vaccine type offers a SET of them.
Plotting min against max would be two discrete axes and the same collision
problem that sank an earlier chart here. A horizontal span from the smallest to
the largest presentation available, one row per type, draws the same two numbers
as position and length and stays readable. Types whose span never reaches 1 are
the finding.
"""
from __future__ import annotations

import collections
import csv
import glob
import gzip
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples/charts/vial-sizes.svg"

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8880"
GRID, BAND = "#f0efe9", "#fbf1e4"
NOSMALL, OK = "#d17b00", "#1b4f8a"
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'
W, H = 1080, 760
L, R, T, B = 340, 150, 186, 84


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def clip(s, n=40):
    s = s.replace("∆", "d")
    if len(s) <= n:
        return s
    cut = s[:n]
    return (cut[:cut.rfind(" ")] if " " in cut[20:] else cut).rstrip(" ,(") + "…"


def main() -> int:
    f = sorted(glob.glob(str(ROOT / "derived/observations/*.csv.gz")))[-1]
    prod = collections.defaultdict(dict)
    for r in csv.DictReader(gzip.open(f, "rt")):
        if r["series_id"] != "who.pq.vaccines":
            continue
        prod[r["entity_id"]][r["metric"]] = r["value"]
    types = collections.defaultdict(set)
    for p in prod.values():
        d = p.get("doses", "")
        if d.isdigit():
            types[p.get("vaccine_type") or "(unstated)"].add(int(d))
    rows = [(t, min(v), max(v), sorted(v)) for t, v in types.items() if v]
    nosmall = [r for r in rows if r[1] >= 10]
    # Worst first: no small vial, then by how large the smallest option is.
    rows.sort(key=lambda r: (-(r[1] >= 10), -r[1], -r[2]))
    rows = rows[:26]

    lo, hi = 1, max(r[2] for r in rows)
    lane = (H - T - B) / len(rows)

    def px(v):
        return L + (math.log10(v) / math.log10(hi)) * (W - L - R)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family=\'{FONT}\'>',
         f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>']
    o.append(f'<text x="34" y="44" font-size="21" font-weight="600" fill="{INK}">'
             f'{len(nosmall)} vaccine types cannot be had in a vial smaller than '
             f'ten doses</text>')
    o.append(f'<text x="34" y="70" font-size="13.5" fill="{INK2}">'
             f'Each row is a vaccine type; the bar runs from the smallest to the '
             f'largest vial WHO has prequalified for it. Worst first, top '
             f'{len(rows)} of {len(types)}.</text>')
    o.append(f'<text x="34" y="89" font-size="13.5" fill="{INK2}">'
             f'<tspan font-weight="600" fill="{INK}">An opened multi-dose vial '
             f'must be used within hours or discarded.</tspan> A type whose bar '
             f'never reaches 1 leaves a programme no way out of that.</text>')
    o.append(f'<text x="34" y="108" font-size="13.5" fill="{INK2}">'
             f'All five oral polio variants and BCG are in the orange group '
             f'&#8212; exactly the vaccines given in outreach settings with low '
             f'daily turnout.</text>')
    o.append(f'<text x="34" y="131" font-size="12.5" fill="{MUTED}">'
             f'One capture. {sum(1 for p in prod.values() if p.get("doses", "").isdigit() and int(p["doses"]) >= 10)} '
             f'of 285 products are 10-dose or larger.</text>')

    o.append(f'<rect x="{L - 16}" y="{T - 12}" width="{W - L - R + 32}" '
             f'height="{lane * len(nosmall) + 6:.0f}" fill="{BAND}"/>')
    for gx in (1, 2, 5, 10, 20, 50):
        if gx > hi:
            continue
        o.append(f'<line x1="{px(gx):.1f}" y1="{T - 12}" x2="{px(gx):.1f}" '
                 f'y2="{H - B}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{px(gx):.1f}" y="{H - B + 22}" font-size="12" '
                 f'fill="{MUTED}" text-anchor="middle">{gx}</text>')

    for i, (t, mn, mx, all_) in enumerate(rows):
        cy = T + lane * (i + 0.5)
        c = NOSMALL if mn >= 10 else OK
        o.append(f'<text x="{L - 18}" y="{cy + 4:.1f}" font-size="12" '
                 f'fill="{INK if mn >= 10 else INK2}" text-anchor="end">'
                 f'{esc(clip(t))}</text>')
        if mx > mn:
            o.append(f'<line x1="{px(mn):.1f}" y1="{cy:.1f}" x2="{px(mx):.1f}" '
                     f'y2="{cy:.1f}" stroke="{c}" stroke-width="3" '
                     f'stroke-opacity="0.35" stroke-linecap="round"/>')
        for d in all_:
            o.append(f'<circle cx="{px(d):.1f}" cy="{cy:.1f}" r="5.5" fill="{c}" '
                     f'fill-opacity="0.8" stroke="{SURFACE}" stroke-width="1.2"/>')
        o.append(f'<text x="{W - R + 12}" y="{cy + 4:.1f}" font-size="11.5" '
                 f'fill="{MUTED}">{"/".join(str(x) for x in all_)}</text>')

    o.append(f'<text x="{W - R + 12}" y="{T - 16}" font-size="11.5" '
             f'fill="{MUTED}">sizes</text>')
    o.append(f'<text x="{(L + W - R) / 2:.0f}" y="{H - B + 52}" font-size="13" '
             f'fill="{INK2}" text-anchor="middle">doses per vial (log)</text>')
    o.append(f'<text x="34" y="{H - 26}" font-size="12" fill="{MUTED}">'
             f'Orange: no presentation under ten doses. One dot per distinct vial '
             f'size prequalified for that type.</text>')
    o.append("</svg>")
    OUT.write_text("\n".join(o))
    print(f"wrote {OUT}  ({len(types)} types, {len(nosmall)} with no small vial)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
