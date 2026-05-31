/*
 * WEGC collapsible disclaimers.
 * Long legal / disclaimer notes collapse to a single line and expand on click.
 * Keeps pages airy without hiding required legal text.
 */
(function () {
  if (window.__wegcNotes) return; window.__wegcNotes = true;

  var SEL = '.why-note,.mech-disclaimer,.f-disclaimer,.f-disc,.cases-note,.settle-note,.note,.disclaimer,.hero-foot-note';

  var css = '' +
    '.wegc-note{cursor:pointer;position:relative;padding-right:26px}' +
    '.wegc-note .wegc-note-in{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:1;line-clamp:1;overflow:hidden}' +
    '.wegc-note.is-open .wegc-note-in{-webkit-line-clamp:9999;line-clamp:9999;overflow:visible}' +
    '.wegc-note .wegc-note-tg{position:absolute;right:6px;top:6px;color:#a08156;font-size:12px;line-height:1;user-select:none;pointer-events:none;transition:transform .2s ease}' +
    '.wegc-note.is-open .wegc-note-tg{transform:rotate(180deg)}' +
    '.wegc-note:focus-visible{outline:2px solid rgba(160,129,86,.5);outline-offset:2px}';

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

    var nodes = [].slice.call(document.querySelectorAll(SEL));
    // also catch footnote paragraphs that begin with a <sup> marker, e.g. [1]
    [].forEach.call(document.querySelectorAll('p'), function (p) {
      if (p.firstElementChild && p.firstElementChild.tagName === 'SUP' && nodes.indexOf(p) < 0) nodes.push(p);
    });

    nodes.forEach(function (el) {
      if (el.getAttribute('data-wegc-note')) return;

      // measure natural height BEFORE clamping
      var cs = getComputedStyle(el);
      var lh = parseFloat(cs.lineHeight) || 18;
      var pad = (parseFloat(cs.paddingTop) || 0) + (parseFloat(cs.paddingBottom) || 0);
      if (el.clientHeight <= lh * 1.6 + pad) return; // single line — leave it

      var inner = document.createElement('span');
      inner.className = 'wegc-note-in';
      while (el.firstChild) inner.appendChild(el.firstChild);
      el.appendChild(inner);

      el.setAttribute('data-wegc-note', '1');
      el.classList.add('wegc-note');
      var tg = document.createElement('span');
      tg.className = 'wegc-note-tg'; tg.textContent = '\u25be';
      el.appendChild(tg);

      el.setAttribute('role', 'button');
      el.setAttribute('tabindex', '0');
      el.setAttribute('aria-expanded', 'false');

      function toggle() {
        var open = el.classList.toggle('is-open');
        el.setAttribute('aria-expanded', open ? 'true' : 'false');
      }
      el.addEventListener('click', function (e) {
        // don't hijack clicks on links inside the note
        if (e.target.closest && e.target.closest('a')) return;
        toggle();
      });
      el.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
      });
    });
  });
})();
