/** Progressive motion only. No fetch, analytics, cookies or persistent state. */
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
const image = document.querySelector('#hero-image');
const toggle = document.querySelector('#motion-toggle');
const hero = document.querySelector('.hero');
let motion = null;
let pausedByUser = false;
let heroVisible = true;
const connection = navigator.connection;
const permitted = () => !reduced.matches && !connection?.saveData;
function updateMotion() {
  if (!image || !toggle || !image.animate) return;
  const enabled = permitted();
  toggle.hidden = !enabled;
  if (!enabled) {
    motion?.cancel();
    motion = null;
    return;
  }
  if (!motion) {
    motion = image.animate([
      { transform: 'scale(1.015) translateX(0)' },
      { transform: 'scale(1.07) translateX(-0.5%)' }
    ], { duration: 18000, iterations: Infinity, direction: 'alternate', easing: 'ease-in-out' });
  }
  if (pausedByUser || document.hidden || !heroVisible) motion.pause();
  else motion.play();
  toggle.setAttribute('aria-pressed', String(pausedByUser));
  toggle.textContent = pausedByUser ? 'Продолжить движение' : 'Пауза движения';
}
toggle?.addEventListener('click', () => { pausedByUser = !pausedByUser; updateMotion(); });
reduced.addEventListener?.('change', updateMotion);
connection?.addEventListener?.('change', updateMotion);
document.addEventListener('visibilitychange', updateMotion);
window.addEventListener('pagehide', () => motion?.pause());
window.addEventListener('pageshow', updateMotion);
updateMotion();
// Default HTML remains visible; headings animate only when already intersecting.
if ('IntersectionObserver' in window) {
  const reveal = new IntersectionObserver(entries => entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    reveal.unobserve(entry.target);
    if (permitted() && entry.target.animate) {
      entry.target.animate([{ opacity: .65, transform: 'translateY(16px)' },
        { opacity: 1, transform: 'translateY(0)' }],
      { duration: 650, easing: 'cubic-bezier(.22,1,.36,1)' });
    }
  }), { threshold: .15 });
  document.querySelectorAll('[data-reveal]').forEach(el => reveal.observe(el));
  const cta = document.querySelector('.mobile-start');
  const form = document.querySelector('#start');
  let formVisible = false;
  const setCTA = () => cta?.classList.toggle('is-visible', !heroVisible && !formVisible);
  const visibility = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.target === hero) heroVisible = entry.isIntersecting;
      if (entry.target === form) formVisible = entry.isIntersecting;
    }
    updateMotion(); setCTA();
  });
  if (hero) visibility.observe(hero);
  if (form) visibility.observe(form);
}

// Keep the preview journey coherent without changing the accepted qualifier.
const planDemo = document.querySelector('#plan-demo');
function keepPreviewDestination() {
  if (!planDemo) return;
  try {
    const base = new URL(document.baseURI);
    const target = new URL(planDemo.getAttribute('href'), base);
    if (target.origin === base.origin && target.pathname === '/mira/marketplace.html') {
      target.pathname = '/mira/marketplace-design.html';
      planDemo.setAttribute('href', target.href);
    }
  } catch { /* An invalid preview URL is left untouched, never opened. */ }
}
if (planDemo) {
  keepPreviewDestination();
  new MutationObserver(keepPreviewDestination).observe(planDemo, { attributes: true, attributeFilter: ['href'] });
}
