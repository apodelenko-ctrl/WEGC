/*
 * WEGC on-site chat widget — live AI consultant "Anna".
 * Talks to the WEGC AI-agent Worker (/web), which runs Claude over the WEGC
 * knowledge base, qualifies the lead and hands warm leads to the manager.
 * Self-contained: injects its own CSS + DOM. No phone number exposed.
 */
(function () {
  if (window.__wegcChat) return; window.__wegcChat = true;
  var AGENT = (window.WEGC_AGENT || 'https://wegc-ai-agent.wegc.workers.dev/web');

  var lang = (document.documentElement.lang || 'en').slice(0, 2).toLowerCase();
  if (lang !== 'ru' && lang !== 'zh') lang = 'en';
  var T = {
    en: { btn: 'Chat', title: 'Anna · WEGC consultant', sub: 'Phuket real estate — ask me anything',
          ph: 'Type a message…', send: 'Send',
          hi: "Hi! I'm Anna, a WEGC consultant for Phuket real estate. I'll help you find a property for your goal and budget and answer questions on payment, instalments and ownership.\n\nWhat are you looking for — a home, a rental, or an investment? And what budget do you have in mind?",
          err: 'Connection hiccup. Please try again in a moment.' },
    ru: { btn: 'Чат', title: 'Анна · консультант WEGC', sub: 'Недвижимость Пхукета — спросите что угодно',
          ph: 'Напишите сообщение…', send: 'Отпр.',
          hi: 'Здравствуйте! Меня зовут Анна, я консультант WEGC по недвижимости на Пхукете. Помогу подобрать объект под вашу цель и бюджет и отвечу на вопросы по оплате, рассрочке и оформлению.\n\nРасскажите, что ищете — для жизни, под аренду или как инвестицию? И в каком бюджете ориентируетесь?',
          err: 'Связь подвисла. Попробуйте ещё раз через секунду.' },
    zh: { btn: '咨询', title: 'Anna · WEGC 顾问', sub: '普吉岛房产 — 欢迎咨询',
          ph: '输入消息…', send: '发送',
          hi: '您好!我是 WEGC 普吉岛房产顾问 Anna。我可以根据您的目标和预算帮您挑选房产,并解答付款、分期与产权方面的问题。\n\n请问您想找什么样的房产 — 自住、出租还是投资?预算大概多少?',
          err: '连接出现问题,请稍后再试。' }
  }[lang];

  // Persistent session id (server keeps the conversation memory)
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
    '.wegc-chat-log{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;scroll-behavior:smooth}' +
    '.wegc-msg{max-width:84%;padding:9px 13px;border-radius:13px;font-size:14px;line-height:1.5;white-space:pre-wrap;word-wrap:break-word}' +
    '.wegc-msg.a{align-self:flex-start;background:#1a2233;color:#e9eef6;border-bottom-left-radius:4px}' +
    '.wegc-msg.u{align-self:flex-end;background:#d6b370;color:#0a0e1a;border-bottom-right-radius:4px}' +
    '.wegc-msg.a a{color:#e3c07f;text-decoration:underline;word-break:break-all}' +
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
    '@media(max-width:640px){.wegc-chat-panel{right:10px;left:10px;width:auto;bottom:72px;height:calc(100vh - 96px)}.wegc-chat-btn{right:14px;bottom:14px}}';

  var style = document.createElement('style'); style.textContent = css; document.head.appendChild(style);

  var btn = document.createElement('button');
  btn.className = 'wegc-chat-btn'; btn.type = 'button'; btn.setAttribute('aria-label', T.title);
  btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-8.5 8.5 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7A8.38 8.38 0 0 1 4 11.5 8.5 8.5 0 0 1 12.5 3 8.38 8.38 0 0 1 21 11.5z"/></svg><span>' + T.btn + '</span>';

  var panel = document.createElement('div');
  panel.className = 'wegc-chat-panel'; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', T.title);
  panel.innerHTML =
    '<div class="wegc-chat-hd">' +
      '<div class="wegc-chat-av">A</div>' +
      '<div><h4>' + T.title + '</h4><p><span class="wegc-chat-dot"></span>' + T.sub + '</p></div>' +
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
    var opened = false, firstSent = false, busy = false;

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

    btn.addEventListener('click', function () {
      var isOpen = panel.classList.toggle('open');
      if (isOpen) {
        if (!opened) { opened = true; bubble(T.hi, 'a'); if (typeof ym !== 'undefined') ym(109732633, 'reachGoal', 'chat_open'); }
        input.focus();
      }
    });
    x.addEventListener('click', function () { panel.classList.remove('open'); });

    input.addEventListener('input', function () { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 96) + 'px'; });
    input.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); doSend(); } });
    send.addEventListener('click', doSend);

    async function doSend() {
      if (busy) return;
      if (panel.querySelector('#wegc-c-gotcha').value) return; // honeypot
      var text = input.value.trim();
      if (!text) { input.focus(); return; }
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

  // Metrika goal: first <video> playback per page view (passport tours, homepage card previews)
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
