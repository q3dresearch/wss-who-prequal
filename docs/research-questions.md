# What an archive of WHO prequalification is for

## The spine

WHO prequalification is a **procurement gate**. UNICEF Supply Division and Gavi
may only buy prequalified product, so presence on this list decides what reaches
most of the world's routine immunisation programmes.

The list publishes **seven columns and not one of them is a status**: Date of
Prequalification, Vaccine Type, Commercial Name, Presentation, No. of doses,
Manufacturer, Responsible NRA. The Drupal view behind it exposes thirteen
filters and every one is a product attribute. `delisted-vaccines`, `withdrawn`
and `vaccines-suspended` all 404. There is no dated file series, no CSV export
and no archive path.

**And WHO says plainly that it removes products.** The list page: *"WHO may
suspend or remove a vaccine from the list."* WHO's post-prequalification
procedures carry a section headed *"Withdrawal from the list of WHO-prequalified
vaccines"*, noting that in most cases status is withdrawn voluntarily by a
manufacturer when production is discontinued. Departure is **routine**, and it
is exactly what is never written down.

## What the capture contains

**285 products, 51 manufacturers, 22 national regulatory authorities, 56 vaccine
types**, across six pages of fifty.

| field | why it matters |
| --- | --- |
| product slug | publisher-minted id from `/prequal/vaccines/p/<slug>`. Distinguishes presentations (`bevacr-0` / `bevacr-1`). 285 rows, 285 distinct ids, zero collisions |
| `prequalification_date` | **the field that makes one capture useful** — see below. Spans 1987-01-01 to 2026-08-24 |
| `manufacturer` | 51 of them, and the concentration is the finding |
| `responsible_nra` | 22 regulators; **one signs off 130 of 285** |
| `vaccine_type` | 56 values, but the string mixes real distinctions with dose variants — see the caveat on the chart |
| `next_page_present` | the truncation alarm, not a fact about vaccines |

## Answerable today, from one capture

![single-supplier exposure](../examples/charts/single-supplier-exposure.svg)

![correlated exposure](../examples/charts/correlated-exposure.svg)

**These two are a chain and the caption says so on the chart itself.** The first
counts 17 exposed vaccine types; the second shows they rest on 9 manufacturers
and 3 regulators. Reading the first alone overstates how independent the
failure modes are — which is step 11 question 4 of the wss sequence, and the
reason the second chart exists.

| # | Question | Answer |
| --- | --- | --- |
| A1 | **How many vaccine types rest on a single manufacturer?** | **17 of 56 (30%)** at WHO's own granularity; **15 of 52 (29%)** with dose and age variants merged. The proportion does not depend on the choice. Includes Ebola Zaire, both HPV valencies, and Pandemic Influenza H5N1 |
| A2 | **How concentrated is manufacture?** | Serum Institute of India holds **72 of 285 (25%)**; the top five manufacturers hold **56%**. Among the 17 exposed types it is starker: Serum Institute is sole maker for **6**, Merck for **3** |
| A3 | **How concentrated is oversight?** | India's CDSCO is the responsible NRA for **130 of 285 (46%)**; the top five NRAs cover **75%**. Among the 17 exposed types, **EMA and CDSCO cover 16**. A regulator-level problem is not a product-level problem |
| A4 | **How old is the list?** | Median prequalification age **12.0 years**; oldest 1987, newest last month |

**These need no archive.** They are why the repo is worth running, not what it
produces. What the archive adds is the date a dot moves left.

## Needs the archive

| # | Question | Who acts | Status |
| --- | --- | --- | --- |
| W1 | **Which vaccines have lost prequalification, and when?** | A procurement officer establishing what was prequalified on a past date; an inquiry or dispute needing the same. Neither can today | **needs the archive** — one departure answers it |
| W2 | **Does the list shrink at all, and how often?** | The founding question. If it never shrinks this repo is a mistake | **needs ~12 months** |
| W3 | **When a single-manufacturer type loses its maker, how long until anything replaces it?** | Gavi and national programmes sizing a supply gap | **needs ~36 months** |
| W4 | **Does WHO's own removal language ever correspond to an observable event?** | Tests whether the procedures page describes something that happens | **needs ~12 months** |
| W5 | **Do the sibling PQ lists behave the same way?** | The antivenom list carries the identical *"WHO may suspend or remove"* sentence with no status column. Medicines, IVDs, vector control and immunization devices are unscreened | **open, answerable now without capture** |
| W6 | **Does anyone else already archive this list?** | If so, cite them and retire this | **blocked** — web.archive.org was offline 2026-09-15 |


## The four categories asked on 2026-09-15, screened

| category | status | what was found |
| --- | --- | --- |
| **Failed vaccines** | **not observable — terminal** | WHO publishes *only* positive lists. `vaccines-not-recommended` 404s; the Prequalified Vaccine Annual Report is a document landing page with no table; the COVID EUL page is another positive list (`Vaccine \| WHO EUL Holder \| NRA of record`); and the antivenom *List of Product Assessment Outcomes* is positive-only too. There is no rejected-application record anywhere in WHO PQ. **Recorded so the question is not re-asked** |
| **Lead time to users** | **blocked** | One end is in hand — the prequalification date. The other end is first procurement, which means UNICEF Supply Division, and `unicef.org/supply/documents/vaccine-price-data` returns **403** to a declared bot. Blocked on access, not on existence |
| **Distribution and recall window** | **larder, and a different event than it sounds** | WHO Medical Product Alerts run **2013–2026, all retained on one page** — so cite, never capture. 15 of 90 alerts name a vaccine. **But every one is a FALSIFIED (counterfeit) alert, not a recall of legitimate product.** It answers *was this vaccine counterfeited*, not *was it withdrawn* |
| **Variants and formulations** | **answered, from one capture** | See A5–A6 below |

### The join, measured rather than assumed

A naive token match between alert titles and the 171 commercial names gave 6 of
12 "matches" and **half were false**: *Falsified Fluzone Quadrivalent* matched
`afluria® quadrivalent` on the word "Quadrivalent", and *Falsified oral cholera
vaccine* matched `oral poliomyelitis vaccines` on "oral". Checked directly
instead: **Fluzone and Comirnaty are in the prequalified list; COVISHIELD is
not.** So the join exists and is thin — a handful of products over a decade.

## Answerable today — formulations

| # | Question | Answer |
| --- | --- | --- |
| A5 | **Do manufacturers extend a product line within a vaccine type?** | 155 manufacturer×type families; **82 hold more than one product**. But **43 of those 82 were prequalified entirely on one day** — that is one filing with several presentations, not a sequence. Only 39 show real spacing |
| A6 | **How long to add a variant, when it is a sequence?** | **Median 2.94 years** between consecutive prequalifications in the same manufacturer×type family (p10 0.38y, p90 9.93y, max 13.6y, n=47 intervals) |
| A8 | **Is the oversight concentration stable or growing?** | **Growing.** CDSCO signed 41% of pre-2010 prequalifications, 45% in 2010–2017, **50% since 2018** (n=91, 88, 106). See `oversight-over-time.svg` |
| A9 | **Which vaccine types force a multi-dose vial?** | **9 of 56 have no presentation under ten doses** — all five oral polio variants, BCG, both Meningococcal A conjugates. 120 of 285 products are 10-dose or larger. An opened multi-dose vial must be used within hours; these are the vaccines given in low-turnout outreach. See `vial-sizes.svg` |
| A10 | **Is the NRA vocabulary clean?** | **No — 22 strings, 21 bodies.** `CBER/FDA` (7) and `US Food and Drug Administration- Office of Vaccine Research and Review` (5) are the same regulator; WHO's own string is also missing a space after the hyphen. Together 12 products, which would rank the US 7th rather than 9th and 10th. **Left unmerged in the data** — a silent merge is a judgement the next reader cannot see |
| A7 | **Is formulation observable at all?** | Yes, and the vocabulary is small: Vial 220, Vial+Ampoule 18, two-vial set 16, Ampoule 14, then Plastic Tube 6, Sprayer 2, Applicator, Uniject, Buffer Sachet. Doses cluster at 1 (109), 10 (79), 20 (37), 5 (33) — multi-dose vials dominate |

**The trap, for the fifth time.** Every one of those pages returns a `withdraw`
hit that is the EU cookie banner's *"Withdraw consent"*. It has now produced a
false positive on the vaccines list, the antivenom list, the news page, the
PQVAR page and the COVID EUL page. **Grep the table, never the page.**

## The precision ceiling, computed before any chart implies otherwise

**The cohort is 285 products, and that is the ceiling on everything below.**

A single proportion to ±10 points needs ~81 outcomes; to ±5 points, ~323.
Comparing two groups needs ~163 per arm. The outcome here is a **departure**,
and its rate is exactly what W2 has not yet measured. So:

| if departures run at… | outcomes/year | ±10pp base rate (81) | two-group comparison (326) |
| --- | --- | --- | --- |
| 10%/yr | ~28 | ~3 years | ~12 years |
| 5%/yr | ~14 | ~6 years | ~23 years |
| 2%/yr | ~6 | ~14 years | never, in practice |

**So W3 and W4 are multi-year questions and any chart that ranks manufacturers
by departure risk is overselling this data.** Extra captures buy resolution in
TIME, not sample size — 285 products yield 285 products' worth of outcomes
however often you look.

**What IS reachable:** W1 needs exactly one departure, and W2 needs a handful.
Those are the questions this archive answers, and they are evidentiary rather
than statistical — *which product, on which date* is a lookup, and a lookup
with n=1 is still the only record that exists.

## Who this is for, and what changes

| who | questions | the decision it changes |
| --- | --- | --- |
| **A UNICEF or Gavi procurement officer** | W1, A1 | which vaccine types have no fallback if one maker exits — and, later, proof of what was prequalified on a past date, which no source provides today |
| **A national immunisation programme** | A1, A2, W3 | whether to hold deeper stock of a single-supplier vaccine type |
| **An inquiry, tribunal or auditor** | W1 | establishing the prequalification status of a product at a past date. The site shows only the present |
| **A vaccine-security or supply-chain researcher** | A1–A4, W2 | concentration is measurable today; whether it is worsening needs the series |
| **WHO itself** | W2, W4 | whether its own withdrawal procedure produces an observable, countable event |

**Who this is NOT for.** Anyone wanting today's prequalified list. That is WHO's
own page, authoritative and free and more current than this. This archive
answers the opposite question — **what used to be on it.**

## What would make this worth stopping

1. **W6 comes back positive.** Someone already holds a dated series of this
   list; cite them and retire this.
2. **W2 comes back near zero** after twelve months. If the list does not shrink,
   the premise is wrong and saying so is worth more than defending it.
3. **WHO adds a status column, or publishes a withdrawn list.** Then `listed`
   is reconstructable from the publisher and this becomes a larder. **Check the
   seven column headers on every derive** — that is the retirement trigger and
   it is cheap to watch.
4. **The slug stops being stable.** If products change slug on rename, a
   departure cannot be told from a rename and the founding question is
   unanswerable at this identity.
