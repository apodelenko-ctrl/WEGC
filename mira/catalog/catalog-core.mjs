/** Pure client-side catalogue helpers. No network, no personal-data collection. */
export const PAGE_SIZE = 24;
export const MAX_SELECTION = 12;
export function normalize(value) {
  return String(value ?? '').normalize('NFKC').toLocaleLowerCase('ru').replace(/ё/g,'е').trim();
}
export function validateCatalogue(data) {
  if (data?.schemaVersion !== 1 || data.mode !== 'public_research' || !Array.isArray(data.projects) || !data.projects.length) throw new Error('Каталог имеет некорректный формат.');
  const ids = new Set();
  for (const p of data.projects) {
    if (!/^[a-z0-9-]{1,180}$/.test(p.id) || typeof p.name !== 'string' || !p.name.trim() || ids.has(p.id) || p.commerciallyEnabled !== false) throw new Error('Проверка записей каталога не пройдена.');
    if (p.image && !/^\/images\/[a-z0-9/_-]+\.(?:webp|jpg|png)$/.test(p.image)) throw new Error('Недопустимый путь изображения.');
    ids.add(p.id);
  }
  if (data.source?.recordCount !== ids.size || data.source.commerciallyEnabled !== 0) throw new Error('Не совпадает число исходных записей.');
  return data;
}
export function selectProjects(projects, filters = {}) {
  const query = normalize(filters.q).slice(0,120);
  const words = query.split(/\s+/).filter(Boolean);
  return projects.filter(p => (!filters.district || p.district === filters.district)
    && (!filters.kind || p.kind === filters.kind) && (!filters.family || p.family === filters.family)
    && words.every(word => normalize([p.name,p.district,p.family].join(' ')).includes(word)));
}
export function paginate(rows, requested = 1) {
  const pages = Math.max(1,Math.ceil(rows.length/PAGE_SIZE));
  const page = Math.min(pages,Math.max(1,Math.trunc(Number(requested)) || 1));
  return {page,pages,total:rows.length,rows:rows.slice((page-1)*PAGE_SIZE,page*PAGE_SIZE)};
}
export function safeSelection(ids, projects) {
  if (!Array.isArray(ids)) return [];
  const valid=new Set(projects.map(p=>p.id));
  return [...new Set(ids.filter(id=>typeof id==='string' && valid.has(id)))].slice(0,MAX_SELECTION);
}
export function toggleSelection(ids,id,projects) {
  const current=safeSelection(ids,projects);
  if (!projects.some(p=>p.id===id)) throw new Error('Проект не найден.');
  if (current.includes(id)) return current.filter(x=>x!==id);
  if(current.length>=MAX_SELECTION) throw new Error('В подборке может быть до 12 проектов. Удалите лишний.');
  return [...current,id];
}
