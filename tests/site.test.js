const {test} = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');

test('website, dashboard, authenticated publishing and uploaded media', async t => {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'likitha-'));
  process.env.CMS_DATA_DIR = directory;
  process.env.CMS_DEV_SETUP = '1';
  delete process.env.CMS_ADMIN_CREDENTIALS;
  delete process.env.VERCEL;
  delete process.env.NODE_ENV;
  const server = http.createServer(require('../server'));
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(async () => { await new Promise(resolve => server.close(resolve)); await fs.rm(directory,{recursive:true}); });
  const base = 'http://127.0.0.1:' + server.address().port;
  let cookie, csrf;
  const post = (endpoint,data) => fetch(base+'/api/admin/'+endpoint,{method:'POST',headers:{
    'content-type':'application/json', origin:base, cookie:cookie || '', 'x-csrf-token':csrf || ''
  },body:JSON.stringify(data)});
  for (const endpoint of ['/','/dashboard','/about-us','/projects','/clients','/testimonials','/services/athletic-track','/logo.png','/healthz']) {
    assert.equal((await fetch(base+endpoint)).status,200,endpoint);
  }
  assert.equal((await fetch(base+'/services/missing')).status,404);
  assert.equal((await fetch(base+'/api/services?category=unknown')).status,400);
  assert.equal((await (await fetch(base+'/api/services?q=pool')).json()).count,1);
  assert.equal((await fetch(base+'/api/admin/content')).status,401);
  const sitemap = await fetch(base+'/sitemap.xml');
  assert.match(sitemap.headers.get('content-type'), /^application\/xml/);
  assert.match(await sitemap.text(), /<loc>https:\/\/www\.likithasports\.in\/services\/athletic-track<\/loc>/);
  assert.match(await (await fetch(base+'/robots.txt')).text(), /Sitemap: https:\/\/www\.likithasports\.in\/sitemap\.xml/);
  for (const name of ['basketball.webp','tennis.webp','football-truf.webp','pickleball.webp']) {
    const asset = await fetch(base+'/service-photos/'+name);
    assert.equal(asset.status,200);
    assert.equal(asset.headers.get('content-type'),'image/webp');
  }
  const password = require('node:crypto').randomUUID();
  assert.equal((await post('setup',{password})).status,201);
  const login = await post('login',{password});
  assert.equal(login.status,200);
  cookie = login.headers.get('set-cookie').split(';')[0];
  csrf = (await login.json()).csrf;
  const data = await (await fetch(base+'/api/admin/content',{headers:{cookie}})).json();
  assert.equal((await post('upload',{data:Buffer.from('invalid').toString('base64')})).status,400);
  const file = await fs.readFile(path.join(__dirname,'../assets/logo-transparent.png'));
  const upload = await post('upload',{data:file.toString('base64')});
  assert.equal(upload.status,201);
  const {url} = await upload.json();
  assert.deepEqual(Buffer.from(await (await fetch(base+url)).arrayBuffer()),file);
  const projectUpload = await post('upload',{data:file.toString('base64'),destination:'projects'});
  assert.equal(projectUpload.status,201);
  const projectImage = await projectUpload.json();
  const projectBytes = Buffer.from(await (await fetch(base+projectImage.url)).arrayBuffer());
  const {width,height} = await require('sharp')(projectBytes).metadata();
  assert.deepEqual([width,height],[500,500]);
  data.galleries.projects = [{image:url,alt:'Published project'}];
  data.projects = [{title:'Shuttle Cort',description:'Court project',photos:[
    {image:projectImage.url,alt:'First court photo'}, {image:url,alt:'Second court photo'}
  ]}];
  assert.equal(data.aboutCards.length,6);
  data.aboutCards[3] = {image:url,alt:'Court build',title:'Our team',designation:'Coach',description:'Site team'};
  data.hero.line1 = 'Published headline';
  const publish = await post('content',data);
  assert.equal(publish.status,200);
  assert.equal((await post('content',data)).status,409);
  const home = await (await fetch(base+'/')).text();
  assert.match(home, /Published headline/);
  assert.match(home, /data-home-project-slideshow tabindex/);
  assert.match(home, /Shuttle Court/);
  assert.match(home, /rel="canonical" href="https:\/\/www\.likithasports\.in\/"/);
  const projects = await (await fetch(base+'/projects')).text();
  assert.match(projects, /Published project/);
  assert.match(projects, /Police Sports Complex, Rajahmundry/);
  assert.match(await (await fetch(base+'/clients')).text(), /SP Office, Rajahmundry/);
  const about = await (await fetch(base+'/about-us')).text();
  assert.ok(about.includes(url) && about.includes('<h3>Our team</h3>') && about.includes('Site team'));
  assert.match(about, /profile-designation">Coach</);
  assert.equal((about.match(/<details class="profile-bio">/g) || []).length,4);
  const saved = await (await fetch(base+'/api/admin/content',{headers:{cookie}})).json();
  assert.deepEqual(saved.aboutCards[3],data.aboutCards[3]);
  assert.equal(saved.aboutProfileIndexes.length,4);
  assert.equal(saved.aboutProfileIndexes[0],3);
  assert.equal((await post('logout',{})).status,200);
});
