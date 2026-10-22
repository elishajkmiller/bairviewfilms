/* BTS page: a click-to-play video on the left of each film row with tabs for more videos, and a photo strip
   on the right whose tiles open full screen; arrows and keys move through that film's photos. */
(function () {
  function play(box, id, title) {
    box.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + id +
      '?autoplay=1" title="' + title + '" allow="autoplay; fullscreen" allowfullscreen></iframe>';
    box.classList.add("playing");
  }

  var cols = document.querySelectorAll(".vid-col");
  var c;
  for (c = 0; c < cols.length; c++) {
    cols[c].addEventListener("click", function (e) {
      var col = e.currentTarget;
      var box = col.querySelector(".vthumb");
      var tab = e.target.closest(".vtabs button");
      var src = tab || e.target.closest("button.vthumb");
      if (!src) { return; }
      var id = src.getAttribute("data-id");
      var title = src.getAttribute("data-title");
      if (tab) {
        var tabs = col.querySelectorAll(".vtabs button");
        var t;
        for (t = 0; t < tabs.length; t++) { tabs[t].classList.toggle("on", tabs[t] === tab); }
        col.querySelector(".vcap").textContent = title;
        if (box.tagName === "BUTTON") {
          var d = document.createElement("div");
          d.className = "vthumb";
          box.parentNode.replaceChild(d, box);
          box = d;
        }
      } else if (box.tagName !== "BUTTON") {
        return;
      }
      play(box, id, title);
    });
  }

  var rails = document.querySelectorAll(".rail");
  if (!rails.length) { return; }
  var lb = document.createElement("div");
  lb.className = "car-lb";
  lb.hidden = true;
  lb.innerHTML = '<button type="button" class="car-x" aria-label="Close">&times;</button>' +
    '<button type="button" class="car-nav car-prev" aria-label="Previous photo">&lsaquo;</button>' +
    '<button type="button" class="car-nav car-next" aria-label="Next photo">&rsaquo;</button>' +
    '<img alt="">';
  document.body.appendChild(lb);
  var img = lb.querySelector("img");
  var srcs = [];
  var n = 0;

  function show(to) {
    n = (to + srcs.length) % srcs.length;
    img.src = srcs[n];
    img.alt = "Behind the scenes photo " + (n + 1) + " of " + srcs.length;
  }

  var r;
  for (r = 0; r < rails.length; r++) {
    rails[r].addEventListener("click", function (e) {
      var t = e.target.closest(".rail-t");
      if (!t) { return; }
      var tiles = e.currentTarget.querySelectorAll(".rail-t");
      var k;
      srcs = [];
      for (k = 0; k < tiles.length; k++) {
        if (!tiles[k].hasAttribute("aria-hidden")) { srcs.push(tiles[k].getAttribute("data-full")); }
      }
      show(+t.getAttribute("data-i"));
      lb.hidden = false;
    });
  }
  lb.addEventListener("click", function (e) {
    var nb = e.target.closest(".car-nav");
    if (nb) { show(n + (nb.className.indexOf("car-next") > -1 ? 1 : -1)); return; }
    if (e.target !== img) { lb.hidden = true; }
  });
  document.addEventListener("keydown", function (e) {
    if (lb.hidden) { return; }
    if (e.key === "Escape") { lb.hidden = true; }
    else if (e.key === "ArrowLeft") { show(n - 1); }
    else if (e.key === "ArrowRight") { show(n + 1); }
  });
})();
