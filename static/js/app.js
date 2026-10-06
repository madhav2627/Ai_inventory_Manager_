/* ══════════════════════════════════════════════════════════════════
   Ledger — Premium UI interactions
   ══════════════════════════════════════════════════════════════════ */
document.addEventListener("DOMContentLoaded", function () {
  var reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.documentElement.classList.toggle("reduced-motion", !!reducedMotion);


  /* ── Flash message auto-dismiss with slide-out ───────────────── */
  document.querySelectorAll(".flash").forEach(function (el, i) {
    // Stagger multiple flashes
    el.style.animationDelay = (i * 0.08) + 's';
    setTimeout(function () {
      el.style.transition = "opacity 0.4s ease, transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)";
      el.style.opacity = "0";
      el.style.transform = "translateX(30px)";
      setTimeout(function () { el.remove(); }, 400);
    }, 4000 + i * 200);
  });

  /* ── Dark / Light theme toggle with rotation ─────────────────── */
  var themeBtns = document.querySelectorAll(".theme-toggle-btn");
  themeBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var html = document.documentElement;
      var current = html.getAttribute("data-theme");
      var next = current === "dark" ? "light" : "dark";

      // Spin animation on toggle for all theme buttons
      themeBtns.forEach(function (tb) {
        tb.style.transition = "transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)";
        tb.style.transform = "rotate(" + (next === "dark" ? "360" : "-360") + "deg)";
        setTimeout(function() { tb.style.transform = ""; }, 500);
      });

      html.setAttribute("data-theme", next);
      var themeMeta = document.getElementById("app-theme-color");
      if (themeMeta) themeMeta.setAttribute("content", next === "dark" ? "#0b0e14" : "#f6f3ed");
      localStorage.setItem("ledger-theme", next);
    });
  });

  /* ── Mobile Sidebar Menu Drawer Toggling ─────────────────────── */
  var menuToggle = document.getElementById("mobile-menu-toggle");
  var navOverlay = document.getElementById("nav-overlay");
  
  if (menuToggle && navOverlay) {
    function toggleMenu() {
      var open = document.body.classList.toggle("nav-open");
      menuToggle.setAttribute("aria-expanded", open ? "true" : "false");
    }
    function closeMenu() {
      document.body.classList.remove("nav-open");
      menuToggle.setAttribute("aria-expanded", "false");
    }
    
    menuToggle.addEventListener("click", toggleMenu);
    navOverlay.addEventListener("click", closeMenu);
    
    // Close menu when navigation item is clicked
    document.querySelectorAll(".sidebar .nav-item, .mobile-bottom-nav .mobile-nav-item").forEach(function(item) {
      item.addEventListener("click", closeMenu);
    });

    // Close menu on screen resize to desktop
    window.addEventListener("resize", function() {
      if (window.innerWidth > 980) {
        closeMenu();
      }
    });

    document.addEventListener("keydown", function(e) {
      if (e.key === "Escape") closeMenu();
    });
  }

  /* ── Inventory shortcut: focus search without stealing typing ────── */
  var inventorySearch = document.getElementById("inventory-search");
  if (inventorySearch) {
    document.addEventListener("keydown", function (event) {
      var target = event.target;
      var tagName = target && target.tagName ? target.tagName.toLowerCase() : "";
      var isTyping = tagName === "input" || tagName === "textarea" || target && target.isContentEditable;
      if (event.key === "/" && !event.ctrlKey && !event.metaKey && !event.altKey && !isTyping) {
        event.preventDefault();
        inventorySearch.focus();
      }
    });
  }

  /* ── Animated number counter ─────────────────────────────────── */
  function animateCount(el) {
    var target = parseFloat(el.getAttribute("data-count-to"));
    if (isNaN(target)) return;

    var prefix = el.getAttribute("data-prefix") || "";
    var isDecimal = String(target).indexOf('.') > -1;
    var duration = reducedMotion ? 0 : 700; // ms
    var startTime = null;

    // Start from 0
    el.textContent = prefix + (isDecimal ? "0.00" : "0");

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      var progress = Math.min((timestamp - startTime) / duration, 1);
      // Ease out cubic
      var eased = 1 - Math.pow(1 - progress, 3);
      var current = target * eased;

      el.textContent = prefix + (isDecimal ? current.toFixed(2) : Math.round(current));

      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = prefix + (isDecimal ? target.toFixed(2) : String(target));
      }
    }

    requestAnimationFrame(step);
  }

  // Trigger counting on elements with data-count-to
  var countEls = document.querySelectorAll("[data-count-to]");
  if (countEls.length > 0) {
    // Use IntersectionObserver for scroll-triggered animations
    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            if (reducedMotion) animateCount(entry.target);
            else setTimeout(function() { animateCount(entry.target); }, 70);
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.3 });

      countEls.forEach(function(el) { observer.observe(el); });
    } else {
      // Fallback: animate immediately
      countEls.forEach(function(el) { animateCount(el); });
    }
  }

  /* ── Staggered grid reveal ───────────────────────────────────── */
  var grids = document.querySelectorAll(".product-grid, .stat-grid");
  if (!reducedMotion) grids.forEach(function(grid) {
    var children = grid.children;
    for (var i = 0; i < children.length; i++) {
      children[i].style.animation = "fadeInUp 0.4s " + (0.04 + i * 0.04) + "s cubic-bezier(0.22, 1, 0.36, 1) both";
    }
  });

  /* ── Sidebar active indicator smooth entrance ────────────────── */
  var activeNav = document.querySelector(".nav-item.is-active");
  if (activeNav) {
    activeNav.style.animation = "none";
    // Force reflow
    void activeNav.offsetWidth;
    activeNav.style.animation = "";
  }

  /* ── AI command bar micro-interaction ─────────────────────────── */
  var aiCommandInput = document.getElementById("nlp-input");
  if (aiCommandInput) {
    aiCommandInput.addEventListener("focus", function () {
      var bar = aiCommandInput.closest(".ai-command-bar");
      if (bar) bar.classList.add("is-focused");
    });
    aiCommandInput.addEventListener("blur", function () {
      var bar = aiCommandInput.closest(".ai-command-bar");
      if (bar) bar.classList.remove("is-focused");
    });
  }

});
