(function () {
  // ---- theme (light / dark / auto) ----
  var root = document.documentElement;
  var toggle = document.getElementById("themeToggle");
  var media = window.matchMedia("(prefers-color-scheme: dark)");

  function effectiveTheme(mode) {
    return mode === "auto" ? (media.matches ? "dark" : "light") : mode;
  }
  function applyTheme(mode) {
    root.setAttribute("data-theme", effectiveTheme(mode));
    localStorage.setItem("theme", mode);
  }
  applyTheme(localStorage.getItem("theme") || "dark");

  media.addEventListener("change", function () {
    if (localStorage.getItem("theme") === "auto") applyTheme("auto");
  });

  toggle.addEventListener("click", function () {
    var current = root.getAttribute("data-theme");
    applyTheme(current === "dark" ? "light" : "dark");
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

  // ---- local time (IST, 12hr) ----
  var timeEl = document.getElementById("localTime");
  if (timeEl) {
    var tz = timeEl.getAttribute("data-tz") || "Asia/Kolkata";
    var fmt = new Intl.DateTimeFormat("en-US", {
      timeZone: tz, hour: "numeric", minute: "2-digit", second: "2-digit", hour12: true
    });
    function tick() { timeEl.textContent = fmt.format(new Date()); }
    tick();
    setInterval(tick, 1000);
  }

  // ---- click-to-reveal contact info ----
  Array.prototype.slice.call(document.querySelectorAll(".reveal-btn")).forEach(function (btn) {
    btn.addEventListener("click", function () {
      var kind = btn.getAttribute("data-reveal");
      var value = btn.getAttribute("data-value");
      var link = document.createElement("a");
      link.className = "meta-value link revealed";
      link.textContent = value;
      link.href = kind === "email" ? "mailto:" + value : "tel:" + value;
      link.setAttribute("data-reveal", kind);
      link.setAttribute("data-value", value);
      btn.replaceWith(link);
    });
  });

  // ---- utm tracking on outbound links ----
  function addUtm(url) {
    try {
      var u = new URL(url, window.location.href);
      if (u.origin === window.location.origin) return url; // internal/local asset, leave alone
      if (!u.searchParams.has("utm_source")) u.searchParams.set("utm_source", "portfolio");
      if (!u.searchParams.has("utm_medium")) u.searchParams.set("utm_medium", "referral");
      return u.toString();
    } catch (e) {
      return url;
    }
  }
  Array.prototype.slice.call(document.querySelectorAll("a[href^='http']")).forEach(function (a) {
    a.setAttribute("href", addUtm(a.getAttribute("href")));
  });

  // ---- mobile hamburger menu ----
  var mobileMenuTrigger = document.getElementById("mobileMenuTrigger");
  var mobileNav = document.getElementById("mobileNav");
  if (mobileMenuTrigger && mobileNav) {
    var openMobileNav = function () {
      mobileNav.hidden = false;
      mobileMenuTrigger.classList.add("open");
      mobileMenuTrigger.setAttribute("aria-expanded", "true");
    };
    var closeMobileNav = function () {
      mobileNav.hidden = true;
      mobileMenuTrigger.classList.remove("open");
      mobileMenuTrigger.setAttribute("aria-expanded", "false");
    };
    mobileMenuTrigger.addEventListener("click", function (e) {
      e.stopPropagation();
      mobileNav.hidden ? openMobileNav() : closeMobileNav();
    });
    Array.prototype.slice.call(mobileNav.querySelectorAll(".mobile-nav-link")).forEach(function (link) {
      link.addEventListener("click", closeMobileNav);
    });
    document.addEventListener("click", function (e) {
      if (!mobileNav.hidden && !mobileNav.contains(e.target) && !mobileMenuTrigger.contains(e.target)) {
        closeMobileNav();
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !mobileNav.hidden) closeMobileNav();
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 860) closeMobileNav();
    });
  }

  // ---- resume / vCard dropdown ----
  function getContactValue(kind) {
    var el = document.querySelector('[data-reveal="' + kind + '"]');
    if (!el) return "";
    return el.getAttribute("data-value") || el.textContent.trim();
  }

  function downloadVCard() {
    var email = getContactValue("email");
    var tel = getContactValue("tel");
    var lines = [
      "BEGIN:VCARD",
      "VERSION:3.0",
      "N:Vijay;Rakshita;;;",
      "FN:Rakshita Vijay",
      "TITLE:CS Engineering Student \u00b7 AI/ML",
      "ORG:BITS Pilani, Hyderabad Campus",
      email ? "EMAIL;TYPE=INTERNET:" + email : null,
      tel ? "TEL;TYPE=CELL:" + tel : null,
      "URL:https://github.com/rakshita-vijay",
      "URL:https://www.linkedin.com/in/rakshita-vijay/",
      "END:VCARD"
    ].filter(Boolean);
    var blob = new Blob([lines.join("\r\n")], { type: "text/vcard;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "rakshita-vijay.vcf";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  var resumeMenuTrigger = document.getElementById("resumeMenuTrigger");
  var resumeMenu = document.getElementById("resumeMenu");
  var vcardBtn = document.getElementById("vcardBtn");

  if (resumeMenuTrigger && resumeMenu) {
    var openResumeMenu = function () {
      resumeMenu.hidden = false;
      resumeMenuTrigger.setAttribute("aria-expanded", "true");
    };
    var closeResumeMenu = function () {
      resumeMenu.hidden = true;
      resumeMenuTrigger.setAttribute("aria-expanded", "false");
    };
    resumeMenuTrigger.addEventListener("click", function (e) {
      e.stopPropagation();
      resumeMenu.hidden ? openResumeMenu() : closeResumeMenu();
    });
    document.addEventListener("click", function (e) {
      if (!resumeMenu.hidden && !resumeMenu.contains(e.target) && !resumeMenuTrigger.contains(e.target)) {
        closeResumeMenu();
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !resumeMenu.hidden) closeResumeMenu();
    });
    if (vcardBtn) {
      vcardBtn.addEventListener("click", function () {
        downloadVCard();
        closeResumeMenu();
      });
    }
  }

  // ---- scroll to top ----
  var scrollTopBtn = document.getElementById("scrollTop");
  if (scrollTopBtn) {
    window.addEventListener("scroll", function () {
      scrollTopBtn.classList.toggle("visible", window.scrollY > 400);
    });
    scrollTopBtn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // ---- command palette ----
  var cmdkOverlay = document.getElementById("cmdkOverlay");
  var cmdkInput = document.getElementById("cmdkInput");
  var cmdkBody = document.getElementById("cmdkBody");
  var cmdkTrigger = document.getElementById("cmdkTrigger");
  var cmdkClose = document.getElementById("cmdkClose");

  var ICONS = {
    about: '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M4 6h16M4 12h10M4 18h7"/>',
    education: '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M12 3 2 8l10 5 10-5-10-5Z"/><path fill="none" stroke="currentColor" stroke-width="2" d="M6 10.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-5.5"/>',
    stack: '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="m12 3 9 5-9 5-9-5 9-5Z"/><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="m3 13 9 5 9-5"/>',
    experience: '<rect x="3" y="7" width="18" height="13" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path fill="none" stroke="currentColor" stroke-width="2" d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
    projects: '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M12 2 3 7l9 5 9-5-9-5Z"/><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M3 12l9 5 9-5M3 17l9 5 9-5"/>',
    leadership: '<circle cx="12" cy="8" r="5" fill="none" stroke="currentColor" stroke-width="2"/><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M8.5 12.5 7 22l5-3 5 3-1.5-9.5"/>',
    talks: '<rect x="9" y="2" width="6" height="12" rx="3" fill="none" stroke="currentColor" stroke-width="2"/><path fill="none" stroke="currentColor" stroke-width="2" d="M5 11a7 7 0 0 0 14 0M12 18v4"/>',
    github: '<path fill="currentColor" d="M12 .5a12 12 0 0 0-3.79 23.39c.6.11.82-.26.82-.58l-.01-2.23c-3.34.73-4.04-1.42-4.04-1.42-.55-1.38-1.33-1.76-1.33-1.76-1.09-.74.08-.73.08-.73 1.2.09 1.84 1.24 1.84 1.24 1.07 1.83 2.8 1.3 3.49.99.11-.78.42-1.3.76-1.6-2.66-.3-5.47-1.34-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.12-.3-.54-1.53.12-3.18 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 0 1 6 0c2.29-1.55 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.77.84 1.24 1.91 1.24 3.22 0 4.6-2.81 5.62-5.49 5.92.43.37.81 1.1.81 2.22l-.01 3.29c0 .32.22.7.83.58A12 12 0 0 0 12 .5Z"/>',
    linkedin: '<path fill="currentColor" d="M20.45 20.45h-3.56v-5.58c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.95v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.38-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.07 2.07 0 1 1 0-4.13 2.07 2.07 0 0 1 0 4.13ZM7.12 20.45H3.56V9h3.56v11.45Z"/>',
    sun: '<circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M12 2v2M12 20v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M2 12h2M20 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/>',
    moon: '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M20 14.5A9 9 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z"/>',
    auto: '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path fill="currentColor" d="M12 3a9 9 0 0 1 0 18V3Z"/>',
    resume: '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 3v11m0 0 4-4m-4 4-4-4M5 19h14"/>',
    vcard: '<rect x="3" y="6" width="18" height="12" rx="1.5" fill="none" stroke="currentColor" stroke-width="2"/><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M3 8l9 6 9-6"/>'
  };

  function svg(name) { return '<svg viewBox="0 0 24 24" width="16" height="16">' + ICONS[name] + '</svg>'; }

  function goTo(hash) {
    var el = document.querySelector(hash);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  }
  function openUrl(url) { window.open(addUtm(url), "_blank", "noopener"); }

  var cmdkGroups = [
    {
      label: "Portfolio",
      items: [
        { label: "About", icon: "about", action: function () { goTo("#about"); } },
        { label: "Education", icon: "education", action: function () { goTo("#education"); } },
        { label: "Stack", icon: "stack", action: function () { goTo("#stack"); } },
        { label: "Experience", icon: "experience", action: function () { goTo("#experience"); } },
        { label: "Projects", icon: "projects", action: function () { goTo("#projects"); } },
        { label: "Leadership", icon: "leadership", action: function () { goTo("#leadership"); } },
        { label: "Talks & Workshops", icon: "talks", action: function () { goTo("#extras"); } },
        { label: "Resume", icon: "resume", action: function () { openUrl("assets/resume.pdf"); } },
        { label: "Save Contact (vCard)", icon: "vcard", action: function () { downloadVCard(); } }
      ]
    },
    {
      label: "Social Links",
      items: [
        { label: "GitHub", icon: "github", action: function () { openUrl("https://github.com/rakshita-vijay"); } },
        { label: "LinkedIn", icon: "linkedin", action: function () { openUrl("https://www.linkedin.com/in/rakshita-vijay/"); } }
      ]
    },
    {
      label: "Theme",
      items: [
        { label: "Light", icon: "sun", action: function () { applyTheme("light"); } },
        { label: "Dark", icon: "moon", action: function () { applyTheme("dark"); } },
        { label: "Auto", icon: "auto", action: function () { applyTheme("auto"); } }
      ]
    }
  ];

  var activeIndex = -1;
  var currentFiltered = [];
  var flatRendered = [];

  function renderGroups(groups) {
    cmdkBody.innerHTML = "";
    var flat = [];
    var anyItems = groups.some(function (g) { return g.items.length; });
    if (!anyItems) {
      var empty = document.createElement("div");
      empty.className = "cmdk-empty";
      empty.textContent = "No matches.";
      cmdkBody.appendChild(empty);
      return flat;
    }
    groups.forEach(function (g) {
      if (!g.items.length) return;
      var label = document.createElement("div");
      label.className = "cmdk-group-label";
      label.textContent = g.label;
      cmdkBody.appendChild(label);
      g.items.forEach(function (item) {
        var row = document.createElement("div");
        row.className = "cmdk-item";
        row.innerHTML = svg(item.icon) + "<span>" + item.label + "</span>";
        row.addEventListener("click", function () { runItem(item); });
        cmdkBody.appendChild(row);
        flat.push({ item: item, el: row });
      });
    });
    return flat;
  }

  function filterItems(q) {
    q = q.trim().toLowerCase();
    var groups = !q ? cmdkGroups : cmdkGroups.map(function (g) {
      return { label: g.label, items: g.items.filter(function (i) { return i.label.toLowerCase().indexOf(q) !== -1; }) };
    });
    flatRendered = renderGroups(groups);
    currentFiltered = flatRendered.map(function (r) { return r.item; });
    activeIndex = flatRendered.length ? 0 : -1;
    if (flatRendered.length) flatRendered[0].el.classList.add("active");
  }

  function runItem(item) {
    closePalette();
    item.action();
  }

  function openPalette() {
    cmdkOverlay.hidden = false;
    cmdkInput.value = "";
    filterItems("");
    cmdkInput.focus();
  }
  function closePalette() {
    cmdkOverlay.hidden = true;
  }

  if (cmdkOverlay && cmdkInput && cmdkBody) {
    if (cmdkTrigger) cmdkTrigger.addEventListener("click", openPalette);
    if (cmdkClose) cmdkClose.addEventListener("click", closePalette);

    document.addEventListener("keydown", function (e) {
      var isCmdK = (e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k";
      if (isCmdK) {
        e.preventDefault();
        cmdkOverlay.hidden ? openPalette() : closePalette();
        return;
      }
      if (cmdkOverlay.hidden) return;
      if (e.key === "Escape") { closePalette(); return; }
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!flatRendered.length) return;
        flatRendered[activeIndex] && flatRendered[activeIndex].el.classList.remove("active");
        activeIndex = e.key === "ArrowDown"
          ? (activeIndex + 1) % flatRendered.length
          : (activeIndex - 1 + flatRendered.length) % flatRendered.length;
        flatRendered[activeIndex].el.classList.add("active");
        flatRendered[activeIndex].el.scrollIntoView({ block: "nearest" });
      }
      if (e.key === "Enter") {
        e.preventDefault();
        if (currentFiltered[activeIndex]) runItem(currentFiltered[activeIndex]);
      }
    });

    cmdkInput.addEventListener("input", function () { filterItems(cmdkInput.value); });
    cmdkOverlay.addEventListener("click", function (e) {
      if (e.target === cmdkOverlay) closePalette();
    });
  }
})();
