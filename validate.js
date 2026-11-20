const {fail} = require('./storage');
const {sections, categories} = require('./pages');
function text(value, label, limit) {
  if (typeof value !== 'string' || !value.trim() || value.trim().length > limit) fail(label + ' must contain 1–' + limit + ' characters.');
  return value.trim();
}
function image(value, required = false) {
  if (!value && !required) return null;
  if (typeof value !== 'string' || !/^(?:\/media\/[a-f0-9]{32}\.(?:png|jpg|webp)|[\w-]+\.(?:jpg|png|webp|jpeg))$/.test(value)) fail('Choose a valid website image.');
  return value;
}
function array(value, min, max, label) {
  if (!Array.isArray(value) || value.length < min || value.length > max) fail('Invalid ' + label + ' count.');
  return value;
}
module.exports = function validate(raw) {
  const hero = raw.hero || {};
  const slugs = new Set();
  const services = array(raw.services, 1, 30, 'service').map(s => {
    if (!s || typeof s.slug !== 'string' || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(s.slug) || s.slug.length > 70 || slugs.has(s.slug)) fail('Choose a unique service URL.');
    slugs.add(s.slug);
    if (!Object.hasOwn(categories, s.category) || typeof s.published !== 'boolean') fail('Choose a service category and visibility.');
    return {slug:s.slug, category:s.category, published:s.published, title:text(s.title,'Service title',100), summary:text(s.summary,'Summary',300), prompt:text(s.prompt,'Guidance',300), image:image(s.image), scope:array(s.scope,1,6,'scope item').map(v => text(v,'Scope',180))};
  });
  if (!services.some(s => s.published)) fail('Keep at least one service published.');
  const slides = array(raw.slides,1,6,'slide').map(s => ({title:text(s?.title,'Slide title',100), category:text(s.category,'Category',70), alt:text(s.alt,'Description',150), image:image(s.image,true)}));
  const galleries = {};
  for (const page of Object.keys(sections)) {
    galleries[page] = array(raw.galleries?.[page] ?? [],0,100,'gallery photo').map(p => ({image:image(p?.image,true), alt:text(p.alt,'Photo description',150)}));
  }
  const aboutCards = array(raw.aboutCards,6,6,'About Us card').map(card => ({
    title: text(card?.title,'Name',100),
    designation: card.designation ? text(card.designation,'Designation',150) : '',
    description: text(card?.description,'Profile paragraph',5000),
    image: image(card.image),
    alt: card.alt ? text(card.alt,'Photo caption',150) : ''
  }));
  return {logo:image(raw.logo), aboutCards, galleries, services, slides, hero:{line1:text(hero.line1,'Headline',60), line2:text(hero.line2,'Headline',60), description:text(hero.description,'Description',300)}};
};
