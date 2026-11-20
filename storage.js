const fs = require('node:fs/promises');
const path = require('node:path');
const blob = require('@vercel/blob');
const {defaults} = require('./pages');
const prefix = 'likitha-cms/';
const directory = !process.env.VERCEL && process.env.CMS_DATA_DIR;
function fail(message, status = 400) { throw Object.assign(new Error(message), {status}); }
function requireStorage() {
  if (!directory && !process.env.BLOB_READ_WRITE_TOKEN) fail('Content storage is not connected.', 503);
}
async function read(key) {
  requireStorage();
  if (directory) {
    try { return await fs.readFile(path.join(directory, key)); }
    catch (e) { if (e.code === 'ENOENT') return null; throw e; }
  }
  const item = await blob.get(prefix + key, {access: 'private'});
  return item ? Buffer.from(await new Response(item.stream).arrayBuffer()) : null;
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
  await blob.put(prefix + key, body, {access: 'private', contentType, addRandomSuffix: false, allowOverwrite: false, cacheControlMaxAge: 60});
}
async function list(key) {
  requireStorage();
  if (directory) {
    try { return (await fs.readdir(path.join(directory, key))).filter(n => n.endsWith('.json')).map(n => key + n); }
    catch (e) { if (e.code === 'ENOENT') return []; throw e; }
  }
  const keys = [];
  let cursor;
  do {
    const batch = await blob.list({prefix: prefix + key, cursor});
    keys.push(...batch.blobs.map(b => b.pathname.slice(prefix.length)));
    cursor = batch.hasMore ? batch.cursor : undefined;
  } while (cursor);
  return keys;
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
    return {...defaults, ...saved};
  } catch (e) { if (strict) fail('Content storage could not be read.', 503); return defaults; }
}
module.exports = {read, write, list, content, fail};
