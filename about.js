/* About page: a trail of bear tracks walks across the text and the text makes room for each print.
   The prints are laid out from the size of the text block (so it works at any width); every word is wrapped in a
   span, and where a print overlaps a line a spacer is put into that line, so the words flow around it the way text
   wraps around a picture. Each print fades in and its gap opens, one after another, then stays. */
(function () {
  var sec = document.querySelector(".about");
  var box = document.querySelector(".about-text");
  var defs = document.getElementById("paw-defs");
  if (!sec || !box || !defs) { return; }
  var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var NS = "http://www.w3.org/2000/svg";
  var XL = "http://www.w3.org/1999/xlink";
  var dim = function (a) { var p = defs.getAttribute(a).split(","); return [+p[0], +p[1]]; };
  var FRONT = dim("data-front"), HIND = dim("data-hind");

  // every word except the big heading gets its own span so lines can be measured word by word
  var words = [];
  function wrap(node) {
    Array.prototype.slice.call(node.childNodes).forEach(function (k) {
      if (k.nodeType === 3) {
        var frag = document.createDocumentFragment();
        k.nodeValue.split(/(\s+)/).forEach(function (part) {
          if (!part) { return; }
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
          var s = document.createElement("span");
          s.className = "w";
          s.textContent = part;
          frag.appendChild(s);
          words.push(s);
        });
        node.replaceChild(frag, k);
      } else if (k.nodeType === 1 && k.tagName !== "BR" && k.tagName !== "H1") {
        if (k.tagName === "A") { k.classList.add("split"); }
        wrap(k);
      }
    });
  }
  wrap(box);

  var layer = document.createElement("div");
  layer.className = "paws";
  layer.setAttribute("aria-hidden", "true");
  sec.appendChild(layer);
  var gaps = [];
  var timers = [];

  // doc-space rectangle of every word, in reading order, ignoring the spacers
  function measure() {
    var sx = window.pageXOffset, sy = window.pageYOffset;
    return words.map(function (w) {
      var r = w.getBoundingClientRect();
      return { el: w, l: r.left + sx, r: r.right + sx, t: r.top + sy, b: r.bottom + sy };
    });
  }

  function trail(tx, ty, tw, th) {
    // a curve from the bottom left of the text, through its middle, to above its right edge
    var p0 = [tx - 10, ty + th + 30], p1 = [tx + tw * 0.62, ty + th * 0.7], p2 = [tx + tw + 50, ty - 10];
    var size = Math.max(64, Math.min(86, tw * 0.18));   // height of a front print
    var stride = size * 3.1, behind = size * 1.35, side = size * 0.28;
    var pts = [], cum = [0], i;
    for (i = 0; i <= 300; i++) {
      var t = i / 300;
      pts.push([(1 - t) * (1 - t) * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                (1 - t) * (1 - t) * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]]);
      if (i) { cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])); }
    }
    function at(dist) {
      dist = Math.max(0, Math.min(cum[300] - 0.01, dist));
      var j = 1;
      while (cum[j] < dist) { j++; }
      var a = pts[j - 1], b = pts[j], f = (dist - cum[j - 1]) / ((cum[j] - cum[j - 1]) || 1);
      return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, Math.atan2(b[0] - a[0], -(b[1] - a[1])) * 180 / Math.PI];
    }
    var out = [], pos = behind + 10, k = 0;
    while (pos < cum[300] - 10) {
      var right = k % 2, off = right ? side : -side;
      [["front", 0], ["hind", behind]].forEach(function (kb) {
        var q = at(pos - kb[1]), rad = q[2] * Math.PI / 180;
        var d = kb[0] === "front" ? FRONT : HIND;
        var sc = size / FRONT[1];
        out.push({
          kind: kb[0], right: right, ang: q[2], w: d[0] * sc, h: d[1] * sc,
          x: q[0] + Math.cos(rad) * off, y: q[1] + Math.sin(rad) * off, r: size * 0.44
        });
      });
      pos += stride;
      k++;
    }
    return out;
  }

  // open gaps in the lines a print overlaps, top to bottom, measuring again after each one
  function makeRoom(p) {
    var guard = 0;
    while (guard++ < 14) {
      var rects = measure(), lines = [], i, j;
      for (i = 0; i < rects.length; i++) {
        var line = null;
        for (j = 0; j < lines.length; j++) {
          if (Math.abs(lines[j].t - rects[i].t) < 4) { line = lines[j]; break; }
        }
        if (!line) { line = { t: rects[i].t, b: rects[i].b, w: [] }; lines.push(line); }
        line.w.push(rects[i]);
      }
      lines.sort(function (a, b) { return a.t - b.t; });
      var done = true;
      for (i = 0; i < lines.length && done; i++) {
        var mid = (lines[i].t + lines[i].b) / 2, dy = Math.abs(mid - p.y);
        if (dy >= p.r + (lines[i].b - lines[i].t) / 2) { continue; }
        var hc = Math.sqrt(Math.max(0, p.r * p.r - Math.min(dy, p.r) * Math.min(dy, p.r))) + 6;
        var x1 = p.x - hc, x2 = p.x + hc;
        lines[i].w.sort(function (a, b) { return a.l - b.l; });
        for (j = 0; j < lines[i].w.length; j++) {
          var w = lines[i].w[j];
          if (w.l < x2 && w.r > x1) {
            var g = document.createElement("span");
            g.className = "gap";
            g.style.width = Math.ceil(x2 - w.l) + "px";
            g.setAttribute("data-w", g.style.width);
            w.el.parentNode.insertBefore(g, w.el);
            gaps.push({ el: g, at: p.at, owner: p });
            done = false;
            break;
          }
        }
      }
      if (done) { return; }
    }
  }

  function ownWidths(p) {
    return gaps.filter(function (g) { return g.owner === p; }).map(function (g) {
      var r = g.el.getBoundingClientRect();
      return g.el.getAttribute("data-w") + "@" + Math.round(r.top + window.pageYOffset);
    }).join(",");
  }

  function build(animate) {
    timers.forEach(clearTimeout);
    timers = [];
    gaps.forEach(function (g) { g.el.parentNode.removeChild(g.el); });
    gaps = [];
    layer.innerHTML = "";
    var sx = window.pageXOffset, sy = window.pageYOffset;
    var b = box.getBoundingClientRect();
    var prints = trail(b.left + sx, b.top + sy, b.width, b.height);
    prints.forEach(function (p, i) { p.at = 0.4 + i * 0.6; });
    // the layer is as wide as the screen and as tall as the section
    var lr0 = layer.getBoundingClientRect();
    var ox = lr0.left + sx, oy = lr0.top + sy;

    // fit the gaps print by print from the top down; a gap can reflow a line an earlier print was fitted to, so go round
    // again, redoing each print's own gaps, until nothing changes
    var order = prints.slice().sort(function (a, c) { return a.y - c.y; });
    var pass, changed;
    for (pass = 0; pass < 8; pass++) {
      changed = false;
      order.forEach(function (p) {
        var before = ownWidths(p);
        gaps = gaps.filter(function (g) {
          if (g.owner !== p) { return true; }
          g.el.parentNode.removeChild(g.el);
          return false;
        });
        makeRoom(p);
        if (ownWidths(p) !== before) { changed = true; }
      });
      if (!changed) { break; }
    }

    prints.forEach(function (p) {
      var s = document.createElementNS(NS, "svg");
      s.setAttribute("class", "paw");
      s.setAttribute("width", p.w.toFixed(1));
      s.setAttribute("height", p.h.toFixed(1));
      s.setAttribute("viewBox", "0 0 " + (p.kind === "front" ? FRONT : HIND).join(" "));
      s.style.left = (p.x - ox).toFixed(1) + "px";
      s.style.top = (p.y - oy).toFixed(1) + "px";
      s.style.transform = "translate(-50%,-50%) rotate(" + p.ang.toFixed(1) + "deg)";
      s.style.setProperty("--d", p.at + "s");
      var u = document.createElementNS(NS, "use");
      u.setAttributeNS(XL, "href", "#paw-" + p.kind[0] + (p.right ? "r" : "l"));
      u.setAttribute("href", "#paw-" + p.kind[0] + (p.right ? "r" : "l"));
      s.appendChild(u);
      layer.appendChild(s);
    });

    if (still || !animate) { layer.className = "paws now"; return; }
    layer.className = "paws";
    // gaps start closed and open as their print lands
    gaps.forEach(function (g) {
      g.el.style.transition = "none";
      g.el.style.width = "0px";
    });
    void document.body.offsetWidth;
    gaps.forEach(function (g) {
      g.el.style.transition = "";
      timers.push(setTimeout(function () { g.el.style.width = g.el.getAttribute("data-w"); }, (g.at + 0.3) * 1000));
    });
  }

  var timer = 0, first = true;
  function go() { build(first); first = false; }
  window.addEventListener("resize", function () { clearTimeout(timer); timer = setTimeout(go, 200); });
  // build once the page has loaded (so fonts and the photo are in), then play the landing
  if (document.readyState === "complete") { go(); } else { window.addEventListener("load", go); }
})();
