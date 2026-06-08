/*
 * WEGC promo toast — discreet, premium, once per session.
 * Surfaces "current developer incentives" and routes interest to the chat
 * widget (-> Telegram). No fabricated numbers; copy stays compliant.
 * Set window.WEGC_PROMO before this script to override the copy, e.g.:
 *   window.WEGC_PROMO = { en:{title,text}, ru:{...}, zh:{...} };
 */
(function () {
  // DISABLED: no active developer incentives to show yet (per request).
  // Re-enable later by removing this early return.
  return;
  if (window.__wegcPromo) return; window.__wegcPromo = true;
  try { if (sessionStorage.getItem('wegcPromoSeen')) return; } catch (e) {}

  var lang = (document.documentElement.lang || 'en').slice(0, 2).toLowerCase();
  if (lang !== 'ru' && lang !== 'zh') lang = 'en';

  var DEF = {
    en: { kicker: 'Limited-time', title: 'Current developer incentives',
          text: 'Selected projects have limited-time incentives from the developer right now. Ask us for the latest offers.',
          cta: 'See current offers' },
    ru: { kicker: 'Ограниченное предложение', title: 'Актуальные акции застройщика',
          text: 'По отдельным проектам сейчас действуют ограниченные по времени предложения застройщика. Спросите об актуальных условиях.',
          cta: 'Узнать предложения' },
    zh: { kicker: '限时', title: '开发商当前优惠',
          text: '部分项目目前提供开发商限时优惠。欢迎咨询最新优惠详情。',
          cta: '查看优惠' }
  };
  var T = (window.WEGC_PROMO && window.WEGC_PROMO[lang]) || DEF[lang];

  var css = '' +
    '.wegc-promo{position:fixed;right:20px;top:88px;z-index:99997;width:320px;max-width:calc(100vw - 40px);background:linear-gradient(180deg,#0d1424,#06080f);border:1px solid #1f2937;border-left:3px solid #d6b370;border-radius:14px;box-shadow:0 26px 60px -20px rgba(0,0,0,.7);padding:18px 20px 18px 20px;font-family:inherit;opacity:0;transform:translateY(-12px);transition:opacity .35s ease,transform .35s ease}' +
    '.wegc-promo.show{opacity:1;transform:none}' +
    '.wegc-promo .pk{font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#d6b370;margin-bottom:7px}' +
    '.wegc-promo h5{margin:0 0 6px;color:#fff;font-size:15px;font-weight:600;letter-spacing:-.01em}' +
    '.wegc-promo p{margin:0 0 14px;color:rgba(255,255,255,.7);font-size:12.5px;line-height:1.55}' +
    '.wegc-promo .pc{display:inline-flex;align-items:center;gap:6px;background:#d6b370;color:#0a0e1a;border:none;font-family:inherit;font-weight:700;font-size:13px;padding:9px 16px;border-radius:8px;cursor:pointer}' +
    '.wegc-promo .pc:hover{background:#c9a45f}' +
    '.wegc-promo .px{position:absolute;top:10px;right:12px;width:24px;height:24px;border:none;background:transparent;color:rgba(255,255,255,.55);font-size:18px;line-height:1;cursor:pointer}' +
    '.wegc-promo .px:hover{color:#fff}' +
    '@media(max-width:640px){.wegc-promo{display:none!important}}';
  var style = document.createElement('style'); style.textContent = css; document.head.appendChild(style);

  var el = document.createElement('div');
  el.className = 'wegc-promo'; el.setAttribute('role', 'complementary');
  el.innerHTML = '<button class="px" type="button" aria-label="Close">\u00d7</button>' +
    '<div class="pk">' + T.kicker + '</div>' +
    '<h5>' + T.title + '</h5><p>' + T.text + '</p>' +
    '<button class="pc" type="button">' + T.cta + ' \u2192</button>';

  function seen() { try { sessionStorage.setItem('wegcPromoSeen', '1'); } catch (e) {} }
  function close() { el.classList.remove('show'); seen(); setTimeout(function () { el.remove(); }, 350); }

  function mount() {
    document.body.appendChild(el);
    el.querySelector('.px').addEventListener('click', close);
    el.querySelector('.pc').addEventListener('click', function () {
      seen();
      var chat = document.querySelector('.wegc-chat-btn');
      if (chat) { chat.click(); el.remove(); }
      else {
        var home = lang === 'ru' ? '/index-ru.html' : (lang === 'zh' ? '/index-zh.html' : '/');
        location.href = home + '#contact';
      }
    });
    setTimeout(function () { el.classList.add('show'); }, 50);
  }
  function arm() { setTimeout(mount, 9000); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', arm); else arm();
})();
