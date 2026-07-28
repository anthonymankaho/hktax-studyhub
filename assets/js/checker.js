/* Transaction Checker: client-side search/filter over window.TRANSACTIONS. */
(function () {
  var STATUS_LABEL = {
    taxable: "Taxable",
    nontaxable: "Non-taxable",
    deductible: "Deductible",
    nondeductible: "Non-deductible",
    dutiable: "Dutiable",
    dutyfree: "Duty-free (0%)",
    allowance: "Allowance available"
  };

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function render() {
    var data = window.TRANSACTIONS || [];
    var q = (document.getElementById("q").value || "").trim().toLowerCase();
    var taxFilter = document.getElementById("filter-tax").value;
    var statusFilter = document.getElementById("filter-status").value;

    var filtered = data.filter(function (row) {
      if (taxFilter && row.tax !== taxFilter) return false;
      if (statusFilter && row.status !== statusFilter) return false;
      if (!q) return true;
      var haystack = (row.item + " " + row.note + " " + row.tax + " " + row.section).toLowerCase();
      return haystack.indexOf(q) !== -1;
    });

    var tbody = document.getElementById("results-body");
    var countEl = document.getElementById("checker-count");
    countEl.textContent = filtered.length + " of " + data.length + " transactions shown";

    if (!filtered.length) {
      tbody.innerHTML = "";
      document.getElementById("checker-empty").style.display = "block";
      return;
    }
    document.getElementById("checker-empty").style.display = "none";

    tbody.innerHTML = filtered.map(function (row) {
      var label = STATUS_LABEL[row.status] || row.status;
      return (
        "<tr>" +
        '<td><span class="tag tag-' + row.status + '">' + escapeHtml(label) + "</span></td>" +
        "<td>" + escapeHtml(row.tax) + "</td>" +
        '<td class="item">' + escapeHtml(row.item) + "</td>" +
        "<td>" + escapeHtml(row.section) + "</td>" +
        '<td class="note">' + escapeHtml(row.note || "") + "</td>" +
        '<td class="goto"><a href="' + row.page + '">View section &rarr;</a></td>' +
        "</tr>"
      );
    }).join("");
  }

  function populateTaxFilter() {
    var select = document.getElementById("filter-tax");
    var taxes = Array.from(new Set((window.TRANSACTIONS || []).map(function (r) { return r.tax; })));
    taxes.forEach(function (t) {
      var opt = document.createElement("option");
      opt.value = t;
      opt.textContent = t;
      select.appendChild(opt);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    populateTaxFilter();
    document.getElementById("q").addEventListener("input", render);
    document.getElementById("filter-tax").addEventListener("change", render);
    document.getElementById("filter-status").addEventListener("change", render);
    render();
  });
})();
