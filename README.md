# Likitha Sports

Responsive sports infrastructure website, served by a Python WSGI application.

## Run locally

```sh
python -m pip install -r requirements.txt
python app.py
```

Visit http://localhost:8000. For production:

```sh
gunicorn app:app --bind 0.0.0.0:${PORT:-8000}
```

## Features

- Three-slide landing carousel with manual controls, pause and reduced-motion support
- Service category filters and enquiry selection
- Construction process and expandable FAQs
- WhatsApp enquiry composer; visitors review and send in WhatsApp
- Responsive navigation and contact links
- GET/HEAD support, health endpoint at `/healthz`, appropriate 404/405 responses

## Deployment

Render Python web service, branch `main`, build command `pip install -r requirements.txt`, start command `gunicorn app:app --bind 0.0.0.0:$PORT`. No database or secrets are required.

Content and images use https://likithasports.com/ (reviewed 18 October 2026). Images currently load from that existing website. Business contact details follow its current published contact information. Additional service enquiries reflect the owner's supplied service list. No certifications, warranty periods, testimonials or project statistics are implied. Competitor references reviewed for information architecture: https://gallantsports.in/ and https://pacecourt.com/. No competitor copy or imagery is included.
