(() => {
  const frames = [...document.querySelectorAll('.world-frame')];
  const tabs = [...document.querySelectorAll('[data-slide]')];
  const caption = document.getElementById('place-caption');
  const names = [['Palm Jumeirah', 'Dubai, UAE'], ['Nusa Penida', 'Bali, Indonesia'], ['The Andaman coast', 'Phuket, Thailand']];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let current = 0, timer, busy = false;
  const hero = document.querySelector('.world-hero');
  let visible = true, focused = false;
  function schedule() {
    clearTimeout(timer);
    if (!reduced.matches && !document.hidden && visible && !focused) timer = setTimeout(() => show((current + 1) % frames.length), 7000);
  }
  async function show(index) {
    if (busy) return;
    busy = true;
    try { await frames[index].querySelector('img').decode(); }
    catch { busy = false; schedule(); return; }
    frames[current].classList.remove('is-active');
    tabs[current].classList.remove('active');
    tabs[current].setAttribute('aria-pressed', 'false');
    current = index;
    frames[current].classList.add('is-active');
    tabs[current].classList.add('active');
    tabs[current].setAttribute('aria-pressed', 'true');
    caption.replaceChildren(document.createTextNode(names[index][0] + ' '));
    const country = document.createElement('span'); country.textContent = names[index][1]; caption.append(country);
    busy = false; schedule();
  }
  tabs.forEach((tab, index) => tab.addEventListener('click', () => show(index)));
  hero.addEventListener('focusin', () => { focused = true; clearTimeout(timer); });
  hero.addEventListener('focusout', () => { focused = false; schedule(); });
  document.addEventListener('visibilitychange', schedule);
  reduced.addEventListener('change', schedule);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => { visible = entries[0].isIntersecting; schedule(); }).observe(hero);
    const reveal = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('is-visible'); reveal.unobserve(entry.target); }
    }), {threshold: .08});
    document.querySelectorAll('.reveal').forEach(el => reveal.observe(el));
    document.documentElement.classList.add('motion-ready');
  }
  schedule();
})();
