# Likitha Sports

Responsive Python WSGI website using the supplied Likitha logo and its sampled colours: navy `#0B1E55`, green `#27BB36`, white `#FFFFFF`. The original logo is embedded losslessly in `app.py` and served at `/logo.png`.

## Run locally

```sh
python app.py
```

Visit http://localhost:8000. For Render, install requirements and run `gunicorn app:app --bind 0.0.0.0:$PORT`.

## Vercel

The checked-in `vercel.json` explicitly packages `app.py` with `@vercel/python` and sends all request paths to the WSGI app. Python is pinned to 3.12 via `.python-version`. This working builder configuration overrides dashboard build settings. No environment secrets or database are required.

Routes: `/`, `/logo.png`, `/healthz`, `/robots.txt`; unknown routes return 404. GET and HEAD are supported; other methods return 405.

The three-slide carousel runs automatically every three seconds, has manual slide and pause controls, and pauses in hidden browser tabs. Category filters and service links populate the WhatsApp enquiry composer. No enquiry is stored or sent automatically by this app.

Images are currently hosted at https://likithasports.com/. Contact details follow the existing website. No additional certification claims or project statistics have been added; the supplied logo is displayed as provided.
