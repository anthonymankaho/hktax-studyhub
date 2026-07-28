/* Freshness check: compares this page's "content reviewed" date against the
   modified dates of the local /Data source files it relies on.
   Each page must set window.PAGE_META = { reviewed: 'YYYY-MM-DD', sources: ['CAP112', ...] }
   BEFORE this script runs. Categories are the top two folders under /Data,
   e.g. 'DIPN/Profits-Tax', 'CAP112', 'PwC', 'IRD-Administration'. */
(function () {
  function fmt(d) {
    if (!d) return "unknown";
    var dt = new Date(d);
    if (isNaN(dt)) return String(d);
    return dt.toISOString().slice(0, 10);
  }

  function render() {
    var el = document.getElementById("freshness-banner");
    if (!el) return;
    var meta = window.PAGE_META || {};
    var manifest = window.DATA_MANIFEST || { generatedAt: null, files: [] };
    var sources = meta.sources || [];
    var reviewed = meta.reviewed ? new Date(meta.reviewed) : null;

    var matched = manifest.files.filter(function (f) {
      return sources.indexOf(f.category) !== -1;
    });

    var state, headline, detail;

    if (!manifest.generatedAt) {
      state = "warn";
      headline = "Data folder manifest has not been generated yet.";
      detail = "Run <code>scripts\\Refresh-Data-Manifest.bat</code> once you've populated the /Data folder, then reload this page.";
    } else if (sources.length && matched.length === 0) {
      state = "warn";
      headline = "No source files found yet for: " + sources.join(", ") + ".";
      detail = "Drop the relevant CAP112 / DIPN / PwC files into <code>Data\\" + sources.join("</code> or <code>Data\\") + "</code>, then run the refresh script.";
    } else {
      var newest = matched.reduce(function (max, f) {
        var m = new Date(f.modified);
        return m > max ? m : max;
      }, new Date(0));

      if (reviewed && newest > reviewed) {
        state = "bad";
        headline = "Source material is newer than this page's last review.";
        detail = "Newest matched source: " + fmt(newest) + " &mdash; page last reviewed " + fmt(meta.reviewed) + ". Ask Claude to re-check this page against the updated source.";
      } else {
        state = "ok";
        headline = "Content matches current /Data sources.";
        detail = matched.length
          ? "Checked against " + matched.length + " source file(s), newest dated " + fmt(newest) + "."
          : "No linked source files declared for this page.";
      }
    }

    el.className = "freshness " + state;
    el.innerHTML =
      '<span class="dot"></span>' +
      '<span class="msg"><strong>' + headline + "</strong> " + detail + "</span>" +
      '<button type="button" id="freshness-toggle">Show source files</button>';

    var list = document.getElementById("freshness-sources");
    if (list) {
      list.innerHTML = matched.length
        ? matched.map(function (f) {
            return '<li><span class="file">' + f.category + " / " + f.name + '</span><span class="date">' + fmt(f.modified) + "</span></li>";
          }).join("")
        : "<li><span class=\"file\">No files matched yet.</span></li>";
    }

    var btn = document.getElementById("freshness-toggle");
    if (btn && list) {
      btn.addEventListener("click", function () {
        var open = list.style.display === "block";
        list.style.display = open ? "none" : "block";
        btn.textContent = open ? "Show source files" : "Hide source files";
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", render);
  } else {
    render();
  }
})();
