const crypto = require('node:crypto');
const derive = require('node:util').promisify(crypto.pbkdf2);
const sharp = require('sharp');
const store = require('./storage');
const validate = require('./validate');
const {aboutProfileIndexes} = require('./pages');
const {fail} = store;
const hex = n => crypto.randomBytes(n).toString('hex');
const hash = async (password, salt) => (await derive(password, Buffer.from(salt, 'hex'), 600000, 32, 'sha256')).toString('hex');
const sign = (payload, key) => crypto.createHmac('sha256', Buffer.from(key, 'hex')).update(payload).digest('hex');
function equal(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string') return false;
  const left = Buffer.from(a), right = Buffer.from(b);
  return left.length === right.length && crypto.timingSafeEqual(left, right);
}
async function admin() {
  if (process.env.CMS_ADMIN_CREDENTIALS === undefined) return JSON.parse(await store.read('auth/admin.json'));
  try {
    const r = JSON.parse(process.env.CMS_ADMIN_CREDENTIALS);
    if (typeof r.username === 'string' && r.username.length && r.username.length <= 100 &&
        /^[a-f0-9]{32}$/.test(r.salt) && /^[a-f0-9]{64}$/.test(r.key) && /^[a-f0-9]{64}$/.test(r.password)) return r;
  } catch {}
  fail('Dashboard sign-in configuration needs attention.', 503);
}
function session(req, record) {
  const match = /(?:^|;\s*)likitha_admin=([\w-]+)\.([a-f0-9]{64})(?:;|$)/.exec(req.headers.cookie || '');
  if (!match || !record || !equal(sign(match[1], record.key), match[2])) return null;
  try {
    const s = JSON.parse(Buffer.from(match[1], 'base64url').toString());
    return Number.isInteger(s.exp) && s.exp > Date.now()/1000 && typeof s.csrf === 'string' ? s : null;
  } catch { return null; }
}
function signedIn(req, res, record, status) {
  const csrf = hex(24);
  const payload = Buffer.from(JSON.stringify({exp: Math.floor(Date.now()/1000) + 28800, csrf})).toString('base64url');
  const secure = process.env.NODE_ENV === 'production' || process.env.VERCEL || req.socket.encrypted;
  res.setHeader('Set-Cookie', 'likitha_admin=' + payload + '.' + sign(payload, record.key) + '; Path=/; Max-Age=28800; HttpOnly; SameSite=Strict' + (secure ? '; Secure' : ''));
  return {status, json:{ok:true, csrf}};
}
async function body(req) {
  if (req.headers['content-type']?.split(';')[0] !== 'application/json') fail('Send JSON content.',415);
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 3*1024*1024) fail('The upload is too large.',413);
    chunks.push(chunk);
  }
  let data;
  try { data = JSON.parse(Buffer.concat(chunks).toString()); } catch { fail('Invalid JSON.'); }
  if (!data || typeof data !== 'object' || Array.isArray(data)) fail('Invalid request.');
  return data;
}
const setupAllowed = () => process.env.VERCEL_ENV === 'preview' && process.env.CMS_PRIVATE_SETUP === '1' || !process.env.VERCEL && process.env.NODE_ENV !== 'production' && !!process.env.CMS_DATA_DIR && process.env.CMS_DEV_SETUP === '1';
async function handle(req, res, path) {
  if (path.startsWith('/media/')) {
    if (!['GET','HEAD'].includes(req.method)) return {status:405, allow:'GET, HEAD'};
    const ext = /^\/media\/[a-f0-9]{32}\.(jpg|png|webp)$/.exec(path)?.[1];
    if (!ext) fail('Image not found.',404);
    const bytes = await store.read(path.slice(1));
    if (!bytes) fail('Image not found.',404);
    res.setHeader('Cache-Control','public, max-age=31536000, immutable');
    return {bytes, type:'image/' + (ext === 'jpg' ? 'jpeg' : ext)};
  }
  res.setHeader('Cache-Control','no-store');
  if (path === '/api/admin/status') {
    if (req.method !== 'GET') return {status:405, allow:'GET'};
    const record = await admin(), current = session(req,record);
    return {json:{configured:!!record, username_required:!!record?.username, authenticated:!!current, csrf:current?.csrf ?? null, setup_allowed:setupAllowed(), setup_url:record ? null : process.env.CMS_SETUP_URL || null}};
  }
  if (path === '/api/admin/content' && req.method === 'GET') {
    if (!session(req,await admin())) fail('Sign in to manage website content.',401);
    const content = await store.content(true);
    return {json:{...content, aboutProfileIndexes:aboutProfileIndexes(content.aboutCards)}};
  }
  if (req.method !== 'POST') return {status:405, allow:'POST'};
  let origin;
  try { origin = new URL(req.headers.origin); } catch {}
  if (!origin || !['http:','https:'].includes(origin.protocol) || origin.host !== req.headers.host) fail('This request must come from the dashboard.',403);
  const data = await body(req), record = await admin();
  if (path === '/api/admin/setup') {
    if (!setupAllowed()) fail('First-time setup requires a local setup session.',403);
    if (record) fail('An admin account already exists.',409);
    if (typeof data.password !== 'string' || data.password.length < 14 || data.password.length > 200) fail('Choose a password between 14 and 200 characters.');
    const created = {salt:hex(16),key:hex(32)};
    created.password = await hash(data.password,created.salt);
    try { await store.write('auth/admin.json',JSON.stringify(created)); } catch { fail('Setup could not be saved.',409); }
    return signedIn(req,res,created,201);
  }
  if (path === '/api/admin/login') {
    if (!record) fail('Configure the dashboard account first.',403);
    const address = (process.env.VERCEL && req.headers['x-vercel-forwarded-for']) || req.socket.remoteAddress || 'unknown';
    const id = crypto.createHash('sha256').update(address).digest('hex').slice(0,32);
    const prefix = 'login/' + id + '/' + Math.floor(Date.now()/900000) + '/';
    if ((await store.list(prefix)).length >= 10) fail('Try signing in again in 15 minutes.',429);
    await store.write(prefix + hex(8) + '.json','{}');
    if (typeof data.password !== 'string' || data.password.length > 200 || !equal(await hash(data.password,record.salt),record.password) || (record.username && !equal(data.username,record.username))) fail('The username or password is incorrect.',401);
    return signedIn(req,res,record,200);
  }
  const current = session(req,record);
  if (!current) fail('Sign in to manage website content.',401);
  if (!equal(req.headers['x-csrf-token'],current.csrf)) fail('Refresh the dashboard and try again.',403);
  if (path === '/api/admin/logout') {
    res.setHeader('Set-Cookie','likitha_admin=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict');
    return {json:{ok:true}};
  }
  if (path === '/api/admin/upload') {
    if (typeof data.data !== 'string' || !/^[A-Za-z0-9+/]+=*$/.test(data.data)) fail('Choose a valid image.');
    let bytes = Buffer.from(data.data,'base64');
    if (!bytes.length || bytes.length > 2*1024*1024) fail('Images must be under 2 MB.',413);
    let format;
    try {
      const image = sharp(bytes,{limitInputPixels:20000000,failOn:'warning'});
      ({format} = await image.metadata());
      if (!['png','jpeg','webp'].includes(format)) throw Error();
      if (data.destination === 'projects') {
        bytes = await image.rotate().resize(500,500,{fit:'contain',background:'#f4f6fa'}).webp({quality:88}).toBuffer();
        format = 'webp';
      } else {
        await image.stats();
      }
    } catch { fail('Choose a PNG, JPEG or WebP image under 20 megapixels.'); }
    const key = 'media/' + hex(16) + '.' + (format === 'jpeg' ? 'jpg' : format);
    await store.write(key,bytes,'image/'+format);
    return {status:201,json:{url:'/'+key}};
  }
  if (path === '/api/admin/content') {
    const old = await store.content(true);
    if (old.revision !== data.revision) fail('The website changed. Reload the latest content.',409);
    const content = validate({...old,...data});
    const revision = hex(16), updated_at = Math.floor(Date.now()/1000);
    const stamp = String(BigInt(Date.now()) * 1000000n).padStart(20,'0');
    await store.write('published/'+stamp+'-'+revision+'.json',JSON.stringify({...content,revision,updated_at}));
    return {json:{ok:true,revision,updated_at}};
  }
  fail('Endpoint not found.',404);
}
module.exports = {handle};
