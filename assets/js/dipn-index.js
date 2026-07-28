/* DIPN Index: search/filter over window.DIPN_INDEX. */
(function () {
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function render() {
    var data = window.DIPN_INDEX || [];
    var q = (document.getElementById("q").value || "").trim().toLowerCase();
    var groupFilter = document.getElementById("filter-group").value;
    var statusFilter = document.getElementById("filter-status").value;

    var filtered = data.filter(function (row) {
      if (groupFilter && row.group !== groupFilter) return false;
      if (statusFilter && row.status !== statusFilter) return false;
      if (!q) return true;
      var haystack = (row.no + " " + row.title + " " + row.summary + " " + row.group).toLowerCase();
      return haystack.indexOf(q) !== -1;
    });

    var tbody = document.getElementById("results-body");
    document.getElementById("checker-count").textContent = filtered.length + " of " + data.length + " documents shown";

    if (!filtered.length) {
      tbody.innerHTML = "";
      document.getElementById("checker-empty").style.display = "block";
      return;
    }
    document.getElementById("checker-empty").style.display = "none";

    tbody.innerHTML = filtered.map(function (row) {
      var statusBadge = row.status === "core"
        ? '<a href="' + row.link + '" class="tag tag-deductible">Core →</a>'
        : '<span class="tag tag-nontaxable">Reference only</span>';
      return (
        "<tr>" +
        "<td>" + escapeHtml(row.no) + "</td>" +
        "<td>" + escapeHtml(row.title) + (row.example ? ' <span class="tag tag-taxable" style="margin-left:4px">example</span>' : "") + "</td>" +
        "<td>" + escapeHtml(row.group) + "</td>" +
        "<td>" + escapeHtml(row.date || "") + "</td>" +
        '<td class="note">' + escapeHtml(row.summary) + "</td>" +
        "<td>" + statusBadge + "</td>" +
        "</tr>"
      );
    }).join("");
  }

  function populateGroupFilter() {
    var select = document.getElementById("filter-group");
    var groups = Array.from(new Set((window.DIPN_INDEX || []).map(function (r) { return r.group; })));
    groups.forEach(function (g) {
      var opt = document.createElement("option");
      opt.value = g;
      opt.textContent = g;
      select.appendChild(opt);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    populateGroupFilter();
    document.getElementById("q").addEventListener("input", render);
    document.getElementById("filter-group").addEventListener("change", render);
    document.getElementById("filter-status").addEventListener("change", render);
    render();
  });
})();
