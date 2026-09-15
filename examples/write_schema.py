#!/usr/bin/env python3
"""Describe the shape of this archive without anyone having to download it.

    python examples/write_schema.py

Writes schema/<source_id>.json and SCHEMA.md.

WHY THIS EXISTS. `manifest/` records TRANSPORT -- status, bytes, sha256, etag.
It says nothing about what is inside. Today the only way to learn that this
archive has a `listed` metric keyed on a product slug, or that
`prequalification_date` runs from 1987, is to clone the repo, find the right
partition, gunzip it and read it. That is a large ask for someone deciding
whether the data is worth downloading at all, and it is the single thing most
likely to stop them.

So the shape is written down at derive time, from the derived rows themselves --
never hand-maintained, because a hand-maintained schema drifts from the data
silently and then lies.

Portable across the fleet: it reads derived/observations/*.csv.gz, manifest/
and registry/, and assumes nothing source-specific.
"""
from __future__ import annotations

import collections
import csv
import glob
import gzip
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = 3
DATEISH = re.compile(r"^\d{4}-\d{2}-\d{2}")


def kind(values):
    """int | date | bool | text — inferred, and stated as inferred."""
    v = [x for x in values if x != ""]
    if not v:
        return "empty"
    if all(x in ("0", "1") for x in v):
        return "bool"
    if all(x.lstrip("-").isdigit() for x in v):
        return "int"
    if all(DATEISH.match(x) for x in v):
        return "date"
    return "text"


def main() -> int:
    parts = sorted(glob.glob(str(ROOT / "derived/observations/*.csv.gz")))
    if not parts:
        print("no derived partitions -- run `wss derive` first")
        return 1
    rows = []
    for p in parts:
        rows.extend(csv.DictReader(gzip.open(p, "rt")))

    by = collections.defaultdict(list)
    for r in rows:
        by[r["metric"]].append(r)

    metrics = {}
    for m, rs in sorted(by.items()):
        vals = [r["value"] for r in rs]
        distinct = sorted(set(vals))
        k = kind(vals)
        entry = {
            "rows": len(rs),
            "unit": rs[0]["unit"],
            "type": k,
            "distinct_values": len(distinct),
            "entities": len({r["entity_id"] for r in rs}),
            "null_or_empty": sum(1 for v in vals if v == ""),
        }
        if k in ("int", "date"):
            entry["min"], entry["max"] = distinct[0], distinct[-1]
        entry["samples"] = distinct[:SAMPLES] if len(distinct) > SAMPLES else distinct
        metrics[m] = entry

    # PER SERIES, not globally. A source can carry more than one grain -- this
    # one has 285 products and 6 fetch-shape rows -- and a single entity count
    # over both reads as 291 products, which is how the split got noticed.
    series = {}
    for sid in sorted({r["series_id"] for r in rows}):
        rs = [r for r in rows if r["series_id"] == sid]
        e = sorted({r["entity_id"] for r in rs})
        series[sid] = {"rows": len(rs), "entities": len(e),
                       "entity_id_samples": e[:SAMPLES],
                       "metrics": sorted({r["metric"] for r in rs})}
    ents = sorted({r["entity_id"] for r in rows})
    raws = [p for p in glob.glob(str(ROOT / "raw/**/*"), recursive=True)
            if os.path.isfile(p) and not p.endswith(".gitkeep")]
    man = []
    for p in sorted(glob.glob(str(ROOT / "manifest/**/*.csv"), recursive=True)):
        man.extend(csv.DictReader(open(p)))

    reg = {}
    for p in sorted(glob.glob(str(ROOT / "registry/*.yml"))):
        t = Path(p).read_text()
        for key in ("source_id", "schema_id", "cadence", "licence", "personal_data",
                    "storage", "publisher"):
            mm = re.search(rf"^{key}:\s*(.+)$", t, re.M)
            if mm:
                reg[key] = mm.group(1).strip().strip('"')
        reg["endpoints"] = len(re.findall(r"^\s+- url:", t, re.M))

    doc = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_from": [Path(p).name for p in parts],
        "note": ("Inferred from the derived rows, not hand-written. Regenerate "
                 "with examples/write_schema.py after any derive."),
        "source": reg,
        "observations": {
            "rows": len(rows),
            "columns": list(rows[0].keys()),
            "partitions": [Path(p).name for p in parts],
            "entities_all_series": len(ents),
            "series": series,
            "parser_versions": sorted({r["parser_version"] for r in rows}),
        },
        "metrics": metrics,
        "raw": {
            "files": len(raws),
            "bytes_on_disk": sum(os.path.getsize(p) for p in raws),
            "content_type": (man[0]["content_type"] if man else None),
            "captures": len({r["fetched_at"][:10] for r in man}) if man else 0,
            "first_capture": min((r["fetched_at"] for r in man), default=None),
            "last_capture": max((r["fetched_at"] for r in man), default=None),
        },
    }
    out = ROOT / "schema" / f"{reg.get('source_id', 'source')}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    # Human-readable twin, so the answer is one click rather than one parse.
    L = [f"# Data shape — `{reg.get('source_id')}`", "",
         f"*Generated {doc['generated_at']} by `examples/write_schema.py` from "
         f"the derived rows. Do not hand-edit — regenerate after any derive.*", "",
         "**You should not need to download anything to read this.**", "",
         f"- **{doc['observations']['rows']:,} observations** across "
         f"{len(parts)} partition(s), in **{len(series)} series**",]
    for sid, sv in series.items():
        L.append(f"  - `{sid}` — {sv['rows']:,} rows, **{sv['entities']} entities** "
                 f"({', '.join('`' + m + '`' for m in sv['metrics'])})")
    L += [
         f"- Raw: {doc['raw']['files']} file(s), "
         f"{doc['raw']['bytes_on_disk']:,} bytes on disk, `{doc['raw']['content_type']}`, "
         f"{doc['raw']['captures']} capture date(s)",
         f"- Cadence `{reg.get('cadence')}` · {reg.get('endpoints')} endpoint(s) · "
         f"storage `{reg.get('storage')}` · personal data `{reg.get('personal_data')}`",
         f"- Licence: {reg.get('licence')}", "",
         "## Columns", "",
         "```", ", ".join(doc["observations"]["columns"]), "```", "",
         "`entity_id` looks like: " +
         "; ".join(f"**{sid}** " + ", ".join(f"`{e}`" for e in sv["entity_id_samples"])
                   for sid, sv in series.items()), "",
         "## Metrics", "",
         "| metric | rows | entities | type | unit | distinct | range / samples |",
         "| --- | ---: | ---: | --- | --- | ---: | --- |"]
    for m, e in metrics.items():
        rng = (f"`{e['min']}` … `{e['max']}`" if "min" in e
               else ", ".join(f"`{s[:28]}`" for s in e["samples"]))
        L.append(f"| `{m}` | {e['rows']:,} | {e['entities']} | {e['type']} | "
                 f"{e['unit']} | {e['distinct_values']} | {rng} |")
    L += ["", "## Partitions", "",
          "\n".join(f"- `derived/observations/{p}`"
                    for p in doc["observations"]["partitions"])]
    (ROOT / "SCHEMA.md").write_text("\n".join(L) + "\n")
    print(f"wrote {out.relative_to(ROOT)} and SCHEMA.md "
          f"({len(metrics)} metrics, {len(series)} series, "
          f"{doc['observations']['entities_all_series']} entities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
