# Research questions

Written before the first capture was committed, which is the point of the file.

Statuses: `needs the archive` · `needs ~N months` · `answered` · `tested and failed` · `not observable`

| # | Question | Who acts on it | Needs | Status |
| --- | --- | --- | --- | --- |
| 1 | **Which vaccines have lost WHO prequalification, and on what date?** | A procurement officer at UNICEF Supply Division or Gavi establishing what was prequalified on a past date; an inquiry or dispute needing the same. Today neither can: the site shows only the present list. | one capture, then a second that differs | **needs the archive** |
| 2 | **Does the list ever shrink, and by how much at a time?** | The founding question. If it never shrinks, this repo is a mistake and should be retired. | ~12 months | **needs ~12 months** |
| 3 | **How long does a prequalification last before withdrawal?** | A national immunisation programme weighing supplier concentration risk — a product prequalified last year is a different bet from one prequalified in 2009. | ~3 years, and question 2 answered first | **needs ~36 months** |
| 4 | **When a product is withdrawn, does its manufacturer return with a replacement, and how fast?** | Gavi and procurement planners sizing how long a gap in supply of a vaccine type lasts. | ~3 years | **needs ~36 months** |
| 5 | **Do the sibling WHO prequalification lists behave the same way?** | Decides whether this is one list or a family worth capturing. The snake-antivenom list carries the identical sentence — *"WHO may suspend or remove an antivenom from the list"* — with no status column either. Medicines, IVDs, vector control products and immunization devices are unscreened. | screening only, no capture | **open, answerable now** |
| 6 | **Does anyone else already archive this list?** | If they do, this repo should be a citation rather than a capture. | a CDX query | **blocked** — web.archive.org was offline on 2026-09-15 |

## The bet this repo is making, stated plainly

**Question 2 is unmeasured, and it is the one that decides everything.** WHO's
own procedures say withdrawal is routine rather than exceptional, and the list
has no way to record one — but nobody has counted how often it actually
happens. If the answer turns out to be *once a decade*, monthly capture buys
almost nothing and this should be retired rather than defended.

The reason to capture now anyway is that it is the only irreversible step. A
missing parser can be fixed next year; a month in which nobody wrote down who
held prequalification cannot be. The cost of being wrong is ~2.2 MB a year.

## What would retire this repo

* **Question 6 comes back positive** — someone already holds a dated series of
  this list, in which case cite them.
* **Question 2 comes back near zero** after twelve months of captures.
* **WHO adds a status column, or publishes a withdrawn list.** The `listed`
  metric would then be reconstructable from the publisher and this becomes a
  larder. Check the seven column headers on every derive.
