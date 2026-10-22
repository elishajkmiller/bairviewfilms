/**
 * Receives the contact form on bairviewfilms.com/contact.html.
 * Writes to the Google Sheet that holds the sign-ups (bound to it, or set SHEET_ID).
 * Appends one row per submission and emails NOTIFY_EMAIL.
 *
 * Deploy: Deploy > New deployment > Web app, Execute as: Me, Who has access: Anyone.
 * Put the /exec URL in content.json (site.form_endpoint), run python3 build.py, push.
 * After changing this file, Deploy > Manage deployments > edit > New version.
 */
var NOTIFY_EMAIL = "kalebfobair@gmail.com";
// Leave empty when the script is opened from the sheet (Extensions > Apps Script); set it for a standalone script.
var SHEET_ID = "";
var SHEET_NAME = "Sign-ups";
var FIELDS = [
  ["name", "Name"], ["email", "Email"], ["type", "Type"],
  ["project_type", "Project type"], ["timeline", "Timeline"], ["budget", "Budget"], ["heard", "Heard about me"],
  ["role", "Role"], ["link", "Reel or portfolio"], ["location", "Location"],
  ["pow_role", "POW417 involvement"], ["outlet", "Outlet or venue"], ["event_date", "Date"],
  ["message", "Message"]
];

function doPost(e) {
  var p = e.parameter || {};
  if (p.website) { return ok_(); } // honeypot
  if (!p.name || !p.email || !p.type) { return ok_(); }

  var row = [new Date()];
  var lines = [];
  FIELDS.forEach(function (f) {
    var v = String(p[f[0]] || "").slice(0, 4000);
    row.push(safe_(v));
    if (v) { lines.push(f[1] + ": " + v); }
  });

  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var ss = SHEET_ID ? SpreadsheetApp.openById(SHEET_ID) : SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(["Received"].concat(FIELDS.map(function (f) { return f[1]; })));
      sheet.setFrozenRows(1);
    }
    sheet.appendRow(row);
  } finally {
    lock.releaseLock();
  }

  MailApp.sendEmail({
    to: NOTIFY_EMAIL,
    replyTo: String(p.email).slice(0, 200),
    subject: "Bairview site: " + p.type + " from " + String(p.name).slice(0, 80),
    body: lines.join("\n")
  });
  return ok_();
}

function doGet() { return ok_(); }

function ok_() {
  return ContentService.createTextOutput("ok");
}

// A cell that starts with = + - @ would run as a formula in Sheets.
function safe_(v) {
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}
