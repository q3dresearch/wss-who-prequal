#!/usr/bin/env python3
"""Which vaccine types have no fallback AND have not been refreshed in years.

    python examples/exposure_staleness.py

Writes examples/charts/exposure-and-staleness.svg.

WHY NOT THE CHART THIS REPLACES. The first version crossed manufacturers-per-
type against products-per-type. Both axes were small discrete integers, so dots
collided and had to be jittered apart -- and jitter is the tell that a form is
wrong rather than a fix for it. Worse, the two axes were near-redundant: extra
products from the same maker are one supply chain, which is the chart's own
argument. A sparse 11x18 heatmap was the obvious replacement and is 14% filled,
which is no better.

The second axis had to be something the first does not already imply, and AGE is
it: how long since anything in that vaccine type was newly prequalified. It is
continuous, so the form works, and it is not redundant -- a type can be
single-source and fresh, or well-supplied and stale.

READ WITH correlated-exposure.svg, which shows that the exposed types are not
independent of each other.
"""
from __future__ import annotations

import collections
import csv
import datetime as dt
import glob
import gzip
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples/charts/exposure-and-staleness.svg"

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8880"
GRID, BAND = "#f0efe9", "#faf3e8"
WORRY, OK = "#d17b00", "#1b4f8a"
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'
W, H = 1100, 660
L, R, T, B = 96, 316, 176, 96
STALE = 10.0            # years; stated on the chart, not hidden in a bin edge


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def clip(s, n=36):
    s = s.replace("∆", "d")
    if len(s) <= n:
        return s
    cut = s[:n]
    return (cut[:cut.rfind(" ")] if " " in cut[18:] else cut).rstrip(" ,(") + "…"


def main() -> int:
    f = sorted(glob.glob(str(ROOT / "derived/observations/*.csv.gz")))[-1]
    prod = collections.defaultdict(dict)
    for r in csv.DictReader(gzip.open(f, "rt")):
        if r["metric"] in ("rows_on_page", "next_page_present"):
            continue
        prod[r["entity_id"]][r["metric"]] = r["value"]
    mfr, dates = collections.defaultdict(set), collections.defaultdict(list)
    for p in prod.values():
        t = p.get("vaccine_type") or "(unstated)"
        mfr[t].add(p.get("manufacturer") or "?")
        if p.get("prequalification_date"):
            dates[t].append(p["prequalification_date"])
    today = dt.date.today()
    rows = []
    for t in mfr:
        if not dates[t]:
            continue
        age = (today - dt.date.fromisoformat(max(dates[t]))).days / 365.25
        rows.append((t, age, len(mfr[t]), sorted(mfr[t])[0]))
    worry = sorted([r for r in rows if r[2] == 1 and r[1] >= STALE],
                   key=lambda r: -r[1])
    sole = [r[1] for r in rows if r[2] == 1]
    multi = [r[1] for r in rows if r[2] > 1]

    xmax = max(r[1] for r in rows) * 1.06
    ymax = max(r[2] for r in rows)

    def px(v):
        return L + v / xmax * (W - L - R)

    def py(v):
        return T + (H - T - B) - (v - 1) / max(ymax - 1, 1) * (H - T - B)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family=\'{FONT}\'>',
         f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>']
    o.append(f'<text x="34" y="44" font-size="21" font-weight="600" fill="{INK}">'
             f'{len(worry)} vaccine types have one supplier and nothing new '
             f'prequalified in a decade</text>')
    o.append(f'<text x="34" y="70" font-size="13.5" fill="{INK2}">'
             f'Each dot is one of the {len(rows)} vaccine types WHO prequalifies. '
             f'Across: years since anything in that type was newly prequalified. '
             f'Up: how many</text>')
    o.append(f'<text x="34" y="89" font-size="13.5" fill="{INK2}">'
             f'distinct manufacturers hold prequalification for it.</text>')
    o.append(f'<text x="34" y="112" font-size="13.5" fill="{INK2}">'
             f'<tspan font-weight="600" fill="{INK}">The shaded corner is the '
             f'worry list: no alternative supplier, and no refresh in '
             f'{STALE:.0f}+ years.</tspan> Sole-source types are older as a '
             f'group &#8212; median '
             f'{statistics.median(sole):.1f}y against {statistics.median(multi):.1f}y.</text>')
    o.append(f'<text x="34" y="133" font-size="12.5" fill="{MUTED}">'
             f'One capture, no archive needed. What the archive adds is the date '
             f'a dot leaves the chart entirely &#8212; WHO records no withdrawals.'
             f'</text>')

    o.append(f'<rect x="{px(STALE):.0f}" y="{py(1) - 15:.0f}" '
             f'width="{W - R - px(STALE):.0f}" height="30" fill="{BAND}"/>')
    for gx in range(0, int(xmax) + 1, 5):
        o.append(f'<line x1="{px(gx):.1f}" y1="{T - 8}" x2="{px(gx):.1f}" '
                 f'y2="{H - B}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{px(gx):.1f}" y="{H - B + 22}" font-size="12" '
                 f'fill="{MUTED}" text-anchor="middle">{gx}y</text>')
    for gy in range(1, ymax + 1, 2):
        o.append(f'<line x1="{L}" y1="{py(gy):.1f}" x2="{W - R}" y2="{py(gy):.1f}" '
                 f'stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{L - 12}" y="{py(gy) + 4:.1f}" font-size="12" '
                 f'fill="{MUTED}" text-anchor="end">{gy}</text>')
    o.append(f'<line x1="{px(STALE):.1f}" y1="{T - 8}" x2="{px(STALE):.1f}" '
             f'y2="{H - B}" stroke="{WORRY}" stroke-width="1.5" '
             f'stroke-dasharray="5 4"/>')
    o.append(f'<text x="{px(STALE) + 8:.0f}" y="{T + 4}" font-size="11.5" '
             f'fill="{WORRY}">{STALE:.0f} years</text>')

    seen = collections.Counter()
    for t, age, n, m in rows:
        k = (round(age, 1), n)
        dy = seen[k] * 7
        seen[k] += 1
        c = WORRY if (n == 1 and age >= STALE) else (OK if n > 1 else "#e8a951")
        o.append(f'<circle cx="{px(age):.1f}" cy="{py(n) - dy:.1f}" r="6" '
                 f'fill="{c}" fill-opacity="0.72" stroke="{SURFACE}" '
                 f'stroke-width="1.2"/>')

    y = T + 6
    o.append(f'<text x="{W - R + 24}" y="{y}" font-size="13" font-weight="600" '
             f'fill="{INK}">The worry list</text>')
    o.append(f'<text x="{W - R + 24}" y="{y + 17}" font-size="11.5" fill="{MUTED}">'
             f'one supplier, {STALE:.0f}+ years since a refresh</text>')
    for t, age, n, m in worry:
        y += 38
        o.append(f'<circle cx="{W - R + 30}" cy="{y - 4}" r="4.5" fill="{WORRY}"/>')
        o.append(f'<text x="{W - R + 42}" y="{y - 7}" font-size="11.5" fill="{INK2}">'
                 f'{esc(clip(t))}</text>')
        o.append(f'<text x="{W - R + 42}" y="{y + 7}" font-size="10.5" fill="{MUTED}">'
                 f'{age:.0f}y &#183; {esc(clip(m, 30))}</text>')

    o.append(f'<text x="{(L + W - R) / 2:.0f}" y="{H - B + 52}" font-size="13" '
             f'fill="{INK2}" text-anchor="middle">years since anything in this '
             f'vaccine type was newly prequalified</text>')
    o.append(f'<text x="26" y="{(T + H - B) / 2:.0f}" font-size="13" fill="{INK2}" '
             f'text-anchor="middle" transform="rotate(-90 26 {(T + H - B) / 2:.0f})">'
             f'distinct manufacturers</text>')
    o.append(f'<text x="34" y="{H - 26}" font-size="12" fill="{MUTED}">'
             f'Orange: single supplier. Dark orange: single supplier and stale. '
             f'Blue: two or more. Small vertical offsets separate overlapping '
             f'types.</text>')
    o.append("</svg>")
    OUT.write_text("\n".join(o))
    print(f"wrote {OUT}  ({len(rows)} types, {len(worry)} on the worry list)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
