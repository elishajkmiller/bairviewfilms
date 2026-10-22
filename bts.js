/* BTS photo walls: click a photo to open it full screen; arrows and keys move through that film's photos. */
(function () {
  var grids = document.querySelectorAll(".bts-grid");
  if (!grids.length) { return; }
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

  var g;
  for (g = 0; g < grids.length; g++) {
    grids[g].addEventListener("click", function (e) {
      var t = e.target.closest(".bts-t");
      if (!t) { return; }
      var tiles = e.currentTarget.querySelectorAll(".bts-t");
      var k;
      srcs = [];
      for (k = 0; k < tiles.length; k++) { srcs.push(tiles[k].getAttribute("data-full")); }
      show(Array.prototype.indexOf.call(tiles, t));
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
