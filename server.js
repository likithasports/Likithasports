const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const pages = require('./pages');
const cms = require('./cms');
const storage = require('./storage');
const dashboard = fs.readFileSync(path.join(__dirname, 'views/dashboard.html'));
async function route(req, res) {
  const url = new URL(req.url, 'http://localhost');
  const pathname = url.pathname;
  if (pathname.startsWith('/api/admin/') || pathname.startsWith('/media/')) return cms.handle(req,res,pathname);
  if (!['GET','HEAD'].includes(req.method)) return {status:405, allow:'GET, HEAD'};
  if (/^\/dashboard(?:\/(?:setup|images|homepage|about-us|team|projects|clients|testimonials|services|carousel))?\/?$/.test(pathname)) {
    res.setHeader('Cache-Control','no-store');
    res.setHeader('X-Robots-Tag','noindex, nofollow');
    res.setHeader('X-Frame-Options','DENY');
    res.setHeader('Referrer-Policy','no-referrer');
    res.setHeader('Content-Security-Policy',"default-src 'self'; img-src 'self' https://likithasports.com data: blob:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'");
    return {bytes:dashboard,type:'text/html; charset=utf-8'};
  }
  if (pathname === '/healthz') return {json:{status:'ok'}};
  if (pathname === '/favicon.ico') return {status:204};
  if (pathname === '/robots.txt') return {text:`User-agent: *\nAllow: /\nSitemap: ${pages.publicOrigin}/sitemap.xml\n`};
  if (pathname === '/sitemap.xml') return {
    text: pages.sitemap(await storage.content()),
    type: 'application/xml; charset=utf-8'
  };
  const servicePhoto = pathname.slice('/service-photos/'.length);
  if (pathname.startsWith('/service-photos/') && pages.servicePhotos.has(servicePhoto)) {
    res.setHeader('Cache-Control','public, max-age=86400');
    return {
      bytes: await fs.promises.readFile(path.join(__dirname, 'assets', 'service-photos', servicePhoto)),
      type: 'image/webp'
    };
  }
  if (pathname === '/logo.png') {
    res.setHeader('Cache-Control','public, max-age=86400');
    return {bytes:await fs.promises.readFile(path.join(__dirname,'assets/logo-transparent.png')),type:'image/png'};
  }
  return pages.render(url,await storage.content());
}
async function handler(req,res) {
  res.setHeader('X-Content-Type-Options','nosniff');
  res.setHeader('X-Frame-Options','SAMEORIGIN');
  res.setHeader('Referrer-Policy','strict-origin-when-cross-origin');
  let result;
  try { result = await route(req,res); }
  catch (error) { result = {status:error.status || 503,json:{error:error.status ? error.message : 'The service could not complete this request.'}}; }
  if (result.allow) res.setHeader('Allow',result.allow);
  const body = result.bytes ?? Buffer.from(result.html ?? result.text ?? (result.json ? JSON.stringify(result.json) : ''));
  res.setHeader('Content-Type',result.type ?? (result.html ? 'text/html; charset=utf-8' : result.json ? 'application/json; charset=utf-8' : 'text/plain; charset=utf-8'));
  res.setHeader('Content-Length',body.length);
  res.statusCode = result.status || 200;
  res.end(req.method === 'HEAD' ? undefined : body);
}
module.exports = handler;
if (require.main === module) http.createServer(handler).listen(Number(process.env.PORT || 8000),'0.0.0.0');
