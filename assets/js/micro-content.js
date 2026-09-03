/* OLZA OPTIC — scheduled notice bar from the BiteIT micro-content CMS.

   The client writes a notice in the admin and gives it a date window;
   this reveals the bar only while that window is open, which is why it
   cannot be baked in at build time the way the opening hours are (see
   tools/sync-opening-hours.py). The bar ships hidden, so a failed or
   empty fetch simply leaves the page as designed.

   Vendor-free re-implementation of BJ_MicroContent.loadSmallUpperBanner:
   the original needs jQuery, which this site does not load. Same API and
   same 1h cache, so the client sees identical behaviour to the other
   sites. */
(function () {
  "use strict";

  var CUSTOMER = "538b6d648927b777cd75e266dcefe85d";
  var API = "https://job3.biteit.cz/fapi/content/";
  var TTL = 60 * 60 * 1000; /* 1 h — same lifespan as the vendor script */

  var bars = document.querySelectorAll("[data-microcontent-banner]");
  if (!bars.length) return;

  var storageKey = function (hash) {
    return "microcontent-" + CUSTOMER + "-" + hash;
  };

  var readCache = function (hash) {
    try {
      var raw = localStorage.getItem(storageKey(hash));
      if (!raw) return null;
      var box = JSON.parse(raw);
      if (Date.now() - box.time > TTL) {
        localStorage.removeItem(storageKey(hash));
        return null;
      }
      return box.content;
    } catch (e) {
      return null;
    }
  };

  var writeCache = function (hash, content) {
    try {
      localStorage.setItem(storageKey(hash), JSON.stringify({ time: Date.now(), content: content }));
    } catch (e) { /* private mode or quota — just go without the cache */ }
  };

  /* The source is a WYSIWYG editor, so trust it for markup and nothing else. */
  var parse = function (html) {
    var body = new DOMParser().parseFromString(html, "text/html").body;
    body.querySelectorAll("script,style,iframe,object,embed,link,meta").forEach(function (el) {
      el.remove();
    });
    body.querySelectorAll("*").forEach(function (el) {
      [].slice.call(el.attributes).forEach(function (attr) {
        if (/^on/i.test(attr.name) || /^\s*javascript:/i.test(attr.value)) {
          el.removeAttribute(attr.name);
        }
      });
    });
    return body;
  };

  /* Editors pad text with runs of &nbsp; to fake alignment; collapse them. */
  var collapseSpacing = function (root) {
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      node.nodeValue = node.nodeValue.replace(/[\s\u00a0]{2,}/g, " ");
    }
    return root;
  };

  var fetchContent = function (hash) {
    var cached = readCache(hash);
    if (cached) return Promise.resolve(cached);

    return fetch(API + CUSTOMER + "/" + hash, { credentials: "omit" })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
      .then(function (res) {
        var content = res && res.data && res.data.content;
        if (typeof content !== "string" || !content) return Promise.reject("empty");
        writeCache(hash, content);
        return content;
      });
  };

  bars.forEach(function (bar) {
    var hash = bar.getAttribute("data-microcontent-banner");
    fetchContent(hash)
      .then(function (raw) {
        var entry = JSON.parse(raw);
        var from = Date.parse(entry.dateFrom);
        var to = Date.parse(entry.dateTo);
        var now = Date.now();
        if (isNaN(from) || isNaN(to) || now < from || now > to) return;

        var body = collapseSpacing(parse(entry.content || ""));
        if (!body.textContent.trim()) return; /* nothing to say — stay hidden */
        bar.textContent = "";
        while (body.firstChild) bar.appendChild(body.firstChild);
        bar.hidden = false;
      })
      .catch(function () { /* no notice scheduled, or CMS down — stay hidden */ });
  });
})();
