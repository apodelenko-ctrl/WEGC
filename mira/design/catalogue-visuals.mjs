/** Exact project-to-existing-media associations. No change to data or demo actions. */
const media = Object.freeze({
  'the-title-vivi': '/images/title-vivi-exterior-3.webp',
  'the-title-artrio': '/images/the-title-artrio-exterior-4-1.webp',
  'the-modeva': '/images/the-modeva-exterior-4-1.webp',
  'the-title-katabello': '/images/the-title-katabello-exterior-2.webp',
  'the-title-adora': '/images/the-title-adora-exterior-9.webp'
});
const root = document.querySelector('#content');
let onlyIllustrated = true;
const compact = window.matchMedia('(max-width:600px)');
compact.addEventListener?.('change', () => { const details=root?.querySelector('.filter-detail'); if(details) details.open=!compact.matches; });
function illustration(id, name, detail = false) {
  if (!Object.hasOwn(media, id)) return null;
  const figure = document.createElement('figure');
  figure.className = detail ? 'detail-visual' : 'project-visual';
  const img = document.createElement('img');
  img.src = media[id];
  img.alt = `Архивная визуализация ${name}`;
  img.loading = 'lazy'; img.decoding = 'async'; img.width = 1280; img.height = 800;
  const caption = document.createElement('figcaption');
  caption.textContent = 'Архивная визуализация · не текущее состояние и не наличие';
  img.addEventListener('error', () => {
    img.hidden = true;
    caption.textContent = 'Визуализация временно недоступна. Карточка проекта остаётся доступной.';
  }, { once: true });
  figure.append(img, caption);
  return figure;
}
function applyMode() {
  const cards = [...root.querySelectorAll('#cards .card')];
  const shown = cards.filter(card => !onlyIllustrated || card.dataset.illustrated === 'true');
  cards.forEach(card => { card.hidden = onlyIllustrated && card.dataset.illustrated !== 'true'; });
  root.querySelectorAll('[data-catalogue-mode]').forEach(button => {
    button.setAttribute('aria-pressed', String((button.dataset.catalogueMode === 'illustrated') === onlyIllustrated));
  });
  const count = root.querySelector('#count');
  if (count && cards.length) count.textContent = onlyIllustrated
    ? `С иллюстрациями: ${shown.length}. Всего в текущей выборке: ${cards.length}.`
    : `В текущей выборке: ${cards.length}. Не все проекты имеют опубликованные иллюстрации.`;
  let empty = root.querySelector('.catalogue-empty');
  if (!empty) { empty = document.createElement('p'); empty.className = 'catalogue-empty'; root.querySelector('#cards')?.before(empty); }
  empty.hidden = !onlyIllustrated || shown.length > 0 || cards.length === 0;
  empty.textContent = 'Для этой выборки нет иллюстраций. Выберите «Весь каталог», чтобы увидеть найденные проекты.';
}
function decorate() {
  const grid = root.querySelector('#cards');
  if (grid) {
    const filters = root.querySelector('.filters');
    if (filters && !filters.querySelector('.filter-detail')) {
      const details = document.createElement('details'); details.className = 'filter-detail'; details.open = !compact.matches;
      const summary = document.createElement('summary'); summary.textContent = 'Район, тип и группа';
      const options = document.createElement('div'); options.className = 'filter-options';
      [...filters.children].slice(1).forEach(label => options.append(label));
      details.append(summary, options); filters.append(details);
    }
    for (const card of grid.querySelectorAll('.card:not([data-decorated])')) {
      card.dataset.decorated = 'true';
      const link = card.querySelector('a[href]');
      const id = link ? new URL(link.href).searchParams.get('project') : null;
      const figure = illustration(id, card.querySelector('h2')?.textContent || 'проекта');
      card.dataset.illustrated = String(Boolean(figure));
      if (figure) card.prepend(figure); else card.classList.add('no-visual');
    }
    if (!root.querySelector('.catalogue-controls')) {
      const controls = document.createElement('div'); controls.className = 'catalogue-controls';
      controls.setAttribute('role', 'group'); controls.setAttribute('aria-label', 'Вид каталога');
      for (const [mode, label] of [['illustrated', 'С иллюстрациями'], ['all', 'Весь каталог']]) {
        const button = document.createElement('button'); button.type = 'button'; button.dataset.catalogueMode = mode;
        button.textContent = label; button.addEventListener('click', () => { onlyIllustrated = mode === 'illustrated'; applyMode(); });
        controls.append(button);
      }
      const note = document.createElement('span'); note.textContent = 'Обложка не означает допуск к продаже. Показаны существующие материалы из библиотеки.';
      controls.append(note); root.querySelector('#count').before(controls);
    }
    applyMode();
  } else if (root.querySelector('#lead-form') && !root.querySelector('.detail-visual')) {
    const id = new URL(window.location.href).searchParams.get('project');
    const heading = root.querySelector('h1');
    const figure = illustration(id, heading?.textContent || 'проекта', true);
    if (figure && heading) heading.after(figure);
  }
}
// Only react to engine render/filter operations, not our own captions or status changes.
const observer = new MutationObserver(records => {
  if (records.some(record => record.target === root || record.target.id === 'cards')) {
    observer.disconnect(); decorate(); observer.observe(root, { childList: true, subtree: true });
  }
});
if (root) { decorate(); observer.observe(root, { childList: true, subtree: true }); }
