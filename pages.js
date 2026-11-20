const path = require('node:path');
const nunjucks = require('nunjucks');
const defaults = require('./views/defaults.json');
const env = nunjucks.configure(path.join(__dirname, 'views'), {autoescape: true});
const categories = {court: 'Courts', field: 'Turfs & tracks', facility: 'Facilities'};
const sections = {'about-us': 'About us', projects: 'Projects', clients: 'Clients', testimonials: 'Testimonials'};
function imageUrl(value) {
  return value.startsWith('/media/') ? value : 'https://likithasports.com/assets/home/' + value;
}
env.addFilter('imageUrl', imageUrl);
env.addFilter('pad', n => String(n).padStart(2, '0'));

function render(url, data) {
  const pathname = url.pathname.replace(/\/+$/, '');
  const query = (url.searchParams.get('q') || '').slice(0, 100);
  const terms = query.toLowerCase().trim().split(/\s+/);
  let category = url.searchParams.get('category') || 'all';
  if (category !== 'all' && !Object.hasOwn(categories, category)) {
    if (pathname === '/api/services') return {status: 400, json: {error: 'Unknown category'}};
    category = 'all';
  }
  const published = data.services.filter(s => s.published !== false);
  const services = published.map(s => {
    const search = [s.title, s.summary, categories[s.category], ...s.scope].join(' ').toLowerCase();
    return {...s, search, matches: (category === 'all' || category === s.category) && terms.every(t => search.includes(t))};
  });
  const matches = published.filter((_, i) => services[i].matches);
  if (pathname === '/api/services') return {json: {services: matches, count: matches.length}};
  const section = pathname.slice(1);
  const detail = services.find(s => pathname === '/services/' + s.slug);
  const isSection = Object.hasOwn(sections, section);
  if (pathname && !detail && !isSection) return {status: 404, text: 'Page not found'};
  const slides = data.slides.map(s => ({...s, image: imageUrl(s.image)}));
  const related = detail ? services.filter(s => s !== detail).sort((a,b) =>
    Number(b.category === detail.category) - Number(a.category === detail.category)).slice(0,3) : [];
  const html = env.render('home.html', {
    hero: data.hero, slides, slidesJson: JSON.stringify(slides).replaceAll('<', '\\u003c'),
    logo: data.logo ? imageUrl(data.logo) : '/logo.png?v=2', categories, services, query, category,
    count: matches.length, detail, selected: detail?.slug, related,
    number: String(services.indexOf(detail) + 1).padStart(2, '0'),
    section: isSection ? section + '.html' : null, title: detail?.title || sections[section],
    aboutCards: data.aboutCards, photos: data.galleries?.[section] || [], hasImages: services.some(s => s.image)
  });
  return {html};
}
function verify() {
  for (const route of ['/', ...Object.keys(sections).map(s => '/' + s), ...defaults.services.map(s => '/services/' + s.slug)]) {
    if (!render(new URL(route, 'http://localhost'), defaults).html.includes('</html>')) throw Error('Invalid template ' + route);
  }
}
module.exports = {render, verify, defaults, sections, categories};
