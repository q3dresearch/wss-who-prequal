#!/usr/bin/env python3
"""Who makes the vaccines, and who vouches for them — the same crosstab.

    python examples/oversight_matrix.py

Writes examples/charts/oversight-matrix.svg.

A HEATMAP BECAUSE THE DATA IS A DENSE DISCRETE CROSSTAB. Manufacturer and
regulator are both categorical with no order, and the cell value is a count.
That is a matrix, and drawing it as markers on two discrete axes forces jitter
to stop dots colliding -- which is the tell that the form was wrong. Colour is a
single hue light-to-dark because the quantity is magnitude, not category.

WHAT IT SHOWS THAT THE OTHER CHARTS CANNOT. The concentration on the two axes
is not two risks. India's CDSCO is the responsible authority for 130 of 285
products, and 107 of those 130 come from just two manufacturers. A regulator
problem and a manufacturer problem would land on the same cells.
"""
from __future__ import annotations

import collections
import csv
import glob
import gzip
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples/charts/oversight-matrix.svg"

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8880"
GRID, EMPTY = "#f0efe9", "#faf9f6"
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'
W, H = 1120, 690
L, T = 300, 300
CW, CH = 62, 34
NM, NN = 9, 8          # manufacturers down, regulators across


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def short(n):
    for long, s in (("Central Drugs Standard Control Organization", "CDSCO"),
                    ("European Medicines Agency", "EMA"),
                    ("Ministry of Food and Drug Safety", "MFDS"),
                    ("Federal Agency for Medicines", "FAMHP"),
                    ("National Medical Products Administration", "NMPA"),
                    ("Pharmaceuticals and Medical Devices Agency", "PMDA"),
                    ("Therapeutic Goods Administration", "TGA"),
                    ("Agencia Nacional de Vigil", "ANVISA"),
                    ("National Agency of Drug and Food Control", "BPOM (Indonesia)"),
                    ("Agence nationale de s", "ANSM (France)"),
                    ("Bulgarian Drug Agency", "BDA (Bulgaria)"),
                    ("Bharat Biotech International", "Bharat Biotech"),
                    ("BB- NCIPD EAD", "BB-NCIPD (Bulgaria)"),
                    ("PT Bio Farma", "Bio Farma (Indonesia)"),
                    ("Serum Institute of India", "Serum Institute of India"),
                    ("GlaxoSmithKline Biologicals", "GlaxoSmithKline"),
                    ("Merck Sharp", "Merck Sharp & Dohme")):
        if n.startswith(long):
            return s
    return n[:26]


def ramp(frac):
    """Single hue, light to dark. Sequential = magnitude, never a rainbow."""
    a = (245, 247, 250)
    b = (16, 58, 105)
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * frac) for i in range(3))


def main() -> int:
    f = sorted(glob.glob(str(ROOT / "derived/observations/*.csv.gz")))[-1]
    prod = collections.defaultdict(dict)
    for r in csv.DictReader(gzip.open(f, "rt")):
        if r["metric"] in ("rows_on_page", "next_page_present"):
            continue
        prod[r["entity_id"]][r["metric"]] = r["value"]
    P = list(prod.values())
    cell = collections.Counter((p.get("manufacturer", "?"), p.get("responsible_nra", "?"))
                               for p in P)
    mtot = collections.Counter(p.get("manufacturer", "?") for p in P)
    ntot = collections.Counter(p.get("responsible_nra", "?") for p in P)
    mans = [m for m, _ in mtot.most_common(NM)]
    nras = [n for n, _ in ntot.most_common(NN)]
    peak = max(cell[(m, n)] for m in mans for n in nras)
    shown = sum(cell[(m, n)] for m in mans for n in nras)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family=\'{FONT}\'>',
         f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>']
    o.append(f'<text x="34" y="44" font-size="21" font-weight="600" fill="{INK}">'
             f'The regulator concentration and the maker concentration are the '
             f'same concentration</text>')
    o.append(f'<text x="34" y="70" font-size="13.5" fill="{INK2}">'
             f'Prequalified products by who makes them and who vouches for them. '
             f'Top {NM} manufacturers of 51, top {NN} regulators of 22 &#8212; '
             f'{shown} of {len(P)} products.</text>')
    o.append(f'<text x="34" y="89" font-size="13.5" fill="{INK2}">'
             f'<tspan font-weight="600" fill="{INK}">India&#8217;s CDSCO is '
             f'responsible for {ntot[nras[0]]} products, and {cell[(mans[0], nras[0])] + cell[(mans[1], nras[0])]} '
             f'of them come from two manufacturers.</tspan> One column carries '
             f'most of the list.</text>')
    o.append(f'<text x="34" y="108" font-size="13.5" fill="{INK2}">'
             f'So a regulator-level problem and a manufacturer-level problem '
             f'would land on the same cells, not on different ones.</text>')

    # column headers, angled so long names do not collide
    for j, n in enumerate(nras):
        x = L + j * CW + CW / 2
        o.append(f'<text x="{x:.0f}" y="{T - 14}" font-size="12" fill="{INK2}" '
                 f'text-anchor="start" transform="rotate(-38 {x:.0f} {T - 14})">'
                 f'{esc(short(n))}</text>')
        o.append(f'<text x="{x:.0f}" y="{T + NM * CH + 22}" font-size="11" '
                 f'fill="{MUTED}" text-anchor="middle">{ntot[n]}</text>')

    for i, m in enumerate(mans):
        y = T + i * CH
        o.append(f'<text x="{L - 14}" y="{y + CH / 2 + 4:.0f}" font-size="12.5" '
                 f'fill="{INK}" text-anchor="end">{esc(short(m))}</text>')
        o.append(f'<text x="{L + NN * CW + 16}" y="{y + CH / 2 + 4:.0f}" '
                 f'font-size="11.5" font-weight="600" fill="{MUTED}">{mtot[m]}</text>')
        for j, n in enumerate(nras):
            v = cell[(m, n)]
            x = L + j * CW
            fill = ramp(v / peak) if v else EMPTY
            o.append(f'<rect x="{x}" y="{y}" width="{CW - 2}" height="{CH - 2}" '
                     f'fill="{fill}" stroke="{GRID}" stroke-width="1"/>')
            if v:
                ink = "#ffffff" if v / peak > 0.45 else INK
                o.append(f'<text x="{x + CW / 2 - 1:.0f}" y="{y + CH / 2 + 4:.0f}" '
                         f'font-size="12.5" font-weight="600" fill="{ink}" '
                         f'text-anchor="middle">{v}</text>')

    o.append(f'<text x="{L + NN * CW + 16}" y="{T - 14}" font-size="11.5" '
             f'fill="{MUTED}">total</text>')
    o.append(f'<text x="{L - 14}" y="{T + NM * CH + 22}" font-size="11.5" '
             f'fill="{MUTED}" text-anchor="end">total</text>')
    o.append(f'<text x="34" y="{H - 40}" font-size="12" fill="{MUTED}">'
             f'Darker is more products. Empty cells are genuinely empty &#8212; '
             f'that manufacturer has nothing prequalified through that regulator.'
             f'</text>')
    o.append(f'<text x="34" y="{H - 23}" font-size="12" fill="{MUTED}">'
             f'One capture. Row and column totals are over all 285 products, not '
             f'only the cells shown.</text>')
    o.append("</svg>")
    OUT.write_text("\n".join(o))
    print(f"wrote {OUT}  ({shown}/{len(P)} products in {NM}x{NN})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
