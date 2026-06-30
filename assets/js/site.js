/* OLZA OPTIC — site behaviour. Progressive enhancement only:
   every page works without JS; this layer adds the niceties. */
(function () {
  "use strict";

  /* ---------- Mobile navigation ---------- */
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav__toggle");
  if (header && toggle) {
    toggle.addEventListener("click", function () {
      var open = header.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    // Close the menu after following an in-page link on mobile
    header.querySelectorAll(".nav__menu a").forEach(function (a) {
      a.addEventListener("click", function () {
        header.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
    // Close on Escape
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && header.classList.contains("is-open")) {
        header.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  /* ---------- Photo gallery: load more ---------- */
  var moreBtn = document.querySelector("[data-gallery-more]");
  if (moreBtn) {
    moreBtn.addEventListener("click", function () {
      var hidden = document.querySelectorAll(".gallery__item.is-hidden");
      var step = 10, i = 0;
      for (; i < step && i < hidden.length; i++) {
        hidden[i].classList.remove("is-hidden");
      }
      if (document.querySelectorAll(".gallery__item.is-hidden").length === 0) {
        moreBtn.parentNode.removeChild(moreBtn);
      }
    });
  }

  /* ---------- Contact form (no backend — graceful confirmation) ---------- */
  var form = document.querySelector("[data-contact-form]");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var success = form.parentNode.querySelector(".form-success");
      if (success) {
        form.hidden = true;
        success.hidden = false;
        success.focus();
      }
    });
  }
})();
