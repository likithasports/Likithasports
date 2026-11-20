# Likitha Sports

Node.js serves the public website, service catalogue, private content dashboard and uploaded media. Use Node.js 22 or 24.

## Run and deploy

From the repository root run `npm ci`, `npm run build`, then `npm start`. The server listens on all interfaces using the host's `PORT` (default 8000). For a hosting control panel, select Node.js, use the repository root as the app directory and set the startup file to `server.js`. The health check is `/healthz`.

The Vercel project uses the same request handler through `api/site.js`. The dashboard is at `/dashboard`. Existing published content, private media keys and administrator credential records retain their original formats.

## Dashboard storage

Use the existing private Vercel Blob store via the server environment variable `BLOB_READ_WRITE_TOKEN`. If the dashboard uses an operator-managed account, configure the existing `CMS_ADMIN_CREDENTIALS` secret on the new host as well. Serve production over HTTPS and set `NODE_ENV=production`. Never put credentials in the repository. Without storage, public pages use the built-in catalogue.

For a separate installation with a persistent volume, set `CMS_DATA_DIR` to a private directory outside the web root. For initial local setup, bind access to a trusted environment, set `CMS_DEV_SETUP=1`, start the app and open `/dashboard/setup`. Turn off local setup before publishing. The filesystem adapter is disabled on Vercel. For first-time setup on a Vercel preview, enable Vercel Authentication for that preview before setting the preview-only variable CMS_PRIVATE_SETUP=1.

## Tests

`npm test` runs the public route, login, image upload, authenticated publish and gallery checks against a temporary directory.
