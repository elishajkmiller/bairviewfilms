/* Stills rail: click a thumbnail to open it full screen; arrows and keys move through the stills. */
(function () {
  var rail = document.querySelector(".rail");
  if (!rail) { return; }
  var tiles = rail.querySelectorAll(".rail-t");
  var srcs = [];
  var k;
  for (k = 0; k < tiles.length; k++) {
    if (!tiles[k].hasAttribute("aria-hidden")) { srcs.push(tiles[k].querySelector("img").getAttribute("src")); }
  }

  var lb = document.createElement("div");
  lb.className = "car-lb";
  lb.hidden = true;
  lb.innerHTML = '<button type="button" class="car-x" aria-label="Close">&times;</button>' +
    '<button type="button" class="car-nav car-prev" aria-label="Previous still">&lsaquo;</button>' +
    '<button type="button" class="car-nav car-next" aria-label="Next still">&rsaquo;</button>' +
    '<img alt="">';
  document.body.appendChild(lb);
  var img = lb.querySelector("img");
  var n = 0;

  function show(to) {
    n = (to + srcs.length) % srcs.length;
    img.src = srcs[n];
    img.alt = "Still " + (n + 1) + " of " + srcs.length;
  }

  rail.addEventListener("click", function (e) {
    var t = e.target.closest(".rail-t");
    if (!t) { return; }
    show(+t.getAttribute("data-i"));
    lb.hidden = false;
  });
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
