# Likitha Sports

Responsive Python WSGI website using the supplied Likitha logo and its sampled colours: navy `#0B1E55`, green `#27BB36`, white `#FFFFFF`. The transparent logo is stored in `assets/logo-transparent.png` and served at `/logo.png`; the original uploaded source is unchanged.

## Run locally

```sh
python app.py
```

Visit http://localhost:8000. For Render, install requirements and run `gunicorn app:app --bind 0.0.0.0:$PORT`.

## Vercel

The checked-in `vercel.json` explicitly packages `app.py` with `@vercel/python` and sends application paths to the WSGI app. The logo is explicitly bundled as a static asset and routed separately. Python is pinned to 3.12 via `.python-version`. This working builder configuration overrides dashboard build settings. No environment secrets or database are required.

Routes: `/`, `/logo.png`, `/healthz`, `/robots.txt`; unknown routes return 404. GET and HEAD are supported; other methods return 405.

The three-slide carousel runs automatically every three seconds, has manual slide and pause controls, and pauses in hidden browser tabs. Category filters and service links populate the WhatsApp enquiry composer. No enquiry is stored or sent automatically by this app.

Images are currently hosted at https://likithasports.com/. Contact details follow the existing website. No additional certification claims or project statistics have been added; the supplied logo is displayed as provided.

## Interactive service catalogue

The shared service catalogue in `catalog.py` renders all nine homepage service cards, individual pages at `/services/<slug>`, and JSON responses at `/api/services`. The catalogue API accepts `q` and `category` (`all`, `court`, `field`, `facility`). Unknown API categories return 400; unknown services return 404.

Homepage search combines terms with the selected category, updates the result count, supports an empty state and reset, and retains filters in the URL. Server-rendered query results and detail links work without JavaScript. Service pages preselect the matching enquiry option. Expandable FAQs use native HTML details. Cards animate into view when motion preferences allow it. No accounts, bookings, database, or admin dashboard are included in this version.
