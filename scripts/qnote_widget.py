# -*- coding: utf-8 -*-
"""Shared "Note" scratchpad (Excel-style, 100 x 100) for the Section A and B
question-bank pages. Imported by build-question-bank-page.py and
build-question-bank-b-page.py, which splice these strings into their output
AFTER their own %-formatting (so literal % in the JS is safe here).

Like the pages' own scripts, it is class-scoped only (no ids) and the <script>
sits inside <main>, so build-combined.py carries it into the combined app.
Formulas: = followed by numbers, cell refs (A1..CV100), + - * / and brackets.
Evaluated by a small hand-written parser - never eval().
"""

BUTTON = ('<button type="button" class="qbank-btn secondary qnote-btn" data-qnote="%s" '
          'title="Open a scratchpad: 100 &times; 100 cells, formulas with = + - * / &middot; '
          '開啟草稿表格">Note</button>')

CSS = r'''
  .qnote-panel{position:fixed;right:16px;bottom:16px;z-index:1000;width:min(580px,calc(100vw - 32px));background:var(--surface);border:1px solid var(--border);border-top:3px solid var(--brand);border-radius:10px;box-shadow:0 8px 30px rgba(0,0,0,.28);display:none;font-size:13px}
  .qnote-panel.open{display:block}
  .qnote-head{display:flex;align-items:center;gap:8px;padding:6px 10px;cursor:move;background:var(--surface-alt);border-radius:7px 7px 0 0;user-select:none;touch-action:none}
  .qnote-head strong{flex:1;font-size:13px}
  .qnote-head button{cursor:pointer;font:inherit;font-size:12px;padding:2px 9px;border-radius:5px;border:1px solid var(--border);background:var(--surface);color:var(--brand)}
  .qnote-hint{margin:0;padding:4px 10px;font-size:11.5px;color:var(--text-muted)}
  .qnote-scroll{height:250px;overflow:auto;border-top:1px solid var(--border);background:var(--surface)}
  .qnote-panel.min .qnote-scroll,.qnote-panel.min .qnote-hint{display:none}
  .qnote-panel table{border-collapse:separate;border-spacing:0;table-layout:fixed;width:max-content}
  .qnote-panel th{position:sticky;top:0;z-index:2;background:var(--surface-alt);color:var(--text-muted);font-size:11px;font-weight:600;height:24px;width:90px;border-right:1px solid var(--border);border-bottom:1px solid var(--border);padding:0}
  .qnote-panel th.qnote-rn{left:0;z-index:3;width:36px}
  .qnote-panel td.qnote-rn{position:sticky;left:0;z-index:1;width:36px;background:var(--surface-alt);color:var(--text-muted);font-size:11px;text-align:center;border-right:1px solid var(--border);border-bottom:1px solid var(--border)}
  .qnote-panel td{padding:0;height:25px;border-right:1px solid var(--border);border-bottom:1px solid var(--border)}
  .qnote-panel td input{display:block;box-sizing:border-box;width:90px;height:24px;border:0;background:transparent;color:var(--text);font:inherit;padding:0 5px;margin:0;outline:none}
  .qnote-panel td input.qnote-num{text-align:right}
  .qnote-panel td input.qnote-err{color:#c0392b}
  .qnote-panel td input:focus{box-shadow:inset 0 0 0 2px var(--brand);background:var(--surface)}
'''

JS = r'''
    <script>
    /* Note: Excel-style scratchpad (100 x 100). Formulas: = numbers, cells, + - * / ( ) */
    (function () {
      var ROWS = 100, COLS = 100;
      function colName(i) { return (i >= 26 ? String.fromCharCode(64 + Math.floor(i / 26)) : '') + String.fromCharCode(65 + i % 26); }
      function colIndex(s) { var n = 0; for (var i = 0; i < s.length; i++) n = n * 26 + (s.charCodeAt(i) - 64); return n - 1; }

      Array.prototype.forEach.call(document.querySelectorAll('.qnote-btn'), function (btn) {
        var key = 'hktax-qnote-' + (btn.getAttribute('data-qnote') || 'x'), panel = null, grid = [], data = {};
        try { data = JSON.parse(localStorage.getItem(key) || '{}'); } catch (e) {}
        function save() { try { localStorage.setItem(key, JSON.stringify(data)); } catch (e) {} }

        function cellValue(r, c, stack) {
          var k = r + ',' + c, raw = data[k];
          if (raw === undefined || raw === '') return 0;
          if (raw.charAt(0) !== '=') {
            var n = Number(String(raw).replace(/,/g, '').trim());
            if (isNaN(n)) throw '#VALUE!';
            return n;
          }
          if (stack.indexOf(k) >= 0) throw '#CIRC!';
          return evalFormula(raw.slice(1), stack.concat(k));
        }
        function evalFormula(src, stack) {
          var toks = [], re = /\s*(\d+\.?\d*|\.\d+|[A-Za-z]{1,2}\d{1,3}|[-+*\/()])/y, m, pos = 0;
          src = src.replace(/\s+$/, '');
          while (pos < src.length) {
            re.lastIndex = pos; m = re.exec(src);
            if (!m) throw '#ERR';
            toks.push(m[1]); pos = re.lastIndex;
          }
          var i = 0;
          function expr() {
            var v = term();
            while (toks[i] === '+' || toks[i] === '-') { var op = toks[i++], t = term(); v = op === '+' ? v + t : v - t; }
            return v;
          }
          function term() {
            var v = factor();
            while (toks[i] === '*' || toks[i] === '/') {
              var op = toks[i++], f = factor();
              if (op === '/') { if (f === 0) throw '#DIV/0!'; v = v / f; } else v = v * f;
            }
            return v;
          }
          function factor() {
            var t = toks[i++];
            if (t === undefined) throw '#ERR';
            if (t === '-') return -factor();
            if (t === '+') return factor();
            if (t === '(') { var v = expr(); if (toks[i++] !== ')') throw '#ERR'; return v; }
            if (/^[0-9.]/.test(t)) return parseFloat(t);
            var mm = /^([A-Za-z]+)(\d+)$/.exec(t);
            if (!mm) throw '#ERR';
            var cc = colIndex(mm[1].toUpperCase()), rr = parseInt(mm[2], 10) - 1;
            if (cc < 0 || cc >= COLS || rr < 0 || rr >= ROWS) throw '#REF!';
            return cellValue(rr, cc, stack);
          }
          var out = expr();
          if (i < toks.length) throw '#ERR';
          return out;
        }
        function fmt(n) { return String(Math.round(n * 1e8) / 1e8); }

        function show(r, c) {
          var inp = grid[r] && grid[r][c]; if (!inp || document.activeElement === inp) return;
          var raw = data[r + ',' + c] || '', num = false, err = false;
          if (raw.charAt(0) === '=') {
            try { raw = fmt(cellValue(r, c, [])); num = true; } catch (e) { raw = String(e).indexOf('#') === 0 ? e : '#ERR'; err = true; }
          } else if (raw !== '' && !isNaN(Number(raw.replace(/,/g, '')))) num = true;
          inp.value = raw;
          inp.className = (num ? 'qnote-num ' : '') + (err ? 'qnote-err' : '');
        }
        function refresh() {
          Object.keys(data).forEach(function (k) {
            if (data[k].charAt(0) === '=') { var p = k.split(','); show(+p[0], +p[1]); }
          });
        }
        function setCell(r, c, v) {
          var k = r + ',' + c;
          if (v) data[k] = v; else delete data[k];
        }

        function build() {
          panel = document.createElement('div'); panel.className = 'qnote-panel';
          var h = '<div class="qnote-head"><strong>Note &middot; 草稿 (100 &times; 100)</strong>' +
            '<button type="button" class="qnote-min" title="Collapse / expand">&minus;</button>' +
            '<button type="button" class="qnote-clear">Clear</button>' +
            '<button type="button" class="qnote-close" aria-label="Close">&times;</button></div>' +
            '<p class="qnote-hint">Type numbers or formulas like =A1+B1*2 (only + - * / and brackets). Arrow keys / Enter / Tab move; Excel paste works. Saved in this browser. &middot; 支援 = + - * / 公式，自動儲存。</p>' +
            '<div class="qnote-scroll"><table><thead><tr><th class="qnote-rn"></th>';
          for (var c = 0; c < COLS; c++) h += '<th>' + colName(c) + '</th>';
          h += '</tr></thead><tbody>';
          for (var r = 0; r < ROWS; r++) {
            h += '<tr><td class="qnote-rn">' + (r + 1) + '</td>';
            for (c = 0; c < COLS; c++) h += '<td><input type="text" autocomplete="off" spellcheck="false" data-r="' + r + '" data-c="' + c + '"></td>';
            h += '</tr>';
          }
          panel.innerHTML = h + '</tbody></table></div>';
          document.body.appendChild(panel);

          var ins = panel.querySelectorAll('input');
          Array.prototype.forEach.call(ins, function (inp) {
            var r = +inp.getAttribute('data-r'), c = +inp.getAttribute('data-c');
            (grid[r] = grid[r] || [])[c] = inp;
          });
          Array.prototype.forEach.call(ins, function (inp) {
            var r = +inp.getAttribute('data-r'), c = +inp.getAttribute('data-c'), k = r + ',' + c;
            inp.addEventListener('focus', function () { inp.className = ''; inp.value = data[k] || ''; inp.select(); });
            inp.addEventListener('input', function () { setCell(r, c, inp.value); save(); refresh(); });
            inp.addEventListener('blur', function () { show(r, c); });
            inp.addEventListener('keydown', function (e) {
              var t = null;
              if (e.key === 'ArrowDown' || e.key === 'Enter') t = grid[Math.min(r + 1, ROWS - 1)][c];
              else if (e.key === 'ArrowUp') t = grid[Math.max(r - 1, 0)][c];
              else if (e.key === 'ArrowLeft' && inp.selectionStart === 0 && inp.selectionEnd === 0) t = grid[r][Math.max(c - 1, 0)];
              else if (e.key === 'ArrowRight' && inp.selectionStart === inp.value.length) t = grid[r][Math.min(c + 1, COLS - 1)];
              if (t) { e.preventDefault(); t.focus(); }
            });
            inp.addEventListener('paste', function (e) {
              var txt = (e.clipboardData || window.clipboardData).getData('text');
              if (txt.indexOf('\n') < 0 && txt.indexOf('\t') < 0) return;
              e.preventDefault();
              txt.replace(/\r/g, '').replace(/\n$/, '').split('\n').forEach(function (line, i) {
                line.split('\t').forEach(function (v, j) { if (grid[r + i] && grid[r + i][c + j]) setCell(r + i, c + j, v); });
              });
              save(); inp.blur();
              Object.keys(data).forEach(function (kk) { var p = kk.split(','); show(+p[0], +p[1]); });
            });
          });
          Object.keys(data).forEach(function (kk) { var p = kk.split(','); show(+p[0], +p[1]); });

          panel.querySelector('.qnote-close').addEventListener('click', function () { panel.classList.remove('open'); });
          panel.querySelector('.qnote-min').addEventListener('click', function () { panel.classList.toggle('min'); });
          panel.querySelector('.qnote-clear').addEventListener('click', function () {
            if (!Object.keys(data).length || !confirm('Clear the whole Note sheet? 清除全部草稿？')) return;
            data = {}; save();
            Array.prototype.forEach.call(ins, function (i) { i.value = ''; i.className = ''; });
          });

          var head = panel.querySelector('.qnote-head'), drag = null;
          head.addEventListener('pointerdown', function (e) {
            if (e.target.tagName === 'BUTTON') return;
            var b = panel.getBoundingClientRect();
            drag = { dx: e.clientX - b.left, dy: e.clientY - b.top };
            head.setPointerCapture(e.pointerId);
          });
          head.addEventListener('pointermove', function (e) {
            if (!drag) return;
            panel.style.right = 'auto'; panel.style.bottom = 'auto';
            panel.style.left = Math.max(0, Math.min(window.innerWidth - 80, e.clientX - drag.dx)) + 'px';
            panel.style.top = Math.max(0, Math.min(window.innerHeight - 40, e.clientY - drag.dy)) + 'px';
          });
          head.addEventListener('pointerup', function () { drag = null; });
        }

        btn.addEventListener('click', function () {
          if (!panel) build();
          panel.classList.toggle('open');
          if (panel.classList.contains('open')) { panel.classList.remove('min'); grid[0][0].focus(); }
        });
      });
    })();
    </script>
'''
