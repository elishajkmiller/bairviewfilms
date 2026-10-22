/* Contact form: the chosen button shows its extra fields, the form posts to the Apps Script web app in
   data-endpoint, and falls back to the visitor's mail app when no endpoint is set. */
(function () {
  var form = document.getElementById("contact");
  if (!form) { return; }
  var sets = form.querySelectorAll(".extra");
  var msg = form.querySelector(".msg");
  var send = form.querySelector("button[type=submit]");
  var note = form.querySelector(".status-line");
  var text = form.querySelector("textarea[name=message]");
  var key = "";

  function choose(k) {
    key = k;
    var i;
    for (i = 0; i < sets.length; i++) {
      var on = sets[i].getAttribute("data-key") === k;
      sets[i].hidden = !on;
      sets[i].disabled = !on;
    }
    msg.hidden = false;
    send.hidden = false;
    text.required = k === "reach";
    note.textContent = "";
  }

  form.addEventListener("change", function (e) {
    if (e.target.name === "type") { choose(e.target.getAttribute("data-key")); }
  });

  function labelFor(el) {
    var l = form.querySelector('label[for="' + el.id + '"]');
    return l ? l.firstChild.textContent.trim() : el.name;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (form.website.value) { note.textContent = "Thanks, message sent."; return; }
    var data = new URLSearchParams();
    var lines = [];
    var els = form.elements;
    var i;
    for (i = 0; i < els.length; i++) {
      var el = els[i];
      if (!el.name || el.disabled || el.name === "website") { continue; }
      if (el.type === "radio" && !el.checked) { continue; }
      data.append(el.name, el.value);
      if (el.value) { lines.push((el.name === "type" ? "I'm writing about" : labelFor(el)) + ": " + el.value); }
    }
    var endpoint = form.getAttribute("data-endpoint");
    if (!endpoint) {
      window.location.href = "mailto:" + form.getAttribute("data-email") +
        "?subject=" + encodeURIComponent("Website: " + form.elements.type.value) +
        "&body=" + encodeURIComponent(lines.join("\n"));
      return;
    }
    send.disabled = true;
    note.textContent = "Sending...";
    fetch(endpoint, { method: "POST", mode: "no-cors", body: data }).then(function () {
      form.reset();
      choose("");
      msg.hidden = true;
      send.hidden = true;
      note.textContent = "Thanks, message sent. You will hear back by email.";
    }, function () {
      note.textContent = "Could not send. Please email " + form.getAttribute("data-email") + " instead.";
    }).then(function () { send.disabled = false; });
  });
})();
