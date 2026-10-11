#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render pages/question-bank-b.html from assets/qbank-b.json.

Section B is 3 fixed case scenarios (5 linked questions each) rather than
Section A's filterable single-fact bank, so there is no filter toolbar, no
Random 15 and no search - just the cases in order, a Score tracker, and a
Reset button to clear a case and try it again. The grading logic (select an
option, "Show answer" grades it, re-showing re-grades rather than double-
counting) is identical to Section A's, and lives inside <main class="content">
scoped to a .qbank-app wrapper by class for the same reason: build-
combined.py's per-panel id-namespacing can't see into a <script>, and content
outside <main> is dropped from the combined build entirely.

Run from the project root, after scripts/build-qbank-b.py:
    python scripts/build-question-bank-b-page.py
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qnote_widget  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QBANK = os.path.join(ROOT, "assets", "qbank-b.json")
OUT = os.path.join(ROOT, "pages", "question-bank-b.html")


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


NAV = """    <nav class="site-nav">
      <a href="../index.html">Hub</a>
      <a href="ird-updates.html">IRD What's New</a>
      <a href="acca-tx-hkg.html">ACCA TX-HKG</a>
      <a href="question-bank.html">Question Bank A</a>
      <a href="question-bank-b.html" class="active">Question Bank B</a>
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

SECTION_SWITCH = """      <div class="qbank-section-switch">
        <a href="question-bank.html">Section A</a>
        <a href="question-bank-b.html" class="active">Section B</a>
        <a href="question-bank-c.html">Section C</a>
      </div>"""


def render_item(item, case_id):
    letters = "ABCD"
    opts = "\n".join(
        '        <li><label><input type="radio" name="opt-%s" value="%d"> %s</label></li>'
        % (item["id"], i, esc(o))
        for i, o in enumerate(item["options"])
    )
    ref = ('<span class="qbank-ref">%s</span>' % esc(item["ref"])) if item.get("ref") else ""
    return (
        '        <div class="qbank-item" data-case="%s" data-answer="%d">\n'
        '          <div class="qbank-meta"><span class="qbank-topic">%s</span></div>\n'
        '          <p class="qbank-q"><strong>%s.</strong> %s</p>\n'
        '          <ol type="A" class="qbank-opts">\n%s\n          </ol>\n'
        '          <button type="button" class="qbank-reveal">Show answer</button>\n'
        '          <div class="qbank-ans" hidden>\n'
        '            <p class="qbank-verdict"></p>\n'
        '            <p class="qbank-answer-line"><strong>Correct: %s &mdash; %s.</strong></p>\n'
        '            <p>%s</p>\n'
        '            %s\n'
        '          </div>\n'
        '        </div>\n'
        % (case_id, item["answer"],
           esc(item["topic"]),
           item["id"], item["q"],
           opts,
           letters[item["answer"]], esc(item["options"][item["answer"]]),
           item["explain"],
           ref)
    )


def render_case(case, n):
    items_html = "\n".join(render_item(it, case["id"]) for it in case["questions"])
    return (
        '      <div class="qbank-case" id="%s">\n'
        '        <h3>Case %d — %s <span class="qbank-marks">(%d marks)</span></h3>\n'
        '        <div class="qbank-scenario">%s</div>\n'
        '%s'
        '      </div>\n'
        % (case["id"], n, esc(case["label"]), len(case["questions"]) * 2,
           case["scenario"], items_html)
    )


def main():
    with io.open(QBANK, encoding="utf-8") as f:
        data = json.load(f)
    cases = data["cases"]
    total = sum(len(c["questions"]) for c in cases)
    sittings = len(cases) // 3

    cases_html = "\n".join(render_case(c, i + 1) for i, c in enumerate(cases))

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="A study aid for Hong Kong tax - profits, property and salaries tax, stamp duty, depreciation allowances and personal assessment - built from IRD guidance and the Inland Revenue Ordinance. Not professional advice.">
<title>Question Bank — Section B — HK Tax Study Hub</title>
<link rel="stylesheet" href="../assets/css/main.css">
<style>
  .qbank-section-switch{display:flex;gap:8px;margin:10px 0 4px}
  .qbank-section-switch a{border:1px solid var(--border);background:var(--surface-alt);color:var(--text);border-radius:20px;padding:5px 14px;font-size:12.5px;text-decoration:none}
  .qbank-section-switch a.active{background:var(--brand);color:#fff;border-color:var(--brand)}
  .qbank-toolbar{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:12px 16px;margin:14px 0;display:flex;align-items:center;gap:10px;flex-wrap:wrap;box-shadow:var(--shadow)}
  .qbank-btn{border:1px solid var(--brand);background:var(--brand);color:#fff;border-radius:8px;padding:7px 14px;font-size:13px;cursor:pointer;font-family:inherit}
  .qbank-score{font-size:12.5px;font-weight:700;color:var(--brand);background:var(--surface-alt);border:1px solid var(--border);border-radius:20px;padding:4px 12px;margin-left:auto}
  .qbank-case{margin:26px 0}
  .qbank-case h3{font-size:16px;margin:0 0 8px;padding-bottom:6px;border-bottom:2px solid var(--border)}
  .qbank-marks{font-size:12px;font-weight:500;color:var(--text-muted)}
  .qbank-scenario{background:var(--surface-alt);border:1px solid var(--border);border-left:4px solid var(--brand);border-radius:var(--radius);padding:14px 16px;margin:0 0 14px;font-size:14px}
  .qbank-item{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:14px 16px;margin:12px 0;box-shadow:var(--shadow)}
  .qbank-meta{font-size:11px;text-transform:uppercase;letter-spacing:.03em;margin-bottom:6px;color:var(--brand);font-weight:700}
  .qbank-q{margin:6px 0 8px;font-size:14.5px}
  .qbank-opts{margin:0 0 10px 22px;padding:0;font-size:14px}
  .qbank-opts li{margin:3px 0}
  .qbank-opts label{display:flex;align-items:flex-start;gap:8px;cursor:pointer;padding:2px 4px;border-radius:4px}
  .qbank-opts label:hover{background:var(--surface-alt)}
  .qbank-opts input[type="radio"]{margin-top:3px;flex-shrink:0}
  .qbank-reveal{border:1px solid var(--border);background:var(--surface-alt);color:var(--text);border-radius:6px;padding:5px 12px;font-size:12.5px;cursor:pointer;font-family:inherit}
  .qbank-ans{margin-top:10px;padding-top:9px;border-top:1px dotted var(--border);font-size:13.5px}
  .qbank-answer-line strong{color:var(--ok-text)}
  .qbank-ref{display:inline-block;margin-top:4px;font-size:11.5px;color:var(--text-muted);border:1px solid var(--border);border-radius:4px;padding:1px 7px}
  .qbank-verdict{font-weight:700;padding:6px 10px;border-radius:6px;margin:0 0 8px;font-size:13.5px}
  .qbank-verdict:empty{display:none;margin:0;padding:0}
  .qbank-verdict-ok{background:var(--ok-bg);color:var(--ok-text);border:1px solid var(--ok-border)}
  .qbank-verdict-bad{background:var(--bad-bg);color:var(--bad-text);border:1px solid var(--bad-border)}
  .qbank-verdict-warn{background:var(--warn-bg);color:var(--warn-text);border:1px solid var(--warn-border)}
@@QNOTE_CSS@@</style>
</head>
<body>
<header class="site-header">
  <div class="bar">
    <div class="brand">HK Tax Study Hub<small>Study aid — not professional advice</small></div>
%s
    <button id="ai-prompt-btn" class="ai-prompt-btn" title="Copy a hardened HK-tax prompt to paste into your browser AI" style="background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.3);color:#fff;border-radius:6px;padding:6px 10px;cursor:pointer;font-size:12px;margin-right:8px">AI Prompts</button>
    <button id="theme-toggle" title="Toggle light/dark" style="background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.3);color:#fff;border-radius:6px;padding:6px 10px;cursor:pointer;font-size:12px">Theme</button>
  </div>
</header>

<div class="shell">
  <aside class="toc">
    <h4>On this page</h4>
    <a href="#overview">What this is</a>
    <a href="#case1">Case 1 — Ms Fiona Ng</a>
    <a href="#case2">Case 2 — Golden Horizon Ltd</a>
    <a href="#case3">Case 3 — Harbour Partners</a>
    <a href="#copyright">Originality</a>
  </aside>

  <main class="content">
   <div class="qbank-app">
    <div class="page-title">
      <div>
        <span class="badge badge-common">ACCA TX-HKG</span>
        <h1>Question Bank — Section B</h1>
        <p class="subtitle">ACCA TX-HKG &mdash; Section B, OT Case Questions &middot; %d original questions across %d integrated scenarios, matching the exam's own case-question format: one set of facts, five linked questions, spanning more than one syllabus area at once. A real Section B is 3 cases / 15 questions / 30 marks, so this is %d full sittings' worth.</p>
      </div>
    </div>
%s

    <section class="block" id="overview">
      <h2>What this is</h2>
      <p class="lede">Section B mirrors the exam's real OT case format: unlike Section A's single-fact questions, each case gives one connected scenario and asks five questions against it — so an early answer (a rental value, a share of profit) often feeds directly into a later one, exactly as it would in a real case.</p>
      <div class="callout tip">
        <span class="lbl">Same computation engine as Section A</span>
        Every figure in every case was generated from and checked against <code>scripts/qbank_tax.py</code>, and each case's five questions were verified for internal consistency — an answer used in question 3 is the same figure question 1 or 2 established, not a fresh unrelated number.
      </div>
    </section>

    <div class="qbank-toolbar">
      <button type="button" class="qbank-btn qbank-reset-btn">Reset all three cases</button>
      @@QNOTE_BTN@@
      <span class="qbank-score" title="Correct answers out of questions you've checked so far">Score: 0 / %d</span>
    </div>

%s

    <section class="block" id="copyright">
      <h2>Originality</h2>
      <p>Every case and question on this page is original, written for this Hub in the exam's own case-question format. See the <a href="acca-tx-hkg.html#copyright">ACCA TX-HKG page</a> for the fuller statement of what is and is not reproduced anywhere on this Hub.</p>
    </section>

    <div class="section-nav">
      <a href="question-bank.html">&larr; Question Bank A</a>
      <a href="question-bank-c.html">Question Bank C &rarr;</a>
    </div>

    <script>
    (function(){
      var root = document.currentScript.closest('.qbank-app');
      if (!root) return;
      var items = Array.prototype.slice.call(root.querySelectorAll('.qbank-item'));
      var scoreEl = root.querySelector('.qbank-score');
      var letters = ['A', 'B', 'C', 'D'];
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
          verdict.textContent = "You didn't select an answer \\u2014 pick one before checking, next time.";
        } else {
          var chosen = parseInt(picked.value, 10);
          var correctIdx = parseInt(it.getAttribute('data-answer'), 10);
          var isCorrect = chosen === correctIdx;
          grades.set(it, isCorrect);
          verdict.className = 'qbank-verdict ' + (isCorrect ? 'qbank-verdict-ok' : 'qbank-verdict-bad');
          verdict.textContent = isCorrect
            ? 'Correct \\u2713'
            : ('Incorrect \\u2717 \\u2014 you selected ' + letters[chosen] + '.');
        }
        updateScore();
      }

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

      var resetBtn = root.querySelector('.qbank-reset-btn');
      if (resetBtn) resetBtn.addEventListener('click', function(){
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
      });

      updateScore();
    })();
    </script>
   </div>
@@QNOTE_JS@@
  </main>
</div>

<footer class="site-footer">HK Tax Study Hub — study aid, not professional advice. Not affiliated with or endorsed by ACCA. Verify against the Inland Revenue Ordinance (Cap. 112) and current IRD guidance before relying on any figure.</footer>

<script src="../assets/js/theme.js"></script>
<script src="../assets/js/ai-prompt.js"></script>
</body>
</html>
""" % (NAV, total, len(cases), sittings, SECTION_SWITCH, total, cases_html)
    html = (html.replace("@@QNOTE_CSS@@", qnote_widget.CSS)
                .replace("@@QNOTE_BTN@@", qnote_widget.BUTTON % "B")
                .replace("@@QNOTE_JS@@", qnote_widget.JS))

    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote %s (%d bytes, %d cases, %d questions)"
          % (OUT, os.path.getsize(OUT), len(cases), total))


if __name__ == "__main__":
    main()
