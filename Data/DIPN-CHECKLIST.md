# DIPN / SOIPN / EDOIPN archive — status

**Complete.** All 73 currently-in-force documents listed on the IRD DIPN index
(https://www.ird.gov.hk/eng/ppr/dip.htm) — 64 DIPN (1–63 plus 13A), 8 SOIPN,
1 EDOIPN — have been downloaded and saved under `Data/DIPN/` (and 3 IRD
Administration ones under `Data/IRD-Administration/`). See the **DIPN Index**
page (`pages/dipn-index.html`) in the study hub for the searchable catalogue
with summaries and worked-example flags — that page is the live source of
truth, not this file.

## Folder map

| Folder | Contents |
|---|---|
| `DIPN/Profits-Tax/` | 22 documents — the 20 core ones behind the Profits Tax page, plus DIPN 22 (royalties/IP) and DIPN 55 (R&D deduction), reference-only for now |
| `DIPN/Property-Tax/` | DIPN 14 (DIPN 4 lives in Profits-Tax, shared/cross-referenced) |
| `DIPN/Salaries-Tax/` | 14 documents behind the Salaries Tax page |
| `DIPN/Stamp-Duty/` | SOIPN 1–8, all behind the Stamp Duty page |
| `DIPN/Depreciation-Allowances/` | DIPN 2, 5, 7, 49 — all behind the Depreciation & Allowances page |
| `DIPN/Cross-Border-Transfer-Pricing/` | 13 documents (DTAs, transfer pricing, offshore funds, EOI, APA, PE attribution) — reference-only, no dedicated page yet |
| `DIPN/Special-Regimes/` | 7 documents (shipping, aircraft/ship leasing, corporate treasury, regulatory capital, alternative bonds, amalgamation) — reference-only |
| `DIPN/Other/` | EDOIPN 1 (Estate Duty — abolished 2006, kept for historical reference) |
| `IRD-Administration/` (top-level, not under `DIPN/`) | DIPN 6, 11, 31 (objections/appeals, field audit, advance rulings) |

## Refreshing this archive later

Re-run the same download pass (ask Claude, or repeat manually) if IRD issues a
new or revised DIPN — the IRD index page is the authority on what's current.
After adding/replacing any file, run `scripts\Refresh-Data-Manifest.bat` so
the freshness banners on the core topic pages pick up the change.

## Scope note

Per the agreed build scope, only the five core taxes (Profits, Property,
Salaries, Stamp Duty, Depreciation & Allowances) have full dedicated study
pages with tables, illustrations, and computation templates. The 26
reference-only documents above (transfer pricing, aircraft/ship leasing,
corporate treasury, offshore funds, cross-border DTAs, field audit, advance
rulings, estate duty) are downloaded and briefly summarized in the DIPN
Index, but do not yet have that same depth of treatment. Ask Claude to build
a dedicated page for any of these if your team needs deeper coverage.
