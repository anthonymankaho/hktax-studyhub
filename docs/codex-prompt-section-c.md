# Task: add new Section C questions to the HK Tax Study Hub

You are adding **original ACCA TX-HKG Section C (constructed response) questions
with full model answers** to an existing Hong Kong tax study site.

Work on this machine, in `C:\Users\User\Desktop\HKTAX STUDYHUB - CLAUDE`.

---

## 1. What Section C is

Section C of the real TX-HKG paper is **two long-form questions per sitting — one
worth 15 marks and one worth 25 marks**. No multiple choice: the candidate
prepares an actual computation, or writes an explanation, exactly as they would
in the exam.

The page already holds **4 questions (2 full sittings' worth)**:

| # | Scenario | Marks | Covers |
|---|---|---|---|
| Q1 | Mr Ivan Ho | 15 | Salaries tax computation + personal assessment advice (interest makes electing worthwhile) |
| Q2 | XYZ Trading Ltd | 25 | Corporate profits tax computation: depreciation, capital legal fees, R&D, DA, loss b/f, two-tier, no group relief |
| Q3 | Mr Anthony Cheung | 15 | Property tax over two properties: irrecoverable rent, 36-month premium cap; advice on transferring to a company |
| Q4 | Summit & Vale Partners | 25 | Partnership: s.17(2) add-backs, DA, each partner taxed at own rates on apportioned band, corporate partner can't elect PA |

**Your job: add Q5 and Q6 (one 15-mark, one 25-mark) — a third full sitting.**
Ask the requester if they want more than one sitting's worth.

### Pick topics that are not already covered

Good candidates, roughly in order of value:

- **Depreciation allowances in depth** — industrial/commercial buildings
  allowances (20% initial + 4% annual on cost), the land/construction cost split,
  balancing allowance or charge on sale of a building. *(But read §4 on
  `da_pool()` first — it does not model balancing charges.)*
- **Badges of trade / capital vs revenue** — a discursive question: is this gain
  trading profit or a capital receipt? Good for a 15-mark written answer with
  little computation.
- **Source of profits / an offshore claim** — DIPN 21, the operations test,
  contract-effected test, burden of proof under s.68(4), what evidence IRD
  expects. Also strongly discursive.
- **IRD administration** — objection and appeal procedure and deadlines,
  penalties under s.80(2)/s.82A/s.82, holdover of provisional tax, field audit.
- **Personal assessment for a married couple** — joint vs separate election
  compared with supporting calculations, given the 2018/19 change.

Do not duplicate what Q1–Q4 already test. A new question may revisit a *tax
head* already used, as long as the *mechanics* it tests are different.

---

## 2. Non-negotiable: every figure comes from `scripts/qbank_tax.py`

This is the single rule the whole project is built on. **Never hand-compute a
figure and type it in.** Every number in a question or a model answer — and the
intermediate lines of the computation — must be produced by calling the
functions in `scripts/qbank_tax.py`, so the arithmetic can never drift from the
words around it.

Available functions:

```
progressive(nci)                     standard_rate(net_income)
salaries_tax(net_income, allowances) rental_value(income, kind)
donation_cap(base)                   net_assessable_value(rent, rates_paid_by_owner,
property_tax(nav)                        premium, lease_months, months_let,
two_tier(profit, corporate=True)         irrecoverable, deposit_forfeited)
two_tier_partnership(profit, shares) rnd_deduction(type_a, type_b)
da_pool(wdv_bf, additions, disposals, rate, initial)
hire_purchase_ia(deposit, instalments_paid, capital_per_instalment)
personal_assessment(total_income, interest, concessionary, losses, allowances_total)
s80_max_penalty(tax_undercharged)    late_payment(tax, months_overdue)
money(x)
```

**Workflow:** write a throwaway script that computes every figure for your new
question, run it, read the output, and only then write those exact figures into
the HTML. Keep the script's output — paste a summary of it into your handover so
the figures are auditable.

```bash
cd "C:/Users/User/Desktop/HKTAX STUDYHUB - CLAUDE"
python3 - <<'EOF'
import sys; sys.path.insert(0, "scripts")
import qbank_tax as T
def M(x): return "{:,.0f}".format(round(x))
# ... your computation, printing every intermediate line ...
EOF
```

Also check **internal consistency**: a figure part (b) relies on must be the same
figure part (a) produced. That is the whole point of a long-form question.

---

## 3. Which year of assessment

The Hub is written on **two bases** and you must respect both:

- **YA 2026/27** — current law. Use this by default.
- **YA 2025/26** — what ACCA TX-HKG examines through the December 2026 sitting.
  IRD publishes 2024/25 and 2025/26 as one column.

Only *allowances* differ between the two. **Every rate is identical** —
progressive bands, the 15%/16% standard rate, 8.25%/16.5% and 7.5%/15% profits
tax, property tax 15%, the 60% initial allowance, 10/20/30% pools, the 35%
donations cap. `qbank_tax.ALLOWANCES` holds both sets; `CURRENT_YA` and
`EXAM_YA` name them.

---

## 4. Known traps — read before you start

**a. `da_pool()` does not model balancing charges.** If disposal proceeds exceed
the pool's residue, the pool goes negative and the function silently returns
`aa=0` and a `total` that is just the initial allowance — it does *not* compute
the balancing charge that should be added back. Either keep disposals small
enough that the pool stays positive, or compute the balancing charge yourself
and extend `da_pool()` properly (with a test) rather than working around it
silently. This is why Q4's disposal figure is modest.

**b. The build has an allowance guard that will fail your build.**
`check_allowances()` in `scripts/build-combined.py` scans every line containing
the word "allowance" and rejects any figure that matches a known allowance
amount from *neither* year. It is deliberately strict because a stale allowance
in a tax reference is a silent, costly error.

It does produce false positives: if an allowance keyword and an *unrelated*
figure land on the same line, and that figure happens to equal a known allowance
(e.g. `$130,000` of mortgage interest on a line mentioning "married" — 130,000 is
the child allowance), the build fails. **Change your figure; do not weaken the
guard.** Lines containing "dual", "stale", "original book" or "proposed" are
exempt.

**c. Section C is hand-written HTML — unlike Sections A and B.** A and B are
generated from JSON by Python scripts. Section C is edited directly, because
with only a handful of long questions a generator isn't worth it. Edit
`pages/question-bank-c.html` by hand, then run the combined build.

**d. Page-local `<style>` must not contain `@media`.** `page_style()` in the
build script aborts on at-rules. Responsive CSS goes in `assets/css/main.css`.

**e. If you add any JavaScript, hook it by class, never by `id`, and put the
`<script>` inside `<main class="content">`.** The combined build namespaces every
`id="..."` per panel but cannot see inside a `<script>`, so an id-based selector
works standalone and silently dies in the combined file. Content outside
`<main>` is dropped from the combined build entirely. (Section C currently has
no JS — `<details>` handles the reveal natively. Keep it that way if you can.)

---

## 5. The HTML pattern to follow

Copy the structure of the existing Q1–Q4 exactly. Classes already defined in the
page's `<style>` block:

| Class | Use |
|---|---|
| `.qbox` | The scenario box |
| `.qbox h3` + `.marks` | Scenario heading with the mark total floated right |
| `.qbox .part` | Each `(a) … (10 marks)` part line |
| `details.model-answer` + `<summary>Show model answer</summary>` | The reveal |
| `.proforma` wrapping `<table class="right">` | A computation |
| `<caption>` | Names the computation, e.g. "(a) Ivan Ho — Salaries Tax Computation, YA 2026/27" |
| `.sub` / `.sub2` | Indent levels within a computation |
| `.rule` | Row with a single top rule — a subtotal |
| `.dbl` | Row with a double underline — a final total |
| `<td class="num">` | Right-aligned figure; negatives in parentheses |
| `.note-no` | The `(3 marks)` mark allocation, in brand colour |

Skeleton:

```html
<section class="block" id="q5">
  <h2>Question 5 — [Name] (15 marks)</h2>
  <div class="qbox">
    <h3>Scenario<span class="marks">15 marks</span></h3>
    <p>[facts]</p>
    <p class="part">(a) [requirement]. (10 marks)</p>
    <p class="part">(b) [requirement]. (5 marks)</p>
  </div>
  <details class="model-answer">
    <summary>Show model answer</summary>
    <div class="proforma">
      <table class="right">
        <caption>(a) [Name] — [Computation], YA 2026/27</caption>
        <tbody>
          <tr><th>[Opening line]</th><td class="num">1,020,000</td></tr>
          <tr><td class="sub">Less: [item] <span class="note-no">(1 mark)</span></td><td class="num">(60,000)</td></tr>
          <tr class="rule"><th>[Subtotal]</th><td class="num">960,000</td></tr>
          <tr class="dbl"><th>[Total] <span class="note-no">(2 marks)</span></th><td class="num">92,840</td></tr>
        </tbody>
      </table>
    </div>
    <p style="font-size:13px;color:var(--text-muted)">Total for part (a): 10 marks. [Name the one or two errors this question is designed to catch.]</p>
    <p style="margin-top:14px"><strong>(b) (5 marks):</strong> [written answer, with marks noted inline]</p>
  </details>
</section>
```

Also update, in the same file:
- the `<aside class="toc">` list — add `<a href="#q5">Question 5 — … (15 marks)</a>`
- the `<p class="subtitle">` — the question count and "N full sittings' worth"

---

## 6. Content quality bar

- **Everything must be original.** Write your own scenarios, names and figures.
  Do **not** reproduce any ACCA question, model answer or examiner's report text.
  Where a question tests something the examining team has publicly reported as a
  weak area, the *topic* and the *error tested* may come from that public report
  — the wording and facts must be yours.
- **Allocate marks line by line** in the model answer, the way a real marking
  scheme does, using `.note-no`. Parts must sum to the stated total.
- **Name the trap.** Every existing question closes part (a) with a sentence
  identifying the specific error it is designed to catch (e.g. "applying the
  standard rate to income *after* allowances instead of before"). Do the same —
  it is most of the teaching value.
- Cite the section (`s.16B`, `s.5B(4)`, `s.17(2)`) wherever a rule is applied.
- British English, and the house voice: plain, direct, no filler.

---

## 7. Build, verify, publish

```bash
cd "C:/Users/User/Desktop/HKTAX STUDYHUB - CLAUDE"

# 1. Rebuild the single-file/combined editions (regenerates index.html,
#    combined.html and "HK Tax Study Hub - Combined.html" from pages/)
python scripts/build-combined.py

# 2. Layout audit: every panel, desktop 1400px and phone 380px.
#    Exits non-zero on horizontal overflow or any console error.
#    Playwright is not a project dependency - install it where you run this:
npm install --no-save playwright && npx playwright install chromium
node scripts/audit-layout.js
```

The build must print `allowance guard: …`, `corruption check '??': 0` and
`corruption check '§': 0`. **Never hand-edit `index.html`, `combined.html` or
`HK Tax Study Hub - Combined.html`** — all three are generated.

Then check in a browser that each new `<details>` opens and the tables line up,
in both light and dark mode.

### Publishing — push to BOTH remotes

This repo is deliberately dual-homed across two GitHub accounts, both serving a
live site. **Push to both, or one site silently falls behind.**

```bash
gh auth switch --user anthonymankaho && git push origin master
gh auth switch --user AnthonyManhk  && git push backup master
```

Then **verify the remotes actually moved** rather than trusting the push:

```bash
git fetch origin -q && git fetch backup -q
git rev-parse --short HEAD origin/master backup/master   # all three must match
```

Live sites (both should serve your change once Pages rebuilds):
- <https://anthonymankaho.github.io/hktax-studyhub/>
- <https://anthonymanhk.github.io/hktax-studyhub/>

A wrong-account push fails with `403 Permission … denied` (public repo) or
`Repository not found` (private) — that is an account mismatch, not a missing
repo. `gh auth switch` is the fix.

Finally, update `README.md` — the "Start here" table row and the
"ACCA TX-HKG Question Bank" section both state the question counts.

---

## 8. Hand back

Report:
1. The new questions, with their topic, marks and what error each is built to catch.
2. **The verification output** — the figures your `qbank_tax.py` script produced.
3. Build and audit results.
4. Confirmation that both remotes and both live sites carry the change.
5. Anything you found wrong or fragile that you did not fix.
