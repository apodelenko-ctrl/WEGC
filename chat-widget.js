/*
 * WEGC on-site chat widget — live AI consultant "Anna".
 * Talks to the WEGC AI-agent Worker (/web), which runs Claude over the WEGC
 * knowledge base, qualifies the lead and hands warm leads to the manager.
 * Self-contained: injects its own CSS + DOM. No phone number exposed.
 */
(function () {
  if (window.__wegcChat) return; window.__wegcChat = true;
  var AGENT = (window.WEGC_AGENT || 'https://wegc-ai-agent.wegc.workers.dev/web');

  var SUPPORTED = { ru: 1, zh: 1, en: 1 };
  function pickLang() {
    try {
      var saved = localStorage.getItem('wegc_chat_lang');
      if (saved && SUPPORTED[saved]) return saved;
    } catch (e) {}
    var page = String(document.documentElement.lang || '').slice(0, 2).toLowerCase();
    if (SUPPORTED[page]) return page;
    var nav = (navigator.languages && navigator.languages.length) ? navigator.languages : [navigator.language || navigator.userLanguage || ''];
    for (var i = 0; i < nav.length; i++) {
      var code = String(nav[i] || '').slice(0, 2).toLowerCase();
      if (SUPPORTED[code]) return code;
    }
    return 'en';
  }
  var lang = pickLang();
  var DICT = {
    en: {
      btn: 'Chat', title: 'Anna · WEGC consultant', sub: 'Phuket real estate — ask me anything',
      ph: 'Type a message…', send: 'Send',
      hi: "Hi! I'm Anna, WEGC consultant for Phuket real estate. Pick a topic below or type your question.",
      qprompt: 'What are you looking for?',
      chips: [
        { label: '🏠 Home for family', text: 'Looking for a home in Phuket for my family — what do you recommend?',
          answer: 'For family living, most clients look at spacious condos or villas in calm, well-served areas — Layan, Bang Tao, Rawai: close to beaches, schools and shops. We work directly with developers, so buyer commission is 0%.\n\nTell me your budget and how many bedrooms you need — I\u2019ll shortlist 2–3 options.' },
        { label: '📈 Investment', text: 'Interested in a new launch for investment — typical yields and entry budget?',
          answer: 'For investment, units in strong tourist areas — Bang Tao, Surin, Kamala — work best. Realistic net yield is 5–9% a year, and we check every project against a financial model, no brochure promises. Entry is roughly from 2.87M THB.\n\nShare your budget and I\u2019ll show projects with real yield numbers.' },
        { label: '💰 Up to 5M THB', text: 'Budget up to 5 million THB — which projects fit?',
          answer: 'Up to 5M THB you can get studios and 1-bedroom units in off-plan projects with 0% developer instalments — a solid entry for both rental and resale.\n\nFor your own use or for rental? And which area? I\u2019ll pick specific units.' },
        { label: '📋 Pay from abroad', text: 'How can I pay from outside Thailand? Instalments, freehold options?',
          answer: 'You can pay from abroad legally: sign the contract with the developer, transfer to a non-resident account, and the bank issues an FET form (needed to repatriate funds later). Developer instalments are 0%, and both freehold and leasehold are available.\n\nWant me to map the steps for a specific project and budget?' }
      ],
      err: 'Connection hiccup. Please try again in a moment.',
      nudge: 'I can shortlist Phuket options for your budget — just tell me what you\u2019re looking for 👋'
    },
    ru: {
      btn: 'Чат', title: 'Анна · консультант WEGC', sub: 'Недвижимость Пхукета — спросите что угодно',
      ph: 'Напишите сообщение…', send: 'Отпр.',
      hi: 'Здравствуйте! Я Анна, консультант WEGC по недвижимости на Пхукете. Выберите тему ниже или напишите свой вопрос.',
      qprompt: 'Что вас интересует?',
      chips: [
        { label: '🏠 Для жизни', text: 'Ищу недвижимость на Пхукете для жизни семьёй — что посоветуете?',
          answer: 'Для жизни семьёй обычно смотрят просторные кондо или виллы в спокойных районах с инфраструктурой — Лаян, Банг Тао, Раваи: рядом пляжи, школы, магазины. Работаем напрямую с застройщиком — комиссия для покупателя 0%.\n\nНапишите бюджет и сколько нужно спален — подберу 2–3 варианта под вас.' },
        { label: '📈 Инвестиция', text: 'Интересует инвестиция в новостройку — какая доходность и с какого бюджета?',
          answer: 'Под инвестицию берут юниты в сильных туристических районах — Банг Тао, Сурин, Камала. Реалистичная чистая доходность 5–9% годовых, каждый проект сверяем с финмоделью, без обещаний из брошюр. Вход — примерно от 2,87 млн ฿.\n\nНазовите бюджет — покажу проекты с конкретными цифрами доходности.' },
        { label: '💰 До 5 млн ฿', text: 'Бюджет до 5 млн бат — какие проекты подойдут?',
          answer: 'В бюджет до 5 млн ฿ попадают студии и 1-спальные в строящихся проектах с рассрочкой от застройщика 0%. Рабочий вход и под аренду, и под перепродажу.\n\nДля себя или под аренду? И какой район интересен? Подберу конкретные юниты.' },
        { label: '📋 Оплата из РФ', text: 'Как оплатить из России? Рассрочка, freehold, что нужно для сделки?',
          answer: 'Оплатить из России можно легально, в рублях:\n1) договор с застройщиком;\n2) перевод рублей нашему фин. представителю в РФ;\n3) он платит застройщику от вашего имени, банк фиксирует FET для будущего вывода средств.\nРассрочка застройщика 0%, freehold и leasehold — оба варианта.\n\nПод какой проект и бюджет рассчитать схему?' }
      ],
      err: 'Связь подвисла. Попробуйте ещё раз через секунду.',
      nudge: 'Помогу подобрать варианты на Пхукете под ваш бюджет — напишите, что ищете 👋'
    },
    zh: {
      btn: '咨询', title: 'Anna · WEGC 顾问', sub: '普吉岛房产 — 欢迎咨询',
      ph: '输入消息…', send: '发送',
      hi: '您好!我是 WEGC 普吉岛房产顾问 Anna。请选择下方主题或直接输入您的问题。',
      qprompt: '您想了解什么?',
      chips: [
        { label: '🏠 自住', text: '想在普吉岛为家人买一套自住房 — 有什么推荐?',
          answer: '自住的客户通常会看莱扬、邦涛、拉威等安静且配套齐全的区域的大户型公寓或别墅 — 靠近海滩、学校和商场。我们与开发商直接合作,买家佣金为 0%。\n\n请告诉我您的预算和需要几间卧室 — 我帮您筛选 2–3 个方案。' },
        { label: '📈 投资', text: '考虑投资新房 — 典型回报率和入门预算是多少?',
          answer: '投资首选邦涛、苏林、卡马拉等热门旅游区的房源。实际净收益约为每年 5–9%,每个项目都会用财务模型核对,不做夸大承诺。入门门槛约从 287 万泰铢起。\n\n告诉我您的预算,我会展示带有具体收益数据的项目。' },
        { label: '💰 500万泰铢内', text: '预算500万泰铢以内 — 有哪些项目?',
          answer: '500 万泰铢以内可以买到期房项目的开间和一居室,开发商提供 0% 分期 — 自住或出租出售都很合适。\n\n是自住还是出租?想看哪个区域?我帮您挑选具体房源。' },
        { label: '📋 海外付款', text: '如何从海外付款?分期、freehold 怎么操作?',
          answer: '海外可合法付款:与开发商签约,汇款至非居民账户,银行出具 FET 表(日后资金汇出所需)。开发商分期为 0%,freehold 和 leasehold 均可。\n\n需要我针对具体项目和预算说明步骤吗?' }
      ],
      err: '连接出现问题,请稍后再试。',
      nudge: '我可以根据您的预算推荐普吉岛房源 — 告诉我您的需求 👋'
    }
  };
  var T = DICT[lang];
  var LANGS = [['ru', 'РУ'], ['en', 'EN'], ['zh', '中']];

  var sid;
  try {
    sid = localStorage.getItem('wegc_chat_sid');
    if (!sid) { sid = 's' + Date.now().toString(36) + Math.random().toString(36).slice(2, 10); localStorage.setItem('wegc_chat_sid', sid); }
  } catch (e) { sid = 's' + Date.now().toString(36) + Math.random().toString(36).slice(2, 10); }

  var css = '' +
    '.wegc-chat-btn{position:fixed;right:20px;bottom:20px;z-index:99998;display:inline-flex;align-items:center;gap:8px;border:none;cursor:pointer;font-family:inherit;font-size:14px;font-weight:600;color:#0a0e1a;background:#d6b370;padding:13px 18px;border-radius:999px;box-shadow:0 10px 30px -8px rgba(0,0,0,.5);transition:transform .15s ease,background .15s ease}' +
    '.wegc-chat-btn:hover{background:#c9a45f;transform:translateY(-1px)}' +
    '.wegc-chat-btn svg{display:block}' +
    '.wegc-chat-panel{position:fixed;right:20px;bottom:78px;width:370px;max-width:calc(100vw - 32px);height:560px;max-height:calc(100vh - 110px);z-index:99999;background:#0a0e1a;border:1px solid #1f2937;border-radius:16px;box-shadow:0 30px 70px -20px rgba(0,0,0,.7);overflow:hidden;display:none;flex-direction:column;font-family:inherit}' +
    '.wegc-chat-panel.open{display:flex}' +
    '.wegc-chat-hd{background:linear-gradient(180deg,#0d1424,#06080f);padding:15px 18px;position:relative;flex-shrink:0;display:flex;align-items:center;gap:11px}' +
    '.wegc-chat-av{width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#d6b370,#a9824a);display:flex;align-items:center;justify-content:center;color:#0a0e1a;font-weight:700;font-size:16px;flex-shrink:0}' +
    '.wegc-chat-hd h4{margin:0;color:#fff;font-size:14.5px;font-weight:600;letter-spacing:-.01em}' +
    '.wegc-chat-hd p{margin:3px 0 0;color:rgba(255,255,255,.55);font-size:11.5px;line-height:1.4}' +
    '.wegc-chat-dot{width:7px;height:7px;border-radius:50%;background:#46d17f;display:inline-block;margin-right:5px;vertical-align:middle}' +
    '.wegc-chat-x{position:absolute;top:12px;right:12px;width:26px;height:26px;border:none;background:rgba(255,255,255,.08);color:#fff;border-radius:50%;cursor:pointer;font-size:16px;line-height:1}' +
    '.wegc-chat-x:hover{background:rgba(255,255,255,.18)}' +
    '.wegc-lang{position:absolute;top:13px;right:46px;display:inline-flex;gap:2px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:2px}' +
    '.wegc-lang button{border:none;background:transparent;color:rgba(255,255,255,.6);font:inherit;font-size:11px;font-weight:600;line-height:1;padding:4px 6px;border-radius:6px;cursor:pointer}' +
    '.wegc-lang button:hover{color:#fff}' +
    '.wegc-lang button.on{background:#d6b370;color:#0a0e1a}' +
    '.wegc-chat-log{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;scroll-behavior:smooth}' +
    '.wegc-msg{max-width:84%;padding:9px 13px;border-radius:13px;font-size:14px;line-height:1.5;white-space:pre-wrap;word-wrap:break-word}' +
    '.wegc-msg.a{align-self:flex-start;background:#1a2233;color:#e9eef6;border-bottom-left-radius:4px}' +
    '.wegc-msg.u{align-self:flex-end;background:#d6b370;color:#0a0e1a;border-bottom-right-radius:4px}' +
    '.wegc-msg.a a{color:#e3c07f;text-decoration:underline;word-break:break-all}' +
    '.wegc-chips{align-self:flex-start;display:flex;flex-direction:column;gap:7px;max-width:92%}' +
    '.wegc-chips .q{font-size:12px;color:rgba(255,255,255,.55);margin-bottom:2px}' +
    '.wegc-chip{display:block;width:100%;text-align:left;border:1px solid rgba(214,179,112,.35);background:rgba(214,179,112,.08);color:#e9eef6;border-radius:10px;padding:9px 12px;font:inherit;font-size:13px;line-height:1.35;cursor:pointer;transition:background .12s ease,border-color .12s ease}' +
    '.wegc-chip:hover{background:rgba(214,179,112,.18);border-color:rgba(214,179,112,.55)}' +
    '.wegc-chip:disabled{opacity:.45;cursor:default}' +
    '.wegc-typing{align-self:flex-start;display:inline-flex;gap:4px;padding:11px 14px;background:#1a2233;border-radius:13px;border-bottom-left-radius:4px}' +
    '.wegc-typing span{width:6px;height:6px;border-radius:50%;background:rgba(255,255,255,.5);animation:wegcb 1s infinite}' +
    '.wegc-typing span:nth-child(2){animation-delay:.16s}.wegc-typing span:nth-child(3){animation-delay:.32s}' +
    '@keyframes wegcb{0%,60%,100%{opacity:.3;transform:translateY(0)}30%{opacity:1;transform:translateY(-3px)}}' +
    '.wegc-chat-ft{flex-shrink:0;border-top:1px solid #1c2533;padding:10px 12px;display:flex;gap:8px;align-items:flex-end;background:#0a0e1a}' +
    '.wegc-chat-ft textarea{flex:1;font-family:inherit;font-size:14px;color:#fff;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.14);padding:10px 12px;border-radius:10px;outline:none;resize:none;max-height:96px;line-height:1.4}' +
    '.wegc-chat-ft textarea:focus{border-color:#d6b370}.wegc-chat-ft textarea::placeholder{color:rgba(255,255,255,.4)}' +
    '.wegc-chat-go{flex-shrink:0;background:#d6b370;color:#0a0e1a;border:none;font-weight:700;font-size:13px;padding:0 15px;height:40px;border-radius:10px;cursor:pointer;font-family:inherit;transition:background .15s ease}' +
    '.wegc-chat-go:hover{background:#c9a45f}.wegc-chat-go:disabled{opacity:.5;cursor:default}' +
    '.wegc-hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}' +
    '.wegc-nudge{position:fixed;right:20px;bottom:78px;z-index:99997;max-width:264px;background:#141925;border:1px solid #2a3447;color:#e9eef6;border-radius:14px;border-bottom-right-radius:4px;padding:13px 32px 13px 14px;font-size:13.5px;line-height:1.45;box-shadow:0 16px 40px -12px rgba(0,0,0,.6);cursor:pointer;animation:wegcpop .25s ease}' +
    '.wegc-nudge:hover{border-color:#3a4861}' +
    '.wegc-nudge-x{position:absolute;top:6px;right:8px;border:none;background:transparent;color:#8b95a7;font-size:15px;line-height:1;cursor:pointer;padding:2px}' +
    '.wegc-nudge-x:hover{color:#fff}' +
    '@keyframes wegcpop{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}' +
    '@media(max-width:640px){.wegc-nudge{right:14px;bottom:70px;max-width:calc(100vw - 90px)}}' +
    '@media(max-width:640px){.wegc-chat-panel{right:8px;left:8px;width:auto;top:calc(8px + env(safe-area-inset-top));bottom:calc(8px + env(safe-area-inset-bottom));height:auto;max-height:none;border-radius:14px}.wegc-chat-panel.open{display:flex}.wegc-chat-btn{right:14px;bottom:14px}}';

  var style = document.createElement('style'); style.textContent = css; document.head.appendChild(style);

  var btn = document.createElement('button');
  btn.className = 'wegc-chat-btn'; btn.type = 'button'; btn.setAttribute('aria-label', T.title);
  btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-8.5 8.5 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7A8.38 8.38 0 0 1 4 11.5 8.5 8.5 0 0 1 12.5 3 8.38 8.38 0 0 1 21 11.5z"/></svg><span>' + T.btn + '</span>';

  var panel = document.createElement('div');
  panel.className = 'wegc-chat-panel'; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', T.title);
  var langBtns = LANGS.map(function (l) {
    return '<button type="button" data-lang="' + l[0] + '"' + (l[0] === lang ? ' class="on"' : '') + '>' + l[1] + '</button>';
  }).join('');
  panel.innerHTML =
    '<div class="wegc-chat-hd">' +
      '<div class="wegc-chat-av">A</div>' +
      '<div><h4 id="wegc-title">' + T.title + '</h4><p><span class="wegc-chat-dot"></span><span id="wegc-sub">' + T.sub + '</span></p></div>' +
      '<div class="wegc-lang" id="wegc-lang">' + langBtns + '</div>' +
      '<button class="wegc-chat-x" type="button" aria-label="Close">\u00d7</button>' +
    '</div>' +
    '<div class="wegc-chat-log" id="wegc-log"></div>' +
    '<div class="wegc-chat-ft">' +
      '<input class="wegc-hp" type="text" tabindex="-1" autocomplete="off" id="wegc-c-gotcha"/>' +
      '<textarea id="wegc-c-msg" rows="1" placeholder="' + T.ph + '"></textarea>' +
      '<button class="wegc-chat-go" type="button" id="wegc-c-send">' + T.send + '</button>' +
    '</div>';

  function mount() {
    document.body.appendChild(btn); document.body.appendChild(panel);
    var log = panel.querySelector('#wegc-log');
    var input = panel.querySelector('#wegc-c-msg');
    var send = panel.querySelector('#wegc-c-send');
    var x = panel.querySelector('.wegc-chat-x');
    var titleEl = panel.querySelector('#wegc-title');
    var subEl = panel.querySelector('#wegc-sub');
    var langBox = panel.querySelector('#wegc-lang');
    var opened = false, firstSent = false, busy = false, chipsShown = false;
    var nudgeEl = null, nudgeShown = false, nudgeTimer = null;

    function applyLang() {
      T = DICT[lang];
      titleEl.textContent = T.title;
      subEl.textContent = T.sub;
      input.placeholder = T.ph;
      send.textContent = T.send;
      btn.setAttribute('aria-label', T.title);
      btn.querySelector('span').textContent = T.btn;
      if (nudgeEl) nudgeEl.querySelector('.wegc-nudge-txt').textContent = T.nudge;
      Array.prototype.forEach.call(langBox.children, function (b) {
        b.className = (b.getAttribute('data-lang') === lang) ? 'on' : '';
      });
    }

    function setLang(next) {
      if (!SUPPORTED[next] || next === lang) { applyLang(); return; }
      lang = next;
      try { localStorage.setItem('wegc_chat_lang', lang); } catch (e) {}
      applyLang();
      if (opened && !firstSent) {
        log.innerHTML = '';
        chipsShown = false;
        bubble(T.hi, 'a');
        showChips();
      }
    }

    langBox.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-lang]');
      if (b) setLang(b.getAttribute('data-lang'));
    });

    function scroll() { log.scrollTop = log.scrollHeight; }
    function escHtml(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
    function linkify(s) {
      return escHtml(s).replace(/(https?:\/\/[^\s<]+[^\s<.,;:!?)\]])/g, function (u) {
        return '<a href="' + u + '" target="_blank" rel="noopener">' + u + '</a>';
      });
    }
    function bubble(text, cls) {
      var d = document.createElement('div'); d.className = 'wegc-msg ' + cls;
      if (cls === 'a') d.innerHTML = linkify(text); else d.textContent = text;
      log.appendChild(d); scroll(); return d;
    }
    function typing(on) {
      var ex = log.querySelector('.wegc-typing');
      if (on && !ex) { var t = document.createElement('div'); t.className = 'wegc-typing'; t.innerHTML = '<span></span><span></span><span></span>'; log.appendChild(t); scroll(); }
      else if (!on && ex) ex.remove();
    }
    function hideChips() {
      var box = log.querySelector('.wegc-chips');
      if (box) box.remove();
      chipsShown = false;
    }
    function showChips() {
      if (chipsShown || firstSent) return;
      chipsShown = true;
      var box = document.createElement('div'); box.className = 'wegc-chips';
      var q = document.createElement('div'); q.className = 'q'; q.textContent = T.qprompt;
      box.appendChild(q);
      T.chips.forEach(function (c) {
        var b = document.createElement('button');
        b.type = 'button'; b.className = 'wegc-chip'; b.textContent = c.label;
        b.addEventListener('click', function () {
          if (busy || firstSent) return;
          box.querySelectorAll('.wegc-chip').forEach(function (el) { el.disabled = true; });
          if (c.answer) sendChip(c); else doSend(c.text);
        });
        box.appendChild(b);
      });
      log.appendChild(box); scroll();
    }
    function pingOpen() {
      fetch(AGENT, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sid: sid, lang: lang, event: 'open' }),
        keepalive: true
      }).catch(function () {});
    }

    function nudgeOff() {
      if (nudgeTimer) { clearTimeout(nudgeTimer); nudgeTimer = null; }
      if (nudgeEl) { nudgeEl.remove(); nudgeEl = null; }
    }
    function nudgeDismissed() {
      try { return sessionStorage.getItem('wegc_nudge') === 'off'; } catch (e) { return false; }
    }
    function showNudge() {
      if (nudgeShown || opened || nudgeEl || nudgeDismissed() || panel.classList.contains('open')) return;
      nudgeShown = true;
      nudgeEl = document.createElement('div');
      nudgeEl.className = 'wegc-nudge';
      nudgeEl.innerHTML = '<button class="wegc-nudge-x" type="button" aria-label="Close">\u00d7</button><div class="wegc-nudge-txt"></div>';
      nudgeEl.querySelector('.wegc-nudge-txt').textContent = T.nudge;
      nudgeEl.addEventListener('click', function () { openChat(); });
      nudgeEl.querySelector('.wegc-nudge-x').addEventListener('click', function (e) {
        e.stopPropagation();
        nudgeOff();
        try { sessionStorage.setItem('wegc_nudge', 'off'); } catch (_) {}
      });
      document.body.appendChild(nudgeEl);
    }

    function openChat() {
      nudgeOff();
      panel.classList.add('open');
      if (!opened) {
        opened = true;
        bubble(T.hi, 'a');
        showChips();
        pingOpen();
        if (typeof ym !== 'undefined') ym(109732633, 'reachGoal', 'chat_open');
      }
      input.focus();
    }

    btn.addEventListener('click', function () {
      if (panel.classList.contains('open')) panel.classList.remove('open');
      else openChat();
    });
    x.addEventListener('click', function () { panel.classList.remove('open'); });

    nudgeTimer = setTimeout(showNudge, 18000);
    document.addEventListener('mouseleave', function (e) { if (e.clientY <= 0) showNudge(); });

    input.addEventListener('input', function () { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 96) + 'px'; });
    input.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); doSend(); } });
    send.addEventListener('click', function () { doSend(); });

    function sendChip(c) {
      if (busy) return;
      hideChips();
      bubble(c.text, 'u');
      busy = true; send.disabled = true;
      if (!firstSent) { firstSent = true; if (typeof ym !== 'undefined') ym(109732633, 'reachGoal', 'chat_send'); }
      typing(true);
      setTimeout(function () {
        typing(false);
        bubble(c.answer, 'a');
        busy = false; send.disabled = false; input.focus();
      }, 450);
    }

    async function doSend(forcedText) {
      if (busy) return;
      if (panel.querySelector('#wegc-c-gotcha').value) return;
      var text = (typeof forcedText === 'string' ? forcedText : input.value).trim();
      if (!text) { input.focus(); return; }
      hideChips();
      bubble(text, 'u');
      input.value = ''; input.style.height = 'auto';
      busy = true; send.disabled = true;
      if (!firstSent) { firstSent = true; if (typeof ym !== 'undefined') ym(109732633, 'reachGoal', 'chat_send'); }
      typing(true);
      try {
        var ctrl = new AbortController(); var to = setTimeout(function () { ctrl.abort(); }, 30000);
        var r = await fetch(AGENT, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sid: sid, text: text, lang: lang }), signal: ctrl.signal
        });
        clearTimeout(to);
        var data = await r.json();
        typing(false);
        bubble((data && data.reply) ? data.reply : T.err, 'a');
        if (data && data.handoff && typeof ym !== 'undefined') ym(109732633, 'reachGoal', 'chat_lead');
      } catch (e) {
        typing(false); bubble(T.err, 'a');
      }
      busy = false; send.disabled = false; input.focus();
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();

  var videoGoalFired = false;
  document.addEventListener('play', function (e) {
    if (videoGoalFired) return;
    var el = e.target;
    if (el && el.tagName === 'VIDEO') {
      videoGoalFired = true;
      if (typeof ym !== 'undefined') ym(109732633, 'reachGoal', 'video_play');
    }
  }, true);
})();
