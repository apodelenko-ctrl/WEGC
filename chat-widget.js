/*
 * WEGC on-site chat widget — floating "online operator".
 * Posts messages to the WEGC relay Worker, which forwards them to Telegram.
 * No phone number exposed; self-contained (injects its own CSS + DOM).
 */
(function () {
  if (window.__wegcChat) return; window.__wegcChat = true;
  var RELAY = 'https://wegc-form-relay.wegc.workers.dev';

  var lang = (document.documentElement.lang || 'en').slice(0, 2).toLowerCase();
  if (lang !== 'ru' && lang !== 'zh') lang = 'en';
  var T = {
    en: { btn: 'Chat', title: 'Chat with WEGC', sub: 'Tell us what you are looking for — our team replies shortly.',
          name: 'Your name', contact: 'Email or Telegram', msg: 'Your message…', send: 'Send',
          ok: 'Thank you — your message has been sent. We will reply shortly.',
          err: 'Could not send. Please write to post@wegc.fund.', need: 'Please enter a message.' },
    ru: { btn: 'Чат', title: 'Чат с WEGC', sub: 'Напишите, что вы ищете — команда ответит в ближайшее время.',
          name: 'Ваше имя', contact: 'Email или Telegram', msg: 'Ваше сообщение…', send: 'Отправить',
          ok: 'Спасибо — сообщение отправлено. Мы скоро ответим.',
          err: 'Не удалось отправить. Напишите на post@wegc.fund.', need: 'Введите сообщение.' },
    zh: { btn: '咨询', title: '在线咨询 WEGC', sub: '告诉我们您的需求,我们会尽快回复。',
          name: '您的称呼', contact: '邮箱或 Telegram', msg: '您的留言…', send: '发送',
          ok: '感谢您,信息已发送,我们会尽快回复。',
          err: '发送失败,请发送邮件至 post@wegc.fund。', need: '请输入留言。' }
  }[lang];

  var css = '' +
    '.wegc-chat-btn{position:fixed;right:20px;bottom:20px;z-index:99998;display:inline-flex;align-items:center;gap:8px;border:none;cursor:pointer;font-family:inherit;font-size:14px;font-weight:600;color:#0a0e1a;background:#d6b370;padding:13px 18px;border-radius:999px;box-shadow:0 10px 30px -8px rgba(0,0,0,.5);transition:transform .15s ease,background .15s ease}' +
    '.wegc-chat-btn:hover{background:#c9a45f;transform:translateY(-1px)}' +
    '.wegc-chat-btn svg{display:block}' +
    '.wegc-chat-panel{position:fixed;right:20px;bottom:78px;width:344px;max-width:calc(100vw - 32px);z-index:99999;background:#0a0e1a;border:1px solid #1f2937;border-radius:16px;box-shadow:0 30px 70px -20px rgba(0,0,0,.7);overflow:hidden;display:none;font-family:inherit}' +
    '.wegc-chat-panel.open{display:block}' +
    '.wegc-chat-hd{background:linear-gradient(180deg,#0d1424,#06080f);padding:18px 20px;position:relative}' +
    '.wegc-chat-hd h4{margin:0;color:#fff;font-size:16px;font-weight:600;letter-spacing:-.01em}' +
    '.wegc-chat-hd p{margin:6px 0 0;color:rgba(255,255,255,.66);font-size:12.5px;line-height:1.5}' +
    '.wegc-chat-x{position:absolute;top:14px;right:14px;width:26px;height:26px;border:none;background:rgba(255,255,255,.08);color:#fff;border-radius:50%;cursor:pointer;font-size:16px;line-height:1}' +
    '.wegc-chat-x:hover{background:rgba(255,255,255,.18)}' +
    '.wegc-chat-body{padding:16px 20px 20px;display:flex;flex-direction:column;gap:10px}' +
    '.wegc-chat-body input,.wegc-chat-body textarea{font-family:inherit;font-size:13.5px;color:#fff;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.14);padding:10px 12px;border-radius:8px;outline:none;width:100%}' +
    '.wegc-chat-body input:focus,.wegc-chat-body textarea:focus{border-color:#d6b370}' +
    '.wegc-chat-body input::placeholder,.wegc-chat-body textarea::placeholder{color:rgba(255,255,255,.4)}' +
    '.wegc-chat-body textarea{resize:vertical;min-height:74px}' +
    '.wegc-chat-send{background:#d6b370;color:#0a0e1a;border:none;font-weight:700;font-size:14px;padding:12px;border-radius:8px;cursor:pointer;font-family:inherit;transition:background .15s ease}' +
    '.wegc-chat-send:hover{background:#c9a45f}' +
    '.wegc-chat-send:disabled{opacity:.6;cursor:default}' +
    '.wegc-chat-note{color:rgba(255,255,255,.78);font-size:13px;line-height:1.55;padding:4px 0}' +
    '.wegc-hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}' +
    '@media(max-width:640px){.wegc-chat-panel{right:12px;left:12px;width:auto;bottom:74px}.wegc-chat-btn{right:14px;bottom:14px}}';

  var style = document.createElement('style'); style.textContent = css; document.head.appendChild(style);

  var btn = document.createElement('button');
  btn.className = 'wegc-chat-btn'; btn.type = 'button'; btn.setAttribute('aria-label', T.title);
  btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-8.5 8.5 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7A8.38 8.38 0 0 1 4 11.5 8.5 8.5 0 0 1 12.5 3 8.38 8.38 0 0 1 21 11.5z"/></svg><span>' + T.btn + '</span>';

  var panel = document.createElement('div');
  panel.className = 'wegc-chat-panel'; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', T.title);
  panel.innerHTML =
    '<div class="wegc-chat-hd"><button class="wegc-chat-x" type="button" aria-label="Close">\u00d7</button><h4>' + T.title + '</h4><p>' + T.sub + '</p></div>' +
    '<div class="wegc-chat-body">' +
      '<input class="wegc-hp" type="text" tabindex="-1" autocomplete="off" id="wegc-c-gotcha"/>' +
      '<input type="text" id="wegc-c-name" placeholder="' + T.name + '" autocomplete="name"/>' +
      '<input type="text" id="wegc-c-contact" placeholder="' + T.contact + '" autocomplete="email"/>' +
      '<textarea id="wegc-c-msg" placeholder="' + T.msg + '"></textarea>' +
      '<button class="wegc-chat-send" type="button" id="wegc-c-send">' + T.send + '</button>' +
    '</div>';

  function mount() {
    document.body.appendChild(btn); document.body.appendChild(panel);
    var x = panel.querySelector('.wegc-chat-x');
    var send = panel.querySelector('#wegc-c-send');
    btn.addEventListener('click', function () { panel.classList.toggle('open'); if (panel.classList.contains('open')) panel.querySelector('#wegc-c-msg').focus(); });
    x.addEventListener('click', function () { panel.classList.remove('open'); });
    send.addEventListener('click', async function () {
      if (panel.querySelector('#wegc-c-gotcha').value) { done(); return; }
      var msg = panel.querySelector('#wegc-c-msg').value.trim();
      if (!msg) { panel.querySelector('#wegc-c-msg').focus(); return; }
      send.disabled = true;
      var payload = {
        name: panel.querySelector('#wegc-c-name').value.trim(),
        contact: panel.querySelector('#wegc-c-contact').value.trim(),
        message: msg, _source: 'Online chat', _page: location.pathname, _lang: lang
      };
      var ok = false;
      try {
        var ctrl = new AbortController(); var t = setTimeout(function () { ctrl.abort(); }, 8000);
        var r = await fetch(RELAY, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: ctrl.signal });
        clearTimeout(t); ok = r.ok;
      } catch (e) { ok = false; }
      send.disabled = false;
      if (ok) done(); else showNote(T.err);
    });
    function done() { showNote(T.ok); }
    function showNote(text) {
      panel.querySelector('.wegc-chat-body').innerHTML = '<p class="wegc-chat-note">' + text + '</p>';
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
})();
