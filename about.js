/* About page: a trail of bear tracks walks down the gap between the photo and the text, the full height of the page (across, when the page is one
   column and the photo sits above the text). The trail is laid out from the measured positions of the photo and the
   text, so it works at any width; the prints fade in one after another and then stay. */
(function () {
  var sec = document.querySelector(".about");
  var box = document.querySelector(".about-text");
  var photo = document.querySelector(".about .portrait");
  var defs = document.getElementById("paw-defs");
  if (!sec || !box || !defs) { return; }
  var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var NS = "http://www.w3.org/2000/svg";
  var XL = "http://www.w3.org/1999/xlink";
  var dim = function (a) { var p = defs.getAttribute(a).split(","); return [+p[0], +p[1]]; };
  var FRONT = dim("data-front"), HIND = dim("data-hind");

  var layer = document.createElement("div");
  layer.className = "paws";
  layer.setAttribute("aria-hidden", "true");
  var main = document.querySelector("main") || sec;
  main.appendChild(layer);

  // doc-space start and end of the walk, and the width of the lane the bear has
  function lane() {
    var sx = window.pageXOffset, sy = window.pageYOffset;
    var t = box.getBoundingClientRect();
    if (!photo) { return null; }
    var p = photo.getBoundingClientRect();
    if (t.left >= p.right - 1) {
      var gx = (p.right + t.left) / 2 + sx;
      var m = main.getBoundingClientRect();   // the walk runs the whole height of the page, header to footer
      return { a: [gx, m.top + sy], b: [gx, m.bottom + sy], w: t.left - p.right };
    }
    var gy = (p.bottom + t.top) / 2 + sy;
    return { a: [p.left + sx, gy], b: [Math.max(t.right, p.right) + sx, gy], w: t.top - p.bottom };
  }

  function trail(ln) {
    var size = Math.max(30, Math.min(60, ln.w * 0.45));   // height of a front print
    var stride = size * 2.5, behind = size * 1.2, side = size * 0.22;
    var dx = ln.b[0] - ln.a[0], dy = ln.b[1] - ln.a[1], len = Math.hypot(dx, dy);
    var ux = dx / len, uy = dy / len;
    var ang = Math.atan2(ux, -uy) * 180 / Math.PI, rad = ang * Math.PI /  180;
    // spread whole steps evenly so the last print lands near the end of the lane
    var first = behind + size * 0.6, avail = len - first - size * 0.6;
    var steps = Math.max(0, Math.round(avail / stride));
    if (steps) { stride = avail / steps; }
    var out = [], k;
    for (k = 0; k <= steps; k++) {
      var pos = first + k * stride, right = k % 2, off = right ? side : -side;
      [["front", 0], ["hind", behind]].forEach(function (kb) {
        var d = kb[0] === "front" ? FRONT : HIND, sc = size / FRONT[1], at = pos - kb[1];
        out.push({
          kind: kb[0], right: right, ang: ang, w: d[0] * sc, h: d[1] * sc,
          x: ln.a[0] + ux * at + Math.cos(rad) * off, y: ln.a[1] + uy * at + Math.sin(rad) * off
        });
      });
    }
    return out;
  }

  function build(animate) {
    layer.innerHTML = "";
    var ln = lane();
    if (!ln) { return; }
    var prints = trail(ln);
    var lr = layer.getBoundingClientRect();
    var ox = lr.left + window.pageXOffset, oy = lr.top + window.pageYOffset;
    prints.forEach(function (p, i) {
      var s = document.createElementNS(NS, "svg");
      s.setAttribute("class", "paw");
      s.setAttribute("width", p.w.toFixed(1));
      s.setAttribute("height", p.h.toFixed(1));
      s.setAttribute("viewBox", "0 0 " + (p.kind === "front" ? FRONT : HIND).join(" "));
      s.style.left = (p.x - ox).toFixed(1) + "px";
      s.style.top = (p.y - oy).toFixed(1) + "px";
      s.style.transform = "translate(-50%,-50%) rotate(" + p.ang.toFixed(1) + "deg)";
      s.style.setProperty("--d", (0.4 + i * 0.4) + "s");
      var u = document.createElementNS(NS, "use");
      u.setAttributeNS(XL, "href", "#paw-" + p.kind[0] + (p.right ? "r" : "l"));
      u.setAttribute("href", "#paw-" + p.kind[0] + (p.right ? "r" : "l"));
      s.appendChild(u);
      layer.appendChild(s);
    });
    layer.className = (still || !animate) ? "paws now" : "paws";
  }

  var timer = 0, first = true;
  function go() { build(first); first = false; }
  window.addEventListener("resize", function () { clearTimeout(timer); timer = setTimeout(go, 200); });
  // build once the page has loaded (so fonts and the photo are in), then play the landing
  if (document.readyState === "complete") { go(); } else { window.addEventListener("load", go); }
})();
