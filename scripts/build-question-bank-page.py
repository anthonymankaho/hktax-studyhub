#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render pages/question-bank.html from assets/qbank.json.

The filter toolbar and quiz logic are plain JS scoped to a `.qbank-app`
wrapper by CLASS, never by id. build-combined.py's localise() rewrites every
id="..." (and matching href="#...") to a per-panel-namespaced value so 20+
pages can share one document, but it has no way to find and rewrite an id
string sitting inside a <script>. A script that called
document.getElementById('some-id') would work on the standalone page and
silently break the moment this page is folded into the combined app. Classes
and data-attributes are not touched by that rewrite, so the script uses only
those. The script must also live INSIDE <main class="content"> - build-
combined.py's build_panel() extracts exactly that element and nothing
outside it, so a script placed after </main> (as transaction-checker.html's
external checker.js is) is silently dropped from the combined build.

Run from the project root, after scripts/build-qbank.py:
    python scripts/build-question-bank-page.py
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qnote_widget  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QBANK = os.path.join(ROOT, "assets", "qbank.json")
OUT = os.path.join(ROOT, "pages", "question-bank.html")

AREA_ORDER = ["A", "B", "C", "D", "E"]


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


NAV = """    <nav class="site-nav">
      <a href="../index.html">Hub</a>
      <a href="ird-updates.html">IRD What's New</a>
      <a href="acca-tx-hkg.html">ACCA TX-HKG</a>
      <a href="question-bank.html" class="active">Question Bank A</a>
      <a href="question-bank-b.html">Question Bank B</a>
      <a href="question-bank-c.html">Question Bank C</a>
      <a href="computation-formats.html">Computation Formats</a>
      <a href="tax-reconciliation.html">Tax Reconciliation</a>
      <a href="transaction-checker.html">Transaction Checker</a>
      <a href="dipn-index.html">DIPN Index</a>
      <a href="profits-tax.html">Profits Tax</a>
      <a href="profits-tax-entities.html">Profits Tax by Entity</a>
      <a href="property-tax.html">Property Tax</a>
      <a href="salaries-tax.html">Salaries Tax</a>
      <a href="personal-assessment.html">Personal Assessment</a>
      <a href="stamp-duty.html">Stamp Duty</a>
      <a href="depreciation-allowances.html">Depreciation &amp; Allowances</a>
      <a href="ird-administration.html">IRD Administration</a>
      <a href="https://anthonymanhk.github.io/hkfrs-as-study-platform/" target="_blank" rel="noopener" title="Sister platform: HKFRS and HKAS">HKFRS / HKAS &#8599;</a>
    </nav>"""


def render_item(q):
    letters = "ABCD"
    opts = "\n".join(
        '        <li><label><input type="radio" name="opt-%s" value="%d"> %s</label></li>'
        % (q["id"], i, esc(o))
        for i, o in enumerate(q["options"])
    )
    ref = ('<span class="qbank-ref">%s</span>' % esc(q["ref"])) if q.get("ref") else ""
    return (
        '      <div class="qbank-item" data-area="%s" data-diff="%s" data-kind="%s" data-answer="%d">\n'
        '        <div class="qbank-meta">'
        '<span class="qbank-tag qbank-tag-%s">%s &middot; %s</span> '
        '<span class="qbank-topic">%s</span> '
        '<span class="qbank-diff qbank-diff-%s">%s</span></div>\n'
        '        <p class="qbank-q"><strong>%s.</strong> %s</p>\n'
        '        <ol type="A" class="qbank-opts">\n%s\n        </ol>\n'
        '        <button type="button" class="qbank-reveal">Show answer</button>\n'
        '        <div class="qbank-ans" hidden>\n'
        '          <p class="qbank-verdict"></p>\n'
        '          <p class="qbank-answer-line"><strong>Correct: %s &mdash; %s.</strong></p>\n'
        '          <p>%s</p>\n'
        '          %s\n'
        '        </div>\n'
        '      </div>\n'
        % (q["area"], q["difficulty"], q["kind"], q["answer"],
           q["area"], q["area"], esc(q["area_name"]),
           esc(q["topic"]),
           q["difficulty"], q["difficulty"].capitalize(),
           q["id"], q["q"],
           opts,
           letters[q["answer"]], esc(q["options"][q["answer"]]),
           q["explain"],
           ref)
    )


def main():
    with io.open(QBANK, encoding="utf-8") as f:
        data = json.load(f)
    questions = data["questions"]
    areas = data["areas"]
    total = len(questions)
    counts = {a: sum(1 for q in questions if q["area"] == a) for a in AREA_ORDER}
    n_topics = len(set(q["topic"] for q in questions))
    n_computational = sum(1 for q in questions if q["kind"] == "computational")

    area_chips = ['        <button type="button" class="qbank-chip active" data-value="all">All areas (%d)</button>' % total]
    for a in AREA_ORDER:
        area_chips.append(
            '        <button type="button" class="qbank-chip" data-value="%s">%s &middot; %s (%d)</button>'
            % (a, a, esc(areas[a]), counts[a]))

    coverage_rows = "\n".join(
        "          <tr><td>%s</td><td>%s</td><td>%d</td></tr>" % (a, esc(areas[a]), counts[a])
        for a in AREA_ORDER
    )

    items_html = "\n".join(render_item(q) for q in questions)

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="A study aid for Hong Kong tax - profits, property and salaries tax, stamp duty, depreciation allowances and personal assessment - built from IRD guidance and the Inland Revenue Ordinance. Not professional advice.">
<title>Question Bank — HK Tax Study Hub</title>
<link rel="stylesheet" href="../assets/css/main.css">
<style>
  .qbank-section-switch{display:flex;gap:8px;margin:10px 0 4px}
  .qbank-section-switch a{border:1px solid var(--border);background:var(--surface-alt);color:var(--text);border-radius:20px;padding:5px 14px;font-size:12.5px;text-decoration:none}
  .qbank-section-switch a.active{background:var(--brand);color:#fff;border-color:var(--brand)}
  .qbank-toolbar{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:14px 16px;margin:14px 0;position:sticky;top:60px;z-index:10;box-shadow:var(--shadow)}
  .qbank-filter-group{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px}
  .qbank-chip{border:1px solid var(--border);background:var(--surface-alt);color:var(--text);border-radius:20px;padding:5px 12px;font-size:12.5px;cursor:pointer;font-family:inherit}
  .qbank-chip.active{background:var(--brand);color:#fff;border-color:var(--brand)}
  .qbank-search{width:100%%;padding:9px 12px;border:1px solid var(--border);border-radius:8px;background:var(--surface);color:var(--text);font-size:14px;font-family:inherit;margin:6px 0}
  .qbank-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:6px}
  .qbank-btn{border:1px solid var(--brand);background:var(--brand);color:#fff;border-radius:8px;padding:7px 14px;font-size:13px;cursor:pointer;font-family:inherit}
  .qbank-btn.secondary{background:var(--surface);color:var(--brand)}
  .qbank-count{font-size:12.5px;color:var(--text-muted)}
  .qbank-item{background:var(--surface);border:1px solid var(--border);border-left:4px solid var(--brand);border-radius:var(--radius);padding:14px 16px;margin:12px 0;box-shadow:var(--shadow)}
  .qbank-meta{font-size:11px;text-transform:uppercase;letter-spacing:.03em;margin-bottom:6px}
  .qbank-tag{font-weight:700;color:var(--brand);margin-right:6px}
  .qbank-topic{color:var(--text-muted);margin-right:6px}
  .qbank-diff{padding:1px 8px;border-radius:10px;background:var(--surface-alt);color:var(--text-muted)}
  .qbank-diff-hard{background:var(--warn-bg);color:var(--warn-text)}
  .qbank-q{margin:6px 0 8px;font-size:14.5px}
  .qbank-opts{margin:0 0 10px 22px;padding:0;font-size:14px}
  .qbank-opts li{margin:3px 0}
  .qbank-reveal{border:1px solid var(--border);background:var(--surface-alt);color:var(--text);border-radius:6px;padding:5px 12px;font-size:12.5px;cursor:pointer;font-family:inherit}
  .qbank-ans{margin-top:10px;padding-top:9px;border-top:1px dotted var(--border);font-size:13.5px}
  .qbank-answer-line strong{color:var(--ok-text)}
  .qbank-ref{display:inline-block;margin-top:4px;font-size:11.5px;color:var(--text-muted);border:1px solid var(--border);border-radius:4px;padding:1px 7px}
  .qbank-opts label{display:flex;align-items:flex-start;gap:8px;cursor:pointer;padding:2px 4px;border-radius:4px}
  .qbank-opts label:hover{background:var(--surface-alt)}
  .qbank-opts input[type="radio"]{margin-top:3px;flex-shrink:0}
  .qbank-verdict{font-weight:700;padding:6px 10px;border-radius:6px;margin:0 0 8px;font-size:13.5px}
  .qbank-verdict:empty{display:none;margin:0;padding:0}
  .qbank-verdict-ok{background:var(--ok-bg);color:var(--ok-text);border:1px solid var(--ok-border)}
  .qbank-verdict-bad{background:var(--bad-bg);color:var(--bad-text);border:1px solid var(--bad-border)}
  .qbank-verdict-warn{background:var(--warn-bg);color:var(--warn-text);border:1px solid var(--warn-border)}
  .qbank-score{font-size:12.5px;font-weight:700;color:var(--brand);background:var(--surface-alt);border:1px solid var(--border);border-radius:20px;padding:4px 12px;margin-left:auto}
@@QNOTE_CSS@@</style>
</head>
<body>
<header class="site-header">
  <div class="bar">
    <div class="brand">HK Tax Study Hub<small>Study aid — not professional advice</small></div>
%s
    <button id="theme-toggle" title="Toggle light/dark" style="background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.3);color:#fff;border-radius:6px;padding:6px 10px;cursor:pointer;font-size:12px">Theme</button>
  </div>
</header>

<div class="shell">
  <aside class="toc">
    <h4>On this page</h4>
    <a href="#overview">What this is</a>
    <a href="#coverage">Coverage by syllabus area</a>
    <a href="#howtouse">How to use it</a>
    <a href="#tool">The question bank</a>
    <a href="#copyright">Originality</a>
  </aside>

  <main class="content">
   <div class="qbank-app">
    <div class="page-title">
      <div>
        <span class="badge badge-common">ACCA TX-HKG</span>
        <h1>Practice Question Bank</h1>
        <p class="subtitle">ACCA TX-HKG &mdash; Section A &middot; %d original multiple-choice questions across all five syllabus areas, every computational answer generated and checked against the Hub's own tax-computation engine so the arithmetic cannot drift from the explanation.</p>
      </div>
    </div>

    <div class="qbank-section-switch">
      <a href="question-bank.html" class="active">Section A</a>
      <a href="question-bank-b.html">Section B</a>
      <a href="question-bank-c.html">Section C</a>
    </div>

    <section class="block" id="overview">
      <h2>What this is</h2>
      <p class="lede">A large, filterable bank of original Section A-style MCQs, built to mirror the ACCA TX-HKG syllabus weighting and the errors the examining team has actually reported — not a copy of any past paper or examiner's report question.</p>
      <div class="callout tip">
        <span class="lbl">How the computational questions were built</span>
        Every computational question's correct answer <em>and</em> its wrong-option distractors come from the same small Python tax-computation module (<code>scripts/qbank_tax.py</code>) that this Hub's other worked illustrations use. The distractors are not arbitrary wrong numbers — each one reproduces a specific error pattern the examining team has reported (forgetting the treble-tax element of a s.80(2) penalty, applying the standard rate to net chargeable income instead of net income before allowances, spreading a lease premium over the full term instead of the 36-month cap, and so on).
      </div>
    </section>

    <section class="block" id="coverage">
      <h2>Coverage by syllabus area</h2>
      <table>
        <thead><tr><th>Area</th><th>Syllabus area</th><th>Questions</th></tr></thead>
        <tbody>
%s
          <tr><td colspan="2"><strong>Total</strong></td><td><strong>%d</strong></td></tr>
        </tbody>
      </table>
      <p class="lede">Spread over %d distinct topics; %d of the %d questions are computational (the rest test a rule, a deadline or a distinction conceptually).</p>
    </section>

    <section class="block" id="howtouse">
      <h2>How to use it</h2>
      <ul>
        <li>Filter by <strong>syllabus area</strong> or <strong>difficulty</strong>, or type a keyword or section reference (e.g. <code>s.16B</code>, "premium", "two-tier") into the search box — the filters combine.</li>
        <li><strong>Random 15</strong> pulls a fresh, shuffled set of 15 questions from whatever the current filters allow — close to a real Section A sitting's length and a reasonable practice pace of under two minutes each. It also resets the score and clears every answer, so each draw is a clean attempt.</li>
        <li><strong>Select an option</strong>, then click <strong>Show answer</strong> — it marks your choice Correct or Incorrect, then reveals the full explanation and section reference. 1 correct answer = 1 mark; the <strong>Score</strong> counter at the top right of the toolbar counts marks scored out of questions checked so far.</li>
        <li><strong>Show all</strong> clears the Random 15 selection and returns to the ordinary filtered view — it does not affect the score.</li>
      </ul>
    </section>

    <section class="block" id="tool">
      <h2>The question bank</h2>
      <div class="qbank-toolbar">
        <div class="qbank-filter-group" data-filter="area">
%s
        </div>
        <div class="qbank-filter-group" data-filter="diff">
          <button type="button" class="qbank-chip active" data-value="all">All difficulties</button>
          <button type="button" class="qbank-chip" data-value="easy">Easy</button>
          <button type="button" class="qbank-chip" data-value="medium">Medium</button>
          <button type="button" class="qbank-chip" data-value="hard">Hard</button>
        </div>
        <input type="search" class="qbank-search" placeholder="Search keyword or section, e.g. s.16B, premium, two-tier…">
        <div class="qbank-actions">
          <button type="button" class="qbank-btn">Random 15</button>
          <button type="button" class="qbank-btn secondary">Show all</button>
          @@QNOTE_BTN@@
          <span class="qbank-score" title="Correct answers out of questions you've checked so far &mdash; resets when you draw a new Random 15">Score: 0 / 0</span>
          <span class="qbank-count">Showing %d of %d</span>
        </div>
      </div>

      <div class="qbank-list">
%s
      </div>
    </section>

    <section class="block" id="copyright">
      <h2>Originality</h2>
      <p>Every question on this page was written for this Hub. Where a question tests something the ACCA examining team has publicly reported as a weak area, the <em>topic</em> and the <em>error it tests</em> are drawn from that public report — that is the point of practising it — but the scenario, names, figures and wording are original, and no ACCA question, model answer or examiner's report text is reproduced. See the <a href="acca-tx-hkg.html#copyright">ACCA TX-HKG page</a> for the fuller statement of what is and is not reproduced anywhere on this Hub.</p>
    </section>

    <div class="section-nav">
      <a href="acca-tx-hkg.html">&larr; ACCA TX-HKG</a>
      <a href="question-bank-b.html">Question Bank B &rarr;</a>
    </div>

    <script>
    (function(){
      var root = document.currentScript.closest('.qbank-app');
      if (!root) return;
      var items = Array.prototype.slice.call(root.querySelectorAll('.qbank-item'));
      var state = { area: 'all', diff: 'all', q: '', mode: 'filter' };
      var countEl = root.querySelector('.qbank-count');
      var scoreEl = root.querySelector('.qbank-score');
      var randomPool = [];
      var letters = ['A', 'B', 'C', 'D'];
      // Maps a .qbank-item element to true (correct), false (incorrect), or
      // 'unanswered' (revealed with no option picked) once it has been
      // graded. Re-showing an already-graded item recomputes its entry from
      // whatever is currently selected rather than adding a second entry, so
      // clicking "Show answer" repeatedly can never inflate the score.
      var grades = new Map();

      function updateScore(){
        if (!scoreEl) return;
        var correct = 0, answered = 0;
        grades.forEach(function(v){
          if (v === true || v === false) { answered++; if (v === true) correct++; }
        });
        scoreEl.textContent = 'Score: ' + correct + ' / ' + answered;
      }

      function gradeItem(it){
        var verdict = it.querySelector('.qbank-verdict');
        if (!verdict) return;
        var picked = it.querySelector('input[type="radio"]:checked');
        if (!picked) {
          grades.set(it, 'unanswered');
          verdict.className = 'qbank-verdict qbank-verdict-warn';
          verdict.textContent = "You didn't select an answer — pick one before checking, next time.";
        } else {
          var chosen = parseInt(picked.value, 10);
          var correctIdx = parseInt(it.getAttribute('data-answer'), 10);
          var isCorrect = chosen === correctIdx;
          grades.set(it, isCorrect);
          verdict.className = 'qbank-verdict ' + (isCorrect ? 'qbank-verdict-ok' : 'qbank-verdict-bad');
          verdict.textContent = isCorrect
            ? 'Correct ✓'
            : ('Incorrect ✗ — you selected ' + letters[chosen] + '.');
        }
        updateScore();
      }

      function resetAllGrades(){
        grades = new Map();
        items.forEach(function(it){
          var verdict = it.querySelector('.qbank-verdict');
          if (verdict) { verdict.className = 'qbank-verdict'; verdict.textContent = ''; }
          it.querySelectorAll('input[type="radio"]').forEach(function(r){ r.checked = false; });
          var ans = it.querySelector('.qbank-ans');
          if (ans) ans.setAttribute('hidden', '');
          var revealBtn = it.querySelector('.qbank-reveal');
          if (revealBtn) revealBtn.textContent = 'Show answer';
        });
        updateScore();
      }

      function matches(it){
        var okArea = state.area === 'all' || it.getAttribute('data-area') === state.area;
        var okDiff = state.diff === 'all' || it.getAttribute('data-diff') === state.diff;
        var okSearch = !state.q || it.textContent.toLowerCase().indexOf(state.q) !== -1;
        return okArea && okDiff && okSearch;
      }

      function apply(){
        var shown = 0;
        items.forEach(function(it){
          var visible;
          if (state.mode === 'random') {
            visible = randomPool.indexOf(it) !== -1 && matches(it);
          } else {
            visible = matches(it);
          }
          it.style.display = visible ? '' : 'none';
          if (visible) shown++;
        });
        countEl.textContent = 'Showing ' + shown + ' of ' + items.length;
      }

      function wireChips(selector){
        var chips = Array.prototype.slice.call(root.querySelectorAll(selector + ' .qbank-chip'));
        chips.forEach(function(btn){
          btn.addEventListener('click', function(){
            chips.forEach(function(b){ b.classList.remove('active'); });
            btn.classList.add('active');
            var group = root.querySelector(selector).getAttribute('data-filter');
            state[group] = btn.getAttribute('data-value');
            state.mode = 'filter';
            apply();
          });
        });
      }
      wireChips('[data-filter="area"]');
      wireChips('[data-filter="diff"]');

      var searchInput = root.querySelector('.qbank-search');
      if (searchInput) {
        searchInput.addEventListener('input', function(){
          state.q = searchInput.value.trim().toLowerCase();
          state.mode = 'filter';
          apply();
        });
      }

      var buttons = root.querySelectorAll('.qbank-actions .qbank-btn');
      if (buttons[0]) buttons[0].addEventListener('click', function(){
        var pool = items.filter(matches);
        for (var i = pool.length - 1; i > 0; i--) {
          var j = Math.floor(Math.random() * (i + 1));
          var tmp = pool[i]; pool[i] = pool[j]; pool[j] = tmp;
        }
        randomPool = pool.slice(0, 15);
        state.mode = 'random';
        resetAllGrades();
        apply();
      });
      if (buttons[1]) buttons[1].addEventListener('click', function(){
        state.mode = 'filter';
        apply();
      });

      root.querySelectorAll('.qbank-reveal').forEach(function(btn){
        btn.addEventListener('click', function(){
          var ans = btn.nextElementSibling;
          var isHidden = ans.hasAttribute('hidden');
          if (isHidden) {
            ans.removeAttribute('hidden');
            btn.textContent = 'Hide answer';
            gradeItem(btn.closest('.qbank-item'));
          } else {
            ans.setAttribute('hidden', '');
            btn.textContent = 'Show answer';
          }
        });
      });

      updateScore();
      apply();
    })();
    </script>
   </div>
@@QNOTE_JS@@
  </main>
</div>

<footer class="site-footer">HK Tax Study Hub — study aid, not professional advice. Not affiliated with or endorsed by ACCA. Verify against the Inland Revenue Ordinance (Cap. 112) and current IRD guidance before relying on any figure.</footer>

<script src="../assets/js/theme.js"></script>
</body>
</html>
""" % (NAV, total, coverage_rows, total, n_topics, n_computational, total,
       "\n".join(area_chips), total, total, items_html)
    html = (html.replace("@@QNOTE_CSS@@", qnote_widget.CSS)
                .replace("@@QNOTE_BTN@@", qnote_widget.BUTTON % "A")
                .replace("@@QNOTE_JS@@", qnote_widget.JS))

    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote %s (%d bytes, %d questions)" % (OUT, os.path.getsize(OUT), total))


if __name__ == "__main__":
    main()
