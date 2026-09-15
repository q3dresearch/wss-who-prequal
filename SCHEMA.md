# Data shape

*Generated 2026-09-15T13:15:08Z by `wss schema` from the derived rows. Do not hand-edit — regenerate after any derive.*

**You should not need to download anything to read this.**

- **2,291 observations** across 1 partition(s), in **2 series**
  - `who.pq.vaccines` — 2,279 rows, **285 entities**
  - `who.pq.vaccines.pages` — 12 rows, **6 entities**
- Raw: 6 file(s), 161,226 bytes on disk, 1 capture date(s), 2026-09-15 → 2026-09-15

## Sources

| source | cadence | endpoints | storage | personal data | licence |
| --- | --- | ---: | --- | --- | --- |
| `who.pq.vaccines` | monthly | 6 | git | none | CC BY-NC-SA 3.0 IGO — https://www.who.int/about/policies/pub |

## Columns

```
series_id, entity_id, observed_at, captured_at, metric, value, unit, source_id, raw_ref, parser_version
```

`entity_id` looks like: **who.pq.vaccines** `abrysvo`, `abrysvo-0`, `adacel`; **who.pq.vaccines.pages** `page-0`, `page-1`, `page-2`

## Metrics

| metric | series | rows | entities | type | unit | distinct | range / samples |
| --- | --- | ---: | ---: | --- | --- | ---: | --- |
| `commercial_name` | who.pq.vaccines | 285 | 285 | text | text | 173 | `Abrysvo`, `Adacel`, `Adsorbed DT Vaccine` |
| `doses` | who.pq.vaccines | 284 | 284 | number | text | 9 | `1` … `50` |
| `listed` | who.pq.vaccines | 285 | 285 | bool | presence | 1 | `1` |
| `manufacturer` | who.pq.vaccines | 285 | 285 | text | text | 51 | `AJ Vaccines A/S`, `Abbott Biologicals BV`, `AstraZeneca Pharmaceutic` |
| `next_page_present` | who.pq.vaccines.pages | 6 | 6 | bool | bool | 2 | `0`, `1` |
| `prequalification_date` | who.pq.vaccines | 285 | 285 | date | date | 180 | `1987-01-01` … `2026-08-24` |
| `presentation` | who.pq.vaccines | 285 | 285 | text | text | 11 | `Ampoule`, `Ampoule or Vial`, `Applicator` |
| `responsible_nra` | who.pq.vaccines | 285 | 285 | text | text | 22 | `Agence nationale de sécu`, `Agencia Nacional da Vigi`, `Bulgarian Drug Agency` |
| `rows_on_page` | who.pq.vaccines.pages | 6 | 6 | number | count | 2 | `35` … `50` |
| `vaccine_type` | who.pq.vaccines | 285 | 285 | text | text | 56 | `BCG`, `Covid-19`, `Dengue Tetravalent (live` |

## Partitions

- `derived/observations/2026-09.csv.gz`
