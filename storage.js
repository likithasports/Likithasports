const fs = require('node:fs/promises');
const path = require('node:path');
const blob = require('@vercel/blob');
const {defaults} = require('./pages');
const prefix = 'likitha-cms/';
const directory = !process.env.VERCEL && process.env.CMS_DATA_DIR;
const supabaseUrl = process.env.SUPABASE_CMS_URL;
const supabaseSecret = process.env.SUPABASE_CMS_SECRET;
const supabase = !directory && supabaseUrl && supabaseSecret;
function fail(message, status = 400) { throw Object.assign(new Error(message), {status}); }
function requireStorage() {
  if (!directory && !supabase && !process.env.BLOB_READ_WRITE_TOKEN) fail('Content storage is not connected.', 503);
}
async function supabaseRequest(action, key, body, contentType) {
  const media = key.startsWith('media/');
  const payload = {action, path: key};
  if (action === 'write') {
    payload.body = media ? Buffer.from(body).toString('base64') : JSON.parse(body);
    payload.content_type = contentType;
  }
  const response = await fetch(supabaseUrl, {
    method: 'POST',
    headers: {'Content-Type': 'application/json', 'X-Cms-Secret': supabaseSecret},
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(10000),
    redirect: 'error'
  }).catch(() => fail('Supabase storage is unavailable. Please retry.', 503));
  if (response.status === 409) fail('Content already exists.', 409);
  if (!response.ok) fail('Supabase storage is unavailable. Please retry.', 503);
  if (action === 'write') return;
  if (media && response.headers.get('Content-Type')?.startsWith('image/')) {
    return Buffer.from(await response.arrayBuffer());
  }
  const result = await response.json();
  if (action === 'list') return result.paths;
  return result.missing ? null : Buffer.from(JSON.stringify(result.body));
}
async function read(key) {
  requireStorage();
  if (directory) {
    try { return await fs.readFile(path.join(directory, key)); }
    catch (e) { if (e.code === 'ENOENT') return null; throw e; }
  }
  if (supabase) {
    const bytes = await supabaseRequest('read', key);
    if (bytes || !process.env.BLOB_READ_WRITE_TOKEN) return bytes;
  }
  const item = await blob.get(prefix + key, {access: 'private'});
  if (!item) return null;
  const bytes = Buffer.from(await new Response(item.stream).arrayBuffer());
  if (supabase && /^(published|media)\//.test(key)) {
    const mime = {jpg:'image/jpeg', png:'image/png', webp:'image/webp'}[key.split('.').at(-1)] || 'application/json';
    // A failed compatibility copy must not stop an existing upload from loading.
    await supabaseRequest('write', key, bytes, mime).catch(() => {});
  }
  return bytes;
}
async function write(key, body, contentType = 'application/json') {
  requireStorage();
  if (directory) {
    const dest = path.join(directory, key);
    await fs.mkdir(path.dirname(dest), {recursive: true, mode: 0o700});
    const temp = dest + '.' + require('node:crypto').randomUUID() + '.tmp';
    await fs.writeFile(temp, body, {flag: 'wx', mode: 0o600});
    try { await fs.link(temp, dest); } finally { await fs.unlink(temp); }
    return;
  }
  if (supabase) return supabaseRequest('write', key, body, contentType);
  await blob.put(prefix + key, body, {access: 'private', contentType, addRandomSuffix: false, allowOverwrite: false, cacheControlMaxAge: 60});
}
async function list(key) {
  requireStorage();
  if (directory) {
    try { return (await fs.readdir(path.join(directory, key))).filter(n => n.endsWith('.json')).map(n => key + n); }
    catch (e) { if (e.code === 'ENOENT') return []; throw e; }
  }
  const keys = supabase ? await supabaseRequest('list', key) : [];
  if (supabase && !process.env.BLOB_READ_WRITE_TOKEN) return keys;
  let cursor;
  do {
    const batch = await blob.list({prefix: prefix + key, cursor});
    keys.push(...batch.blobs.map(b => b.pathname.slice(prefix.length)));
    cursor = batch.hasMore ? batch.cursor : undefined;
  } while (cursor);
  return [...new Set(keys)];
}
async function content(strict = false) {
  try {
    const latest = (await list('published/')).sort().at(-1);
    if (!latest) return defaults;
    const saved = JSON.parse(await read(latest));
    if (!saved.aboutCards) {
      const photos = saved.galleries?.['about-us'] || [];
      saved.aboutCards = defaults.aboutCards.map((card, index) => ({...card, ...photos[index]}));
      saved.galleries = {...defaults.galleries, ...saved.galleries, 'about-us': photos.slice(6)};
    }
    for (const project of saved.projects || []) {
      if (project.title === 'Shuttle Cort') project.title = 'Shuttle Court';
    }
    const volleyball = saved.services?.find(service => service.slug === 'beach-volleyball');
    if (volleyball?.title === 'Beach volleyball') volleyball.title = 'Volley Ball';
    if (saved.boardCards?.length === 6) {
      saved.boardCards = saved.boardCards.slice(0, 3);
    }
    return {...defaults, ...saved};
  } catch (e) { if (strict) fail('Content storage could not be read.', 503); return defaults; }
}
module.exports = {read, write, list, content, fail};
