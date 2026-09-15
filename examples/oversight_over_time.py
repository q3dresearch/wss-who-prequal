#!/usr/bin/env python3
"""When each regulator was doing the vouching, and whose share is growing.

    python examples/oversight_over_time.py

Writes examples/charts/oversight-over-time.svg.

One dot per prequalified product: across is the year it was prequalified, down
is the regulator that signed it off. 285 marks, one per thing, no binning --
a three-era bar chart would have invited a curve out of three points, and the
drift is visible without one.

A DATA-QUALITY NOTE THE CHART SURFACED. There are 22 distinct NRA strings but
21 regulators: "CBER/FDA" and "US Food and Drug Administration- Office of
Vaccine Research and Review" are the same body, split across two spellings (and
WHO's own string is missing a space after the hyphen). Together they are 12
products, which would rank the US seventh rather than ninth and tenth. They are
deliberately NOT merged in the data -- the publisher's values are what was
captured -- but the chart says so, because a silent merge is a judgement the
next reader cannot see.

THE FINDING IS A TREND, which none of the other charts here carry. India's
CDSCO has not merely got the largest share, it has GROWN it: 41% of everything
prequalified before 2010, 45% in 2010-2017, 50% since 2018. Half of every
vaccine prequalified in the last eight years was vouched for by one national
regulator. The era figures are printed as a check on the eye, not as the
encoding.
"""
from __future__ import annotations

import collections
import csv
import glob
import gzip
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples/charts/oversight-over-time.svg"

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8880"
GRID, HL = "#f0efe9", "#fbf1e4"
LEAD, REST = "#d17b00", "#1b4f8a"
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'
W, H = 1100, 660
L, R, T, B = 268, 168, 192, 92
TOP = 10


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def short(n):
    for long, s in (("Central Drugs Standard Control Organization", "CDSCO (India)"),
                    ("European Medicines Agency", "EMA"),
                    ("Ministry of Food and Drug Safety", "MFDS (Korea)"),
                    ("Federal Agency for Medicines", "FAMHP (Belgium)"),
                    ("National Agency of Drug and Food Control", "BPOM (Indonesia)"),
                    ("National Medical Products Administration", "NMPA (China)"),
                    ("Pharmaceuticals and Medical Devices Agency", "PMDA (Japan)"),
                    ("Bulgarian Drug Agency", "BDA (Bulgaria)"),
                    ("Agence nationale de s", "ANSM (France)"),
                    ("Therapeutic Goods Administration", "TGA (Australia)"),
                    ("US Food and Drug Administration", "US FDA (2nd spelling)"),
                    ("CBER/FDA", "CBER/FDA (US)"),
                    ("Agencia Nacional de Vigil", "ANVISA (Brazil)")):
        if n.startswith(long):
            return s
    return n[:24]


def main() -> int:
    f = sorted(glob.glob(str(ROOT / "derived/observations/*.csv.gz")))[-1]
    prod = collections.defaultdict(dict)
    for r in csv.DictReader(gzip.open(f, "rt")):
        if r["series_id"] != "who.pq.vaccines":
            continue
        prod[r["entity_id"]][r["metric"]] = r["value"]
    P = [p for p in prod.values() if p.get("prequalification_date")]
    year = lambda p: int(p["prequalification_date"][:4])
    tot = collections.Counter(p.get("responsible_nra", "?") for p in P)
    order = [n for n, _ in tot.most_common(TOP)]
    other = [p for p in P if p.get("responsible_nra") not in order]
    lanes = order + [f"{len(tot) - TOP} others"]

    y0, y1 = min(year(p) for p in P), max(year(p) for p in P)
    lane = (H - T - B) / len(lanes)

    def px(v):
        return L + (v - y0) / (y1 - y0) * (W - L - R)

    def ly(i):
        return T + lane * (i + 0.5)

    era = [("before 2010", lambda y: y < 2010), ("2010–2017", lambda y: 2010 <= y < 2018),
           ("since 2018", lambda y: y >= 2018)]
    shares = []
    for lab, fn in era:
        sel = [p for p in P if fn(year(p))]
        shares.append((lab, len(sel),
                       sum(1 for p in sel if p.get("responsible_nra") == order[0]) / len(sel)))

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family=\'{FONT}\'>',
         f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>']
    o.append(f'<text x="34" y="44" font-size="21" font-weight="600" fill="{INK}">'
             f'One regulator now vouches for half of everything newly '
             f'prequalified</text>')
    o.append(f'<text x="34" y="70" font-size="13.5" fill="{INK2}">'
             f'Every prequalified vaccine as one dot: the year it was '
             f'prequalified, against the national authority that signed it off. '
             f'{len(P)} products, {len(tot)} authorities.</text>')
    o.append(f'<text x="34" y="89" font-size="13.5" fill="{INK2}">'
             f'<tspan font-weight="600" fill="{INK}">{short(order[0])} has not '
             f'just the largest share &#8212; a growing one: '
             + " then ".join(f"{s:.0%}" for _, _, s in shares) +
             f'.</tspan> ' + ", ".join(f"{lab} n={n}" for lab, n, _ in shares) + '.</text>')
    o.append(f'<text x="34" y="112" font-size="12.5" fill="{MUTED}">'
             f'No binning in the encoding &#8212; every dot is a real year. The '
             f'three era figures are a check on the eye, not the chart.</text>')
    o.append(f'<text x="34" y="131" font-size="12.5" fill="{MUTED}">'
             f'22 authority STRINGS, 21 bodies: &#8220;CBER/FDA&#8221; and '
             f'&#8220;US Food and Drug Administration- Office of Vaccine Research '
             f'and Review&#8221; are the same regulator. Left unmerged &#8212; '
             f'the publisher&#8217;s values are not rewritten here.</text>')

    o.append(f'<rect x="{L - 20}" y="{ly(0) - lane / 2:.0f}" '
             f'width="{W - L - R + 40}" height="{lane:.0f}" fill="{HL}"/>')
    for gx in range(((y0 + 4) // 5) * 5, y1 + 1, 5):
        o.append(f'<line x1="{px(gx):.1f}" y1="{T - 10}" x2="{px(gx):.1f}" '
                 f'y2="{H - B}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{px(gx):.1f}" y="{H - B + 22}" font-size="12" '
                 f'fill="{MUTED}" text-anchor="middle">{gx}</text>')

    seen = collections.Counter()
    for i, n in enumerate(lanes):
        sel = other if i == TOP else [p for p in P if p.get("responsible_nra") == n]
        c = LEAD if i == 0 else REST
        o.append(f'<text x="{L - 16}" y="{ly(i) + 5:.1f}" font-size="12.5" '
                 f'fill="{INK if i == 0 else INK2}" text-anchor="end" '
                 f'font-weight="{600 if i == 0 else 400}">{esc(short(n))}</text>')
        o.append(f'<text x="{W - R + 14}" y="{ly(i) + 5:.1f}" font-size="12" '
                 f'font-weight="600" fill="{MUTED}">{len(sel)}</text>')
        for p in sel:
            k = (i, year(p))
            j = seen[k]
            seen[k] += 1
            o.append(f'<circle cx="{px(year(p)):.1f}" '
                     f'cy="{ly(i) - (j % 4) * 5.5 + 8:.1f}" r="4.2" fill="{c}" '
                     f'fill-opacity="0.6" stroke="{SURFACE}" stroke-width="0.9"/>')

    o.append(f'<text x="{W - R + 14}" y="{T - 16}" font-size="11.5" '
             f'fill="{MUTED}">products</text>')
    o.append(f'<text x="{(L + W - R) / 2:.0f}" y="{H - B + 52}" font-size="13" '
             f'fill="{INK2}" text-anchor="middle">year of prequalification</text>')
    o.append(f'<text x="34" y="{H - 26}" font-size="12" fill="{MUTED}">'
             f'Small vertical offsets separate products prequalified in the same '
             f'year by the same authority. Read with oversight-matrix.svg, which '
             f'shows whose products those are.</text>')
    o.append("</svg>")
    OUT.write_text("\n".join(o))
    print(f"wrote {OUT}  ({len(P)} products, {len(tot)} authorities, "
          f"lead share {' -> '.join(f'{s:.0%}' for _, _, s in shares)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
