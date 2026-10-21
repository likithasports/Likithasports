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

The hero fills the page content width on desktop, with a responsive image stage and overlaid introduction. On phones, the introduction sits above a shorter image stage and controls wrap within the available width. The hero carousel uses dashboard-managed slides (one to six), rotates every six seconds, and provides previous/next buttons, slide selectors, keyboard arrows, touch swipes, and pause/play. It pauses on hover and in hidden browser tabs; focus entry or manual navigation stops rotation until Play is chosen. Reduced-motion users start with autoplay off and receive no transitions. The headline and enquiry actions remain stationary. With JavaScript disabled, the first slide stays visible and inactive controls stay hidden. Category filters and service links populate the WhatsApp enquiry composer. No enquiry is stored or sent automatically by this app.

Images are currently hosted at https://likithasports.com/. Contact details follow the existing website. No additional certification claims or project statistics have been added; the supplied logo is displayed as provided.

## Interactive service catalogue

The shared service catalogue in `catalog.py` renders all nine homepage service cards, individual pages at `/services/<slug>`, and JSON responses at `/api/services`. The catalogue API accepts `q` and `category` (`all`, `court`, `field`, `facility`). Unknown API categories return 400; unknown services return 404.

Homepage search combines terms with the selected category, updates the result count, supports an empty state and reset, and retains filters in the URL. Server-rendered query results and detail links work without JavaScript. Service pages preselect the matching enquiry option. Expandable FAQs use native HTML details. Cards animate into view when motion preferences allow it. Customer accounts and bookings are not included. An owner content dashboard is available at `/dashboard`.

## Content dashboard

`/dashboard` provides password-protected editing for homepage text, service entries and carousel slides. Images (PNG/JPEG/WebP, up to 2 MB and 20 megapixels) are validated server-side and stored in a private Vercel Blob store. Only website images are delivered through the public `/media/<opaque-id>` route. Service visibility, service addition/removal and slide reordering are supported. Changes affect the public pages after Publish.

`BLOB_READ_WRITE_TOKEN` is automatically supplied by the connected `likitha-sports-content` Vercel Blob store. Do not commit tokens. There is no production filesystem persistence or client-only persistence. Published content is stored as immutable timestamped JSON versions; reads select the latest version. Prior versions are retained. Publishing checks the editor revision to detect an already-published update. Concurrent publishes that start at exactly the same time may both be retained, with the newest version taking effect.

### Owner setup

First-time setup at `/dashboard/setup` is permitted **only on a Preview deployment protected by Vercel Authentication**, or in explicit local test mode. Production rejects the setup endpoint. The setup deployment must never be made public or have Deployment Protection disabled. The first successful setup stores a PBKDF2-SHA256 password hash and random signing key in private Blob storage; subsequent setup attempts are refused atomically by a non-overwriting object creation. After setup, sign in at the production `/dashboard` URL with the password you chose.

The dashboard uses signed eight-hour HttpOnly/SameSite=Strict cookies, Secure cookies on Vercel, origin checks and session-specific CSRF tokens on writes. Login attempts are rate-limited per IP and 15-minute bucket in persistent storage. Signing out clears the browser cookie. Do not use shared computers without signing out.

Content editing is intended for a small owner-managed site. There is one admin password, no customer registration and no public upload endpoint. All write endpoints require admin authentication except the protected first-time setup flow.

### Checks

Run `python -m unittest discover -s tests -v`. Tests use an isolated temporary storage adapter enabled through `CMS_TEST_DIR`; the adapter is ignored on Vercel. The production app always uses Vercel Blob. `CMS_DEV_SETUP=1` is a local testing option and is not deployed.

## Tailwind CSS

Tailwind CSS v4 is compiled with the CLI and loaded by the homepage, service pages and content dashboard. Python remains the application runtime. Prefixed utilities (`tw:flex`, `tw:gap-3`) avoid collisions with existing CSS; Preflight is omitted to preserve the current design. Brand theme utilities include `tw:text-brand-navy` and `tw:bg-brand-green`.

```sh
npm ci
npm run build:css
# Or rebuild automatically while editing Python templates:
npm run dev:css
```

Use complete, literal utility class names in `app.py` or `dashboard.py` so the scanner can detect them. Add other template paths with `@source` in `styles/tailwind.css` as needed. Run `npm run build:css` and commit the generated `assets/tailwind.css` after changing classes or theme settings. The committed CSS is explicitly served by Vercel's static builder, so the existing Python deployment does not need Node.js or a runtime CDN. Local Python/Gunicorn serves the same CSS path. Bump the stylesheet query version in both templates when updating the compiled stylesheet for cache invalidation.

### Operator-managed login reset

`CMS_ADMIN_CREDENTIALS` is an optional server-only Secret configuration containing `username`, a 16-byte hexadecimal `salt`, the existing PBKDF2-SHA256 `password` hash (600,000 iterations), and a fresh 32-byte hexadecimal session `key`. Set it through Vercel environment configuration, never in source files. When present, this credential record takes precedence over the legacy Blob login and requires both username and password. A new key invalidates existing sessions on the updated deployment. Malformed configuration fails closed. No content or uploaded images are deleted. Without this variable, the original password-only setup/login continues to work. Scope the reset to the intended environment/branch and deploy again to apply it; existing immutable deployments retain their earlier configuration. Removing the variable re-enables the legacy Blob credentials.
