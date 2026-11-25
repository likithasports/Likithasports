const path = require('node:path');
const nunjucks = require('nunjucks');
const defaults = require('./views/defaults.json');
const env = nunjucks.configure(path.join(__dirname, 'views'), {autoescape: true});
const categories = {court: 'Courts', field: 'Turfs & tracks', facility: 'Facilities'};
const sections = {'about-us': 'About us', team: 'Team', projects: 'Projects', clients: 'Clients', testimonials: 'Testimonials'};
const publicOrigin = 'https://www.likithasports.in';
const policeSportsComplex = {
  title: 'Police Sports Complex, Rajahmundry',
  client: 'SP Office, Rajahmundry',
  description: 'Sports infrastructure at the SP Office in Rajahmundry, Andhra Pradesh. The site includes an eight-layer synthetic court with fencing and floodlights, a floodlit clay tennis court, and three floodlit volleyball courts. It also includes an outdoor synthetic badminton court, two astro turf cricket pitches with floodlights, and a walking track with landscaped grounds.'
};
const servicePhotos = new Map([
  ['basketball.webp', {
    author: 'Sujaybagi',
    source: 'https://commons.wikimedia.org/wiki/File:BMSCE_Basket-ball_court_(Outdoor).jpg'
  }],
  ['tennis.webp', {
    author: 'Prince Roy',
    source: 'https://commons.wikimedia.org/wiki/File:Outdoor_Tennis_Court_at_THU_2008-5-3.jpg',
    license: 'https://creativecommons.org/licenses/by/2.0/'
  }],
  ['football-truf.webp', null],
  ['pickleball.webp', {
    author: 'Wikideas1',
    source: 'https://commons.wikimedia.org/wiki/File:Outdoor_pickleball_courts.jpg'
  }]
]);
function imageUrl(value) {
  if (servicePhotos.has(value)) return '/service-photos/' + value;
  return value.startsWith('/media/') ? value : 'https://www.likithasports.in/assets/home/' + value;
}
env.addFilter('imageUrl', imageUrl);
env.addFilter('pad', n => String(n).padStart(2, '0'));

function aboutProfileIndexes(cards) {
  const active = card => Boolean(card.image || card.designation);
  return cards.map((_, index) => index)
    .sort((a, b) => Number(active(cards[b])) - Number(active(cards[a])));
}

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
    return {...s, photoCredit: servicePhotos.get(s.image), search, matches: (category === 'all' || category === s.category) && terms.every(t => search.includes(t))};
  });
  const matches = published.filter((_, i) => services[i].matches);
  if (pathname === '/api/services') return {json: {services: matches, count: matches.length}};
  const section = pathname.slice(1);
  const detail = services.find(s => pathname === '/services/' + s.slug);
  const isSection = Object.hasOwn(sections, section);
  if (pathname && !detail && !isSection) return {status: 404, text: 'Page not found'};
  const slides = data.slides.map(s => ({...s, image: imageUrl(s.image), example: Boolean(servicePhotos.get(s.image))}));
  const related = detail ? services.filter(s => s !== detail).sort((a,b) =>
    Number(b.category === detail.category) - Number(a.category === detail.category)).slice(0,3) : [];
  const projectCards = [];
  if (!pathname || section === 'projects') {
    projectCards.push(...(data.projects || []).filter(project => project.photos.length));
    for (const photo of data.galleries?.projects || []) projectCards.push({photos:[photo]});
    while (section === 'projects' && projectCards.length < 15) projectCards.push({photos:[]});
  }
  const html = env.render('home.html', {
    canonical: publicOrigin + (pathname || '/'),
    hero: data.hero, slides, slidesJson: JSON.stringify(slides).replaceAll('<', '\\u003c'),
    logo: data.logo ? imageUrl(data.logo) : '/logo.png?v=2', categories, services, query, category,
    count: matches.length, detail, selected: detail?.slug, related,
    number: String(services.indexOf(detail) + 1).padStart(2, '0'),
    section: isSection ? section + '.html' : null, title: detail?.title || sections[section],
    revision: data.revision,
    intro: data.pageIntros?.[section] || defaults.pageIntros[section],
    entries: data.entries?.[section] || [],
    projectCards: pathname ? projectCards : projectCards.map(project => ({
      ...project,
      photos: project.photos.filter(photo => photo.image !== '/media/d18c50e38531292c38d4149074dbabe0.jpg')
    })).filter(project => project.photos.length),
    policeSportsComplex,
    aboutCards: aboutProfileIndexes(data.aboutCards).map(index => data.aboutCards[index]),
    teamDivisions: [
      {id:'management', title:'Management Team', cards:data.teamCards ?? defaults.teamCards},
      {id:'team', title:'Team', cards:data.staffCards ?? defaults.staffCards}
    ],
    photos: data.galleries?.[section] || [], hasImages: services.some(s => s.image)
  });
  return {html};
}
function verify() {
  for (const route of ['/', ...Object.keys(sections).map(s => '/' + s), ...defaults.services.map(s => '/services/' + s.slug)]) {
    if (!render(new URL(route, 'http://localhost'), defaults).html.includes('</html>')) throw Error('Invalid template ' + route);
  }
}
function sitemap(data) {
  const paths = ['/', ...Object.keys(sections).map(section => '/' + section)];
  paths.push(...data.services.filter(service => service.published !== false).map(service => '/services/' + service.slug));
  const entries = paths.map(route => `  <url><loc>${publicOrigin}${route}</loc></url>`).join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${entries}\n</urlset>\n`;
}
module.exports = {render, verify, defaults, sections, categories, publicOrigin, sitemap, servicePhotos, aboutProfileIndexes};
