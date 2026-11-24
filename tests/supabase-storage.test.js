const {test} = require('node:test');
const assert = require('node:assert/strict');
const {createServer} = require('node:http');

test('Supabase adapter stores JSON and media using the existing function contract', async t => {
  const objects = new Map();
  const server = createServer(async (req, res) => {
    try {
      assert.equal(req.method, 'POST');
      assert.equal(req.headers['x-cms-secret'], 'local-test-token');
      const chunks = [];
      for await (const chunk of req) chunks.push(chunk);
      const {action, path, body, content_type: type} = JSON.parse(Buffer.concat(chunks));
      const entry = objects.get(path);
      res.setHeader('Content-Type', 'application/json');
      if (action === 'list') {
        res.end(JSON.stringify({paths: [...objects.keys()].filter(key => key.startsWith(path))}));
      } else if (action === 'read' && path.startsWith('media/') && entry) {
        res.setHeader('Content-Type', entry.type);
        res.end(Buffer.from(entry.body, 'base64'));
      } else if (action === 'read') {
        res.end(JSON.stringify(entry ? {body: entry.body} : {missing: true}));
      } else if (action === 'write') {
        res.statusCode = entry ? 409 : 201;
        if (!entry) objects.set(path, {body, type});
        res.end('{}');
      } else {
        throw Error('Unexpected action');
      }
    } catch (error) {
      res.statusCode = 500;
      res.end(JSON.stringify({error: error.message}));
    }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => server.close(resolve)));
  delete process.env.CMS_DATA_DIR;
  delete process.env.BLOB_READ_WRITE_TOKEN;
  process.env.SUPABASE_CMS_URL = 'http://127.0.0.1:' + server.address().port;
  process.env.SUPABASE_CMS_SECRET = 'local-test-token';
  const storage = require('../storage');

  const published = 'published/0001.json';
  assert.equal(await storage.read(published), null);
  await storage.write(published, '{"revision":"first"}');
  assert.deepEqual(await storage.list('published/'), [published]);
  assert.equal((await storage.content(true)).revision, 'first');
  await assert.rejects(storage.write(published, '{}'), {status: 409});

  const media = 'media/abcdef0123456789abcdef0123456789.webp';
  const bytes = Buffer.from([0, 255, 10, 193]);
  await storage.write(media, bytes, 'image/webp');
  assert.deepEqual(await storage.read(media), bytes);
});
