/* Manual light/dark override, persisted in localStorage. Defaults to OS preference. */
(function () {
  var KEY = "hktax-theme";
  function apply(mode) {
    if (mode === "light" || mode === "dark") {
      document.documentElement.setAttribute("data-theme", mode);
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
  }
  var saved = localStorage.getItem(KEY);
  apply(saved);

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var current = localStorage.getItem(KEY);
      var next = current === "dark" ? "light" : current === "light" ? null : "dark";
      if (next) localStorage.setItem(KEY, next);
      else localStorage.removeItem(KEY);
      apply(next);
    });
  });
})();
