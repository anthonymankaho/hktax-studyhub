# HK Tax Study Hub

Internal, team-only reference and study tool for Hong Kong tax — **not for
external distribution or publication**. Static HTML, no server or build step:
double-click `index.html` to open it in a browser.

## What this is for

1. **Tax computation / transaction analysis** — for financial-statement tax
   computations of Hong Kong incorporated companies, confirming under which
   IRO/SDO section a transaction is Taxable / Non-taxable / Deductible /
   Non-deductible. Use the **Transaction Checker** for this.
2. **Study material** — rules, tables, and worked illustrations per tax
   topic, drawn from IRD's own guidance (DIPNs/SOIPNs) and a professional
   taxation textbook (Module 9: Principles of Taxation, 4th ed.), with every
   figure cross-checked against current law.

## Start here

Open `index.html`. From the hub you can reach:

| Page | Purpose |
|---|---|
| **Transaction Checker** | Search any transaction by keyword → Taxable/Non-taxable/Deductible/Non-deductible/Dutiable, with the exact section and a link to the full explanation. |
| **DIPN Index** | Searchable catalogue of all 73 currently-in-force DIPN/SOIPN/EDOIPN documents, with topic, summary, and whether it backs a full study page or is reference-only. |
| **Profits Tax / Property Tax / Salaries Tax / Stamp Duty / Depreciation & Allowances** | The five core topic pages — charging basis, rates, taxable/deductible tables, computation templates, all tied to exact IRO (Cap. 112) / Stamp Duty Ordinance (Cap. 117) sections. |
| **[Topic] — Worked Illustrations** | Companion page per topic (linked from each topic page's Illustrations section) with every worked example — DIPN-sourced and textbook-sourced — in one place. |
| **Profits Tax Return Guide** / **Box Finder** | Box-by-box walkthrough of the actual BIR51/52/54 return forms (linked from the Profits Tax page) — bridges "what the law says" to "what you type into the form," plus a keyword search over every box. |
| **IRD Administration** | Returns, assessment, objections/appeals, provisional tax, penalties — the process layer common to all taxes. |

## How it stays current

This is a **manual-refresh** tool by design — it does not, and cannot, live-fetch
ird.gov.hk from inside a browser-opened HTML file. The loop is:

1. **Download** an updated CAP112 / CAP117 / DIPN / SOIPN PDF and drop it into
   the matching `Data/` subfolder (see `Data/README.md` for the folder map).
2. **Run** `scripts\Refresh-Data-Manifest.bat` (double-click it) — it rescans
   `Data/` and rebuilds the file-date manifest the pages check against.
3. **Reload** the page. If a source file is now newer than that page's
   "last reviewed" date, the freshness banner at the top turns amber/red,
   telling you which page needs a re-check.
4. **Ask Claude** (in a Claude Code session) to re-read the updated source and
   refresh that page's content — step 2 only detects *that* something
   changed, not *what* changed.

`elegislation.gov.hk` (for CAP112/CAP117) gates automated downloads behind a
JS/cookie check — a normal browser download works fine, but re-fetching it
programmatically does not, so step 1 for legislation is a manual download.

## Data sources already in `Data/`

- **`CAP112/`** — Inland Revenue Ordinance, consolidated, current to 6.6.2025 per page-level stamps in the text. Covers Profits Tax, Property Tax, Salaries Tax, Depreciation Allowances, and administration provisions.
- **`CAP117/`** — Stamp Duty Ordinance (a *separate* ordinance from Cap. 112), consolidated, current to 26.2.2026.
- **`DIPN/`** — all 64 current DIPNs (1–63 plus 13A), organized into subfolders by topic (`Profits-Tax/`, `Property-Tax/`, `Salaries-Tax/`, `Stamp-Duty/`, `Depreciation-Allowances/`, `Cross-Border-Transfer-Pricing/`, `Special-Regimes/`, `Other/`).
- **`IRD-Administration/`** — DIPN 6, 11, 31 (objections/appeals, field audit, advance rulings).
- Stamp Office notes (SOIPN 1–8) live under `DIPN/Stamp-Duty/`.
- **`PwC/`** — reserved for saved PwC Worldwide Tax Summaries pages (cross-check source; not yet populated with saved files).
- **`Forms/`** — BIR51/52/54 Profits Tax Return forms + Notes and Instructions, and IRC1952/1953 Notice to File forms, revision 4/2025.

See `Data/DIPN-CHECKLIST.md` for the full document-by-document status, and
`Data/README.md` for the refresh mechanics in more detail.

## What's fully built vs. reference-only

The **five core taxes** (Profits, Property, Salaries, Stamp Duty, Depreciation
& Allowances) have complete study pages: rules, taxable/deductible tables,
computation templates, and a dedicated worked-illustrations page each.

Everything else IRD publishes a DIPN on — transfer pricing, aircraft/ship
leasing concessions, corporate treasury, offshore funds, cross-border DTAs,
estate duty (historical) — is **downloaded and briefly summarized** in the
DIPN Index, but does not have that same depth of treatment yet. Ask Claude to
build a dedicated page for any of these if your team needs deeper coverage.

## Where the worked illustrations come from

Each topic's "Worked Illustrations" page draws on two kinds of source,
labelled inline:

- **From IRD DIPNs/SOIPNs** — official illustrative examples, paraphrased
  (not reproduced verbatim).
- **From Module 9: Principles of Taxation (4th ed.)** — a professional
  taxation qualification manual. Facts are paraphrased; every allowance/rate
  figure has been checked against current law and **corrected where the
  textbook was using a stale amount** (e.g. old personal allowances, the
  pre-2023 flat-15% stamp duty rate) — each correction is flagged inline as
  "Original book figure used X; current law is Y."

A second textbook — *Hong Kong Taxation and Tax Planning* (22nd ed.) — could
**not** be processed: it's a scanned PDF with no text layer, and this build
environment has no OCR or PDF-rendering tools installed (poppler, Ghostscript,
ImageMagick all absent). If you can run it through OCR (e.g. Adobe Acrobat's
"Recognize Text") and provide a text-searchable version, ask Claude to
extract illustrations from it the same way.

## Folder structure

```
index.html                       Hub — links to everything below
pages/
  transaction-checker.html       Search tool: transaction → tax treatment
  dipn-index.html                Searchable catalogue of all 73 DIPN/SOIPN/EDOIPN docs
  profits-tax.html               + profits-tax-illustrations.html
  profits-tax-return-guide.html  + profits-tax-return-finder.html (BIR51/52/54 box guide + search)
  property-tax.html              + property-tax-illustrations.html
  salaries-tax.html              + salaries-tax-illustrations.html (incl. Personal Assessment)
  stamp-duty.html                + stamp-duty-illustrations.html
  depreciation-allowances.html   + depreciation-allowances-illustrations.html
  ird-administration.html        Returns, assessment, objections/appeals, penalties
assets/
  css/main.css                   Shared design system (light/dark aware)
  js/                            Freshness-check logic, search/filter logic, data files
scripts/
  Refresh-Data-Manifest.bat      Double-click after updating Data/ — rescans and re-stamps dates
  update-manifest.ps1            The PowerShell script the .bat wraps
Data/
  CAP112/, CAP117/               Legislation
  DIPN/<topic>/                  DIPNs + SOIPNs, organized by tax topic
  IRD-Administration/            Admin-specific DIPNs
  Forms/                         BIR51/52/54 return forms + notes
  README.md                      Refresh-workflow details and folder map
  DIPN-CHECKLIST.md              Document-by-document download status
```

## Caveats — read before relying on a figure for a filing position

- This is an **internal working document**, not a substitute for professional
  judgement or a final review against the primary legislation.
- CAP112's Part 6 (Depreciation Allowances) and the numbered Schedules did not
  extract cleanly from the currently-saved PDF — those pages' section numbers
  are cross-verified against DIPNs that quote the Ordinance directly, not
  re-derived from a direct grep. Re-verify against a fresh Cap. 112 download
  if you need precision on a specific sub-clause.
- Any figure tied to an **annual Budget measure** (one-off tax reductions,
  elderly-care expense caps, etc.) is flagged rather than guessed where the
  current year's figure wasn't independently confirmed — check the current
  Budget before treating those as final.
- Every page shows a "last reviewed" date and a freshness banner — check both
  before relying on a page for a filing decision.
