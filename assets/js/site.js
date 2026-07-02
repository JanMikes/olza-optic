/* OLZA OPTIC — progressive enhancement for the pre-rendered static site.
   Every page works without JS; this only adds the interactions that the
   original React design system provided at runtime. */
(function () {
  "use strict";

  /* ---------- Mobile navigation ---------- */
  var burger = document.querySelector(".nav-burger");
  var menu = document.getElementById("mobile-menu");
  if (burger && menu) {
    var setOpen = function (open) {
      menu.classList.toggle("open", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
      burger.setAttribute("aria-label", open ? "Zavřít menu" : "Otevřít menu");
    };
    burger.addEventListener("click", function () {
      setOpen(!menu.classList.contains("open"));
    });
    menu.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { setOpen(false); });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("open")) {
        setOpen(false);
        burger.focus();
      }
    });
  }

  /* ---------- Photo gallery: load more (steps of 8) ---------- */
  var moreBtn = document.querySelector("[data-gallery-more]");
  if (moreBtn) {
    moreBtn.addEventListener("click", function () {
      var hidden = document.querySelectorAll(".gal-item[hidden]");
      for (var i = 0; i < 8 && i < hidden.length; i++) {
        hidden[i].removeAttribute("hidden");
        hidden[i].classList.remove("gal-item-hidden");
      }
      if (document.querySelectorAll(".gal-item[hidden]").length === 0 && moreBtn.parentNode) {
        moreBtn.parentNode.style.display = "none";
      }
    });
  }

  /* ---------- Contact form (no backend — graceful confirmation) ---------- */
  var form = document.querySelector("#kontakt form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = document.createElement("div");
      ok.setAttribute("role", "status");
      ok.setAttribute("tabindex", "-1");
      ok.style.cssText =
        "display:flex;align-items:center;gap:10px;background:rgba(255,255,255,0.12);" +
        "padding:16px 18px;color:var(--paper);font-size:14px;font-weight:600";
      ok.innerHTML =
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#e7bd83" ' +
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/></svg>' +
        "Děkujeme! Ozveme se Vám do 24 hodin.";
      form.replaceWith(ok);
      ok.focus();
    });
  }

  /* ---------- Scroll-spy for the homepage in-page nav ---------- */
  try {
    var anchors = [].slice.call(document.querySelectorAll('.r-navlinks a[href^="#"]'));
    if (anchors.length) {
      var ids = anchors
        .map(function (a) { return a.getAttribute("href").slice(1); })
        .filter(Boolean);
      var spy = function () {
        var cur = ids[0];
        ids.forEach(function (id) {
          var el = document.getElementById(id);
          if (el && el.getBoundingClientRect().top <= 120) cur = id;
        });
        anchors.forEach(function (a) {
          var active = a.getAttribute("href") === "#" + cur;
          a.style.color = active ? "var(--ochre-300, #e7bd83)" : "rgba(247,245,239,0.82)";
          var bar = a.querySelector("span");
          if (bar) bar.style.transform = active ? "scaleX(1)" : "scaleX(0)";
        });
      };
      window.addEventListener("scroll", spy, { passive: true });
      spy();
    }
  } catch (e) { /* non-critical */ }
})();
