/* Stills carousel: crossfade, arrows, dots, swipe, auto-advance, click to open a lightbox. */
(function () {
  var cars = document.querySelectorAll(".car");
  if (!cars.length) { return; }
  var calm = false;
  try { calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (er) {}

  var lb = document.createElement("div");
  lb.className = "car-lb";
  lb.hidden = true;
  lb.innerHTML = '<button type="button" class="car-x" aria-label="Close">&times;</button>' +
    '<button type="button" class="car-nav car-prev" aria-label="Previous still">&lsaquo;</button>' +
    '<button type="button" class="car-nav car-next" aria-label="Next still">&rsaquo;</button>' +
    '<img alt="">';
  document.body.appendChild(lb);
  var lbImg = lb.querySelector("img");
  var open = null;

  function Car(root) {
    var frame = root.querySelector(".car-frame");
    var imgs = frame.querySelectorAll("img");
    var bg = frame.querySelector(".car-bg");
    var dots = root.querySelectorAll(".car-dots i");
    var n = 0, timer = null, hover = false, seen = true;

    function go(to) {
      imgs[n].className = "";
      dots[n].className = "";
      n = (to + imgs.length) % imgs.length;
      imgs[n].className = "on";
      dots[n].className = "on";
      bg.style.backgroundImage = 'url("' + imgs[n].src + '")';
      if (open === api && !lb.hidden) { lbImg.src = imgs[n].getAttribute("src"); lbImg.alt = imgs[n].alt; }
    }
    function tick() {
      if (hover || !seen || !lb.hidden || document.hidden) { return; }
      go(n + 1);
    }
    var api = { go: go, step: function (d) { go(n + d); } };

    root.addEventListener("click", function (e) {
      var nb = e.target.closest(".car-nav");
      if (nb) { go(n + (nb.className.indexOf("car-next") > -1 ? 1 : -1)); return; }
      var d = e.target.closest(".car-dots i");
      if (d) { go(Array.prototype.indexOf.call(dots, d)); return; }
      if (e.target.closest(".car-frame")) {
        open = api;
        lbImg.src = imgs[n].getAttribute("src");
        lbImg.alt = imgs[n].alt;
        lb.hidden = false;
      }
    });
    frame.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { go(n - 1); }
      else if (e.key === "ArrowRight") { go(n + 1); }
      else if (e.key === "Enter" || e.key === " ") { e.preventDefault(); frame.click(); }
    });
    var x0 = null;
    frame.addEventListener("pointerdown", function (e) { x0 = e.clientX; });
    frame.addEventListener("pointerup", function (e) {
      if (x0 !== null && Math.abs(e.clientX - x0) > 40) { go(n + (e.clientX < x0 ? 1 : -1)); frame.setAttribute("data-swiped", "1"); }
      x0 = null;
    });
    frame.addEventListener("click", function (e) {
      if (frame.getAttribute("data-swiped")) { frame.removeAttribute("data-swiped"); e.stopPropagation(); }
    }, true);
    root.addEventListener("mouseenter", function () { hover = true; });
    root.addEventListener("mouseleave", function () { hover = false; });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) { seen = es[0].isIntersecting; }).observe(root);
    }
    if (!calm && imgs.length > 1) { timer = setInterval(tick, 5000); }
    return api;
  }

  for (var i = 0; i < cars.length; i++) { Car(cars[i]); }

  lb.addEventListener("click", function (e) {
    var nb = e.target.closest(".car-nav");
    if (nb) { open.step(nb.className.indexOf("car-next") > -1 ? 1 : -1); return; }
    if (e.target === lbImg) { return; }
    lb.hidden = true;
  });
  document.addEventListener("keydown", function (e) {
    if (lb.hidden) { return; }
    if (e.key === "Escape") { lb.hidden = true; }
    else if (e.key === "ArrowLeft") { open.step(-1); }
    else if (e.key === "ArrowRight") { open.step(1); }
  });
})();
