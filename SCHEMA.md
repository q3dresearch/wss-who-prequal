# Data shape — `who.pq.vaccines`

*Generated 2026-09-15T12:02:15Z by `examples/write_schema.py` from the derived rows. Do not hand-edit — regenerate after any derive.*

**You should not need to download anything to read this.**

- **2,291 observations** across 1 partition(s), in **2 series**
  - `who.pq.vaccines` — 2,279 rows, **285 entities** (`commercial_name`, `doses`, `listed`, `manufacturer`, `prequalification_date`, `presentation`, `responsible_nra`, `vaccine_type`)
  - `who.pq.vaccines.pages` — 12 rows, **6 entities** (`next_page_present`, `rows_on_page`)
- Raw: 6 file(s), 161,226 bytes on disk, `text/html`, 1 capture date(s)
- Cadence `monthly` · 6 endpoint(s) · storage `git` · personal data `none`
- Licence: CC BY-NC-SA 3.0 IGO — https://www.who.int/about/policies/publishing/copyright

## Columns

```
series_id, entity_id, observed_at, captured_at, metric, value, unit, source_id, raw_ref, parser_version
```

`entity_id` looks like: **who.pq.vaccines** `abrysvo`, `abrysvo-0`, `adacel`; **who.pq.vaccines.pages** `page-0`, `page-1`, `page-2`

## Metrics

| metric | rows | entities | type | unit | distinct | range / samples |
| --- | ---: | ---: | --- | --- | ---: | --- |
| `commercial_name` | 285 | 285 | text | text | 173 | `Abrysvo`, `Adacel`, `Adsorbed DT Vaccine` |
| `doses` | 284 | 284 | int | text | 9 | `1` … `50` |
| `listed` | 285 | 285 | bool | presence | 1 | `1` |
| `manufacturer` | 285 | 285 | text | text | 51 | `AJ Vaccines A/S`, `Abbott Biologicals BV`, `AstraZeneca Pharmaceuticals ` |
| `next_page_present` | 6 | 6 | bool | bool | 2 | `0`, `1` |
| `prequalification_date` | 285 | 285 | date | date | 180 | `1987-01-01` … `2026-08-24` |
| `presentation` | 285 | 285 | text | text | 11 | `Ampoule`, `Ampoule or Vial`, `Applicator` |
| `responsible_nra` | 285 | 285 | text | text | 22 | `Agence nationale de sécurité`, `Agencia Nacional da Vigilanc`, `Bulgarian Drug Agency` |
| `rows_on_page` | 6 | 6 | int | count | 2 | `35` … `50` |
| `vaccine_type` | 285 | 285 | text | text | 56 | `BCG`, `Covid-19`, `Dengue Tetravalent (live, at` |

## Partitions

- `derived/observations/2026-09.csv.gz`
