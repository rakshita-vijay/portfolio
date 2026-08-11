(function () {
  // ---- theme toggle ----
  var root = document.documentElement;
  var toggle = document.getElementById("themeToggle");
  var stored = localStorage.getItem("theme");
  var prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  var initial = stored || (prefersDark ? "dark" : "light");
  root.setAttribute("data-theme", initial);

  toggle.addEventListener("click", function () {
    var current = root.getAttribute("data-theme");
    var next = current === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
  });

  // ---- scroll-spy nav ----
  var sections = Array.prototype.slice.call(document.querySelectorAll(".section[id]"));
  var navLinks = Array.prototype.slice.call(document.querySelectorAll(".nav-link"));

  function setActive(id) {
    navLinks.forEach(function (link) {
      link.classList.toggle("active", link.getAttribute("href") === "#" + id);
    });
  }

  if ("IntersectionObserver" in window && sections.length) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) setActive(entry.target.id);
        });
      },
      { rootMargin: "-20% 0px -70% 0px", threshold: 0 }
    );
    sections.forEach(function (s) { observer.observe(s); });
  }
})();
