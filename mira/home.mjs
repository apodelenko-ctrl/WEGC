// Progressive enhancement: every section and first slide work without JavaScript.
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
for (const gallery of document.querySelectorAll('[data-carousel]')) {
  const slides = [...gallery.querySelectorAll('.mira-slide')];
  const controls = gallery.querySelector('.carousel-controls');
  if (slides.length < 2 || !controls) continue;
  let current = 0, timer = null, paused = reducedMotion.matches, hovered = false, focused = false, inView = true;
  const pause = controls.querySelector('[data-pause]');
  const show = (index) => {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => { slide.classList.toggle('is-current', i === current); slide.setAttribute('aria-hidden', String(i !== current)); });
    controls.querySelector('[data-counter]').textContent = `${String(current + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
    gallery.dataset.activeSlide = String(current);
  };
  const schedule = () => {
    clearInterval(timer);
    timer = null;
    if (!paused && !reducedMotion.matches && !hovered && !focused && inView && !document.hidden) timer = setInterval(() => show(current + 1), 6500);
  };
  const updatePause = () => {
    pause.hidden = reducedMotion.matches;
    pause.textContent = paused ? '▶' : 'Ⅱ';
    pause.setAttribute('aria-label', paused ? 'Возобновить смену изображений' : 'Приостановить смену изображений');
    pause.setAttribute('aria-pressed', String(paused));
    schedule();
  };
  controls.hidden = false;
  controls.querySelector('[data-next]').addEventListener('click', () => { show(current + 1); schedule(); });
  controls.querySelector('[data-previous]').addEventListener('click', () => { show(current - 1); schedule(); });
  pause.addEventListener('click', () => { paused = !paused; updatePause(); });
  gallery.addEventListener('mouseenter', () => { hovered = true; schedule(); });
  gallery.addEventListener('mouseleave', () => { hovered = false; schedule(); });
  gallery.addEventListener('focusin', () => { focused = true; schedule(); });
  gallery.addEventListener('focusout', (event) => { focused = gallery.contains(event.relatedTarget); schedule(); });
  document.addEventListener('visibilitychange', schedule);
  reducedMotion.addEventListener('change', () => { paused = reducedMotion.matches; updatePause(); });
  if ('IntersectionObserver' in window) new IntersectionObserver(([entry]) => { inView = entry.isIntersecting; schedule(); }).observe(gallery);
  show(0); updatePause();
}
if (!reducedMotion.matches && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) if (entry.isIntersecting) { entry.target.classList.add('is-seen'); observer.unobserve(entry.target); }
  }, {threshold: .06});
  const targets = document.querySelectorAll('.step, .stackrow, .trow, .owner-side .point, .guide-steps li');
  targets.forEach((element, i) => {
    if (element.getBoundingClientRect().top < window.innerHeight) return;
    element.classList.add('reveal-ready'); element.style.setProperty('--reveal-delay', `${(i % 3) * 65}ms`); observer.observe(element);
  });
  reducedMotion.addEventListener('change', () => { if (reducedMotion.matches) targets.forEach(element => element.classList.add('is-seen')); });
}
