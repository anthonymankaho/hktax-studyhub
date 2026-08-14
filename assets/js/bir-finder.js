/* BIR Box Finder: search/filter over window.BIR_BOXES. */
(function () {
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function render() {
    var data = window.BIR_BOXES || [];
    var q = (document.getElementById("q").value || "").trim().toLowerCase();
    var formFilter = document.getElementById("filter-form").value;

    var filtered = data.filter(function (row) {
      if (formFilter && row.form !== formFilter) return false;
      if (!q) return true;
      var haystack = (row.form + " " + row.part + " " + row.box + " " + row.label + " " + (row.note || "")).toLowerCase();
      return haystack.indexOf(q) !== -1;
    });

    var tbody = document.getElementById("results-body");
    document.getElementById("checker-count").textContent = filtered.length + " of " + data.length + " boxes shown";

    if (!filtered.length) {
      tbody.innerHTML = "";
      document.getElementById("checker-empty").style.display = "block";
      return;
    }
    document.getElementById("checker-empty").style.display = "none";

    tbody.innerHTML = filtered.map(function (row) {
      var formBadge = '<span class="tag tag-dutiable">' + escapeHtml(row.form) + "</span>";
      var linkCell = row.link
        ? '<a href="' + row.link + '">View section &rarr;</a>'
        : "";
      return (
        "<tr>" +
        "<td>" + formBadge + "</td>" +
        "<td>" + escapeHtml(row.box) + "</td>" +
        "<td>" + escapeHtml(row.part) + "</td>" +
        '<td class="item">' + escapeHtml(row.label) + "</td>" +
        '<td class="note">' + escapeHtml(row.note || "") + "</td>" +
        '<td class="goto">' + linkCell + "</td>" +
        "</tr>"
      );
    }).join("");
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("q").addEventListener("input", render);
    document.getElementById("filter-form").addEventListener("change", render);
    render();
  });
})();
