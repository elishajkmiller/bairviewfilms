# Contact form backend

`Code.gs` is the Google Apps Script that receives the form on `contact.html`, adds a row to the sign-up sheet and emails the owner.

1. Open the sign-up Google Sheet, Extensions > Apps Script, paste `Code.gs`.
2. Deploy > New deployment > Web app. Execute as: Me. Who has access: Anyone.
3. Authorize when asked (it needs the sheet and mail).
4. Copy the `/exec` URL into `content.json` as `site.form_endpoint`, run `python3 build.py`, commit and push.

Until the URL is set, the form opens the visitor's mail app instead.
