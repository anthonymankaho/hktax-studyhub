# HK Tax Study Hub

A study aid for Hong Kong tax — profits tax, property tax, salaries tax, stamp
duty, depreciation allowances and IRD administration — built from the Inland
Revenue Department's own published guidance and from the Inland Revenue
Ordinance (Cap. 112) and Stamp Duty Ordinance (Cap. 117).

**Live site:** <https://anthonymanhk.github.io/hktax-studyhub/>

Static HTML, no server and nothing to install: open `index.html` in a browser.
It is a single self-contained file — the whole Hub, every page, one download.

## ⚠️ Disclaimer — read this first

**This is study material, not professional advice.** Nothing here is tax advice,
no adviser–client relationship is created by reading it, and no one maintaining
it will answer questions about your tax position.

It is written to an internal working standard for one finance team's own
learning and analysis. It is published openly because the underlying material is
public, not because it has been reviewed for anyone else's use. It will contain
mistakes, and it goes out of date whenever the law changes.

**Before relying on any figure or section reference for a filing position,
verify it against the Inland Revenue Ordinance (Cap. 112), the Stamp Duty
Ordinance (Cap. 117), and current IRD guidance.** Every page carries the same
warning for the same reason.

## Licence

Two different things, two different answers:

- **Code** — `scripts/`, `assets/js/`, `assets/css/`: MIT. See [`LICENSE`](LICENSE).
- **Study content** — the prose, tables and worked illustrations in
  `index.html` and `pages/`: **not licensed for redistribution.** These are
  study notes paraphrased from the sources cited inline. Read them, link to
  them; please do not republish them as your own.
- **Cited material** — IRD's DIPNs/SOIPNs, the ordinances, the BIR forms, and
  the textbook the illustrations derive from remain the property of their
  respective owners. This repository does **not** redistribute them; it links to
  the publishers' own copies.

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

Open `index.html` (or the live site). From the card index you can reach:

| Page | Purpose |
|---|---|
| **IRD What's New** | Every item on IRD's What's New page, read against this Hub and marked **enacted** / **bill** / **proposed**, with the exact page each item changed. Open this first after any IRD refresh. |
| **ACCA TX-HKG Question Bank (A / B / C)** | Three pages matching the exam's own three sections — A: 282 filterable standalone MCQs with select-and-check scoring; B: 6 OT case scenarios (30 linked MCQs); C: 8 constructed-response questions with full model answers. B is 2 full sittings' worth; C is 4 full sittings' worth. All computation-checked against `scripts/qbank_tax.py`. |
| **Transaction Checker** | Search any transaction by keyword → Taxable/Non-taxable/Deductible/Non-deductible/Dutiable, with the exact section and a link to the full explanation. |
| **DIPN Index** | Searchable catalogue of all 73 currently-in-force DIPN/SOIPN/EDOIPN documents, with topic, summary, and whether it backs a full study page or is reference-only. |
| **Profits Tax / Property Tax / Salaries Tax / Stamp Duty / Depreciation & Allowances** | The five core topic pages — charging basis, rates, taxable/deductible tables, computation templates, all tied to exact IRO (Cap. 112) / Stamp Duty Ordinance (Cap. 117) sections. |
| **[Topic] — Worked Illustrations** | Companion page per topic (linked from each topic page's Illustrations section) with every worked example — DIPN-sourced and textbook-sourced — in one place. |
| **Profits Tax Return Guide** / **Box Finder** | Box-by-box walkthrough of the actual BIR51/52/54 return forms (linked from the Profits Tax page) — bridges "what the law says" to "what you type into the form," plus a keyword search over every box. |
| **IRD Administration** | Returns, assessment, objections/appeals, provisional tax, penalties — the process layer common to all taxes. |

Every page's header also carries an **AI Prompts** button — see below.

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

### Checking IRD's What's New

Steps 1–3 watch the *saved PDFs*. They cannot see a new announcement on
ird.gov.hk. For that, ask Claude to read
<https://www.ird.gov.hk/eng/new/index.htm> and update the Hub. Claude should:

- Add or update rows in **`pages/ird-updates.html` §2** so the page records
  what was read, on what date, and which page changed.
- Mark each item **enacted** / **bill** / **proposed**. A Policy Address
  measure is *not* law on announcement day — keep the enacted figure as the
  Hub's primary statement and carry the change as a marked note beside it.
- Update the "read on" date in the banner at the top of `ird-updates.html`
  **and** `IRD_READ_DATE` in `scripts/build-combined.py`.
- Re-run the combined build (below).

Last read: **24 September 2026** (38 items, 1 Jun – 16 Sep 2026).

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

A second textbook — *Hong Kong Taxation and Tax Planning* (22nd ed., Ho & Mak)
— **can** now be used, correcting an earlier note here. It is still a scanned
PDF with no text layer and there is still no OCR, so text extraction returns
nothing. But PyMuPDF renders each page to an image, and those images can be
read directly. The workflow that works: locate pages through the book's own
index at the back, convert book page to PDF page (**PDF page = book page + 21**
for this file), render at ~135 dpi, then read. The
[Computation Formats](pages/computation-formats.html) page was built this way.

Two limits: reading is one page at a time, so target chapters rather than
sweeping all 920 pages; and the book states the law only **to 31 May 2024**, so
every rate and allowance taken from it must be re-checked against IRD.

## Folder structure

```
index.html                       GENERATED — the whole Hub in ONE self-contained file
                                 (all pages, data and question banks embedded)
pages/                           THE SOURCES. Edit these, then rebuild.
  ird-updates.html               IRD What's New, marked enacted / bill / proposed
  acca-tx-hkg.html                Exam syllabus mapping + examiner-report digest + sample Qs
  question-bank.html              ACCA TX-HKG Section A practice bank — GENERATED, see below
  question-bank-b.html            ACCA TX-HKG Section B, OT case questions — GENERATED, see below
  question-bank-c.html            ACCA TX-HKG Section C, constructed response — hand-written, see below
  module9-extra-practice.html    Extra paraphrased Module 9 practice Q&A
  transaction-checker.html       Search tool: transaction → tax treatment
  dipn-index.html                Searchable catalogue of all 73 DIPN/SOIPN/EDOIPN docs
  profits-tax.html               + profits-tax-illustrations.html
  profits-tax-entities.html       Sole trader / partnership / corporation computations
  profits-tax-return-guide.html  + profits-tax-return-finder.html (BIR51/52/54 box guide + search)
  property-tax.html              + property-tax-illustrations.html
  salaries-tax.html              + salaries-tax-illustrations.html
  personal-assessment.html        Election mechanics, eligibility, computation
  computation-formats.html        Pro-forma layout per tax, one worked example each
  tax-reconciliation.html         Wrong computation + notes → revised computation illustrations
  stamp-duty.html                + stamp-duty-illustrations.html
  depreciation-allowances.html   + depreciation-allowances-illustrations.html
  ird-administration.html        Returns, assessment, objections/appeals, penalties
assets/
  css/main.css                   Shared design system (light/dark aware)
  js/                            Freshness-check logic, search/filter logic, data files
  qbank.json                     GENERATED — the 282-question Section A bank, source for question-bank.html
  qbank-b.json                   GENERATED — Section B's 3 cases / 15 questions, source for question-bank-b.html
  revision.json                  What's changed in the Hub, rendered into the landing-page notice
scripts/
  build-combined.py              Rebuilds the single-file edition from pages/ + assets/
  qbank_tax.py                   HK tax computation module backing every computational MCQ
  build-qbank.py                 Generates Section A -> assets/qbank.json
  build-question-bank-page.py    Renders assets/qbank.json -> pages/question-bank.html
  build-qbank-b.py               Generates Section B's 3 cases -> assets/qbank-b.json
  build-question-bank-b-page.py  Renders assets/qbank-b.json -> pages/question-bank-b.html
  audit-layout.js                Playwright: every panel, desktop + phone, overflow/console-error gate
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

## The two editions, and how to rebuild

There are two ways to read the Hub, from **one** set of sources:

- **Single-file app** — a tabbed frame: sticky topbar, a bilingual card index,
  one panel per page, jump-search and a dark-mode toggle. The build writes it
  to a single file, `index.html`, which is both the landing page of the
  published site and the one file to share or download — every page, data
  table and question bank is embedded, nothing is fetched at run time.
- **Multi-file** — `pages/*.html` opened individually. These are the sources
  you edit, and they stay browsable on their own.

**`index.html` is generated. Never hand-edit it** — including
`index.html`, which used to be a hand-written hub page and no longer is. Edit
the page under `pages/` and rebuild:

```
python scripts\build-combined.py
```

The builder namespaces every `id`/anchor per page (`salaries-tax__allowances`),
rewrites cross-page links into tab links, inlines the three searchable data
tables, and prints a corruption check. A hand-built combined file previously
lost 994 em-dashes and mangled two Chinese passages by concatenating with the
wrong encoding; the builder reads the clean sources as UTF-8 and writes UTF-8,
so that failure cannot recur.

When adding a page, put it in `pages/`, add a row to `PAGES` in
`scripts\build-combined.py` (id, file, English label, Chinese label, group,
Chinese summary, search keywords), add its nav link to the other pages, and
rebuild.

## The revision notice

`assets/revision.json` records what has changed in the Hub and what is still
missing, with a reason for each gap. `scripts/build-combined.py` renders it
into a collapsible notice on the landing page **at build time** - there is no
runtime fetch, so it works offline in the single-file edition and the data
lives in exactly one place.

To update it, edit the JSON and rebuild. Keep the two lists honest: an item
belongs in `sections_need_increase` only if it is genuinely absent, with
`blocked_by` saying whether that is external, copyright, not-yet-done or
unverified.

Dated IRD changes belong on the **IRD What's New** page instead. This notice
covers changes to the Hub itself.

## Two years of allowances, and the guard that keeps them straight

Allowance figures appear on the Hub in **two bases**:

- **YA 2026/27** — current law, and what you use for real work.
- **YA 2025/26** — what ACCA TX-HKG examines from the June 2025 sitting
  through **December 2026**. IRD publishes 2024/25 and 2025/26 as a single
  column, so one set of figures covers the whole J25–D26 run.

Only the allowances differ. **Every rate is identical on both bases** —
progressive bands, the 15%/16% standard rate, 8.25%/16.5% and 7.5%/15% profits
tax, property tax 15%, the 60% initial allowance, the 10/20/30% pools and the
35% donations cap.

`ALLOWANCES` in `scripts/build-combined.py` holds the figures in one table and
**fails the build** if an allowance line states a figure belonging to neither
year. Lines marked dual-stated, historical or proposed are exempt. When the
next Budget moves an allowance, update that one table — the build will then
point at every line still carrying the old number.

## ACCA TX-HKG Question Bank — Sections A, B and C

Three pages, one for each real exam section, cross-linked by a Section A ⇄ B
⇄ C switch strip at the top of each:

- **`pages/question-bank.html` (Section A)** — a filterable bank of 282
  original standalone multiple-choice questions spanning all five syllabus
  areas (tax administration, salaries tax, profits tax, property tax,
  personal assessment). Filter by area or difficulty, search by keyword or
  section reference, or pull a shuffled **Random 15** for a timed practice
  run.
- **`pages/question-bank-b.html` (Section B)** — 6 original OT case
  scenarios (30 linked questions = 2 full sittings' worth; a real Section B
  is 3 cases / 15 questions / 30 marks), matching the exam's own
  case-question format: one set of facts, five questions against it,
  spanning more than one syllabus area at once — e.g. a case integrating an
  employee's rental-value benefit, her own let property's NAV, her salaries
  tax computation, *and* whether she should elect personal assessment, all
  from the same figures. No filters here; the three cases are fixed and
  always shown in full, with a **Reset all three cases** button for a clean
  second attempt.
- **`pages/question-bank-c.html` (Section C)** — 8 original constructed-
  response questions (four 15-mark, four 25-mark = 4 full sittings' worth),
  spanning salaries tax, profits tax, property tax, partnerships, badges of
  trade, depreciation allowances, offshore claims and IRD administration, in the
  exam's own long-form
  format: no multiple choice, just a full scenario and a `<details>`-
  revealed model answer laid out as a real computation with marks
  allocated line by line, the same proforma/`.rule`/`.dbl` table style as
  the Tax Reconciliation page.

Sections A and B share the same grading mechanic: each question's four
options are real radio buttons. Select one and click **Show answer** and it
marks your choice **Correct**/**Incorrect** (or, if you didn't pick anything,
says so rather than silently grading a blank) before revealing the
explanation and section reference — 1 correct answer = 1 mark, tallied live
in the **Score** counter. Re-showing an already-checked question re-grades it
from whatever is currently selected rather than adding a second mark, so
changing your mind and checking again can't inflate the score. On Section A,
**Random 15** resets the score and clears every answer for a clean attempt,
and filtering/**Show all** never touch it; on Section B, the dedicated
**Reset** button does the same for all three cases at once. Section C has no
scoring — it's marked by comparing your own working to the model answer.

Every computational question's correct answer **and** (on Sections A and B)
its wrong-option distractors, and every figure in Section C's eight model
answers, are generated from `scripts/qbank_tax.py` — the same small tax-
computation module the Hub's worked illustrations use — so the arithmetic
cannot drift from the explanation. Distractors are not arbitrary wrong
numbers; each reproduces a specific error the examining team has reported
(e.g. omitting the treble-tax element of a s.80(2) penalty, applying the
standard rate to net chargeable income instead of net income before
allowances, spreading a lease premium over the full term instead of the
36-month cap, stating a R&D deduction's total instead of the additional
amount still to be deducted). A case's five questions (Section B) or a long
question's two parts (Section C) are also checked for **internal
consistency** — a figure question 3 relies on is the same figure question 1
established, not a fresh unrelated number.

To regenerate Section A after editing a question or adding new ones:

```
python scripts\build-qbank.py                 # writes assets/qbank.json
python scripts\build-question-bank-page.py    # writes pages/question-bank.html
python scripts\build-combined.py              # folds it into index.html
```

Section B is generated the same way, from its own smaller pair of scripts:

```
python scripts\build-qbank-b.py               # writes assets/qbank-b.json
python scripts\build-question-bank-b-page.py  # writes pages/question-bank-b.html
python scripts\build-combined.py
```

Section C (`pages/question-bank-c.html`) is hand-written prose and proforma
tables, like the Tax Reconciliation page, rather than JSON-driven — with only
8 questions there is more value in writing them directly than building a
generator for two items. Its figures are still verified by running the same
`qbank_tax.py` functions in a scratch calculation first (see the build log
for the exact commands), before being transcribed into the page.

The filter/search/random-practice/grading scripts live **inside**
`<main class="content">` on all three pages and are scoped by **class**, never
by `id` — `build-combined.py`'s namespacing rewrites every `id="..."` per
panel but cannot see into a `<script>`, so any interactive page must hook its
own JS by class/data-attribute, and the script must sit inside `<main>` or
the builder (which extracts only that element) drops it silently. Section
B's own **Reset** button was first built with `id="qbank-reset"` and
`document.querySelector('#qbank-reset')`, which worked standalone but
silently did nothing once combined — exactly the failure this rule exists to
prevent, caught by testing the combined build specifically rather than only
the standalone page. Fixed by switching to `class="qbank-reset-btn"`.

## The "AI Prompts" button

Every page's header carries an **AI Prompts** button (`assets/js/ai-prompt.js`).
Clicking it copies a hardened Hong Kong tax prompt template to the clipboard —
with a fallback modal showing the text pre-selected if the browser blocks the
clipboard API (as Chrome does on a `file://` page) — so it can be pasted into
whatever AI the user already has open (Edge Copilot, Chrome Gemini, or any
chat AI) to ask about a transaction not covered by the Transaction Checker.

There is **no API for a webpage to push a prompt directly into another
browser feature's own chat box** — this is a copy-to-clipboard helper, not a
live integration, and the modal is explicit about that.

The template itself is deliberately stricter than a naive "act as a tax
specialist" prompt, because a general-purpose AI asked to cite a specific
IRO section or DIPN number is exactly where it will confidently invent a
plausible-looking but wrong one:

- It instructs the AI to **say so explicitly rather than guess** when it is
  not certain a section or DIPN reference is correct.
- It states the **year of assessment basis to default to** (2026/27; 2025/26
  for the ACCA TX-HKG exam basis), rather than leaving that to the model's
  own guess — this Hub is built around exactly that dual-year distinction.
- The modal always carries a warning that the AI's answer is **not checked
  by this Hub**, unlike the Transaction Checker's, and needs the same
  independent verification as everything else here.

`ai-prompt.js` is loaded two ways from **one file**: as an external
`<script src="../assets/js/ai-prompt.js">` on every `pages/*.html`, and
inlined by `build-combined.py` (which reads the same file and writes its
content into its own `<script>` block) for the combined single-file editions
— so the prompt text and the copy/fallback logic live in exactly one place.

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
- Items marked **proposed** on the IRD What's New page (currently the two 2026
  Policy Address measures — the $160,000 child allowance for second and
  subsequent children, and the $20,000 newborn-family stamp duty waiver) are
  **not law**. Each needs an amendment ordinance. Quote the enacted figure in
  any computation until the ordinance is gazetted.
