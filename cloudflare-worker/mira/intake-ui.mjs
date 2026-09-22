const escape=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function intakePage(env){return `<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>МИРА — запрос подключения</title>
<style>body{font:18px/1.5 system-ui;margin:0;background:#f5f3ec;color:#152f2b}main{max-width:620px;margin:40px auto;padding:24px}h1{font-size:2rem}label{display:block;margin-top:16px}input:not([type=checkbox]){display:block;box-sizing:border-box;width:100%;font:inherit;padding:12px;border:1px solid #63736b;border-radius:6px}button{font:inherit;padding:12px 18px;margin:16px 0;background:#183d35;color:white;border:0;border-radius:6px}button:disabled{opacity:.5}a{color:#185d49}#message{white-space:pre-wrap;overflow-wrap:anywhere}small{display:block}input[type=checkbox]{width:22px;height:22px;vertical-align:middle}</style>
<script src="/mira/request/client.mjs" type="module"></script><script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script></head><body><main>
<a href="https://wegc.fund/mira/start/">МИРА</a><h1>Подключить агентство</h1><p>Оставьте рабочие контакты. Мы сохраним запрос и передадим его оператору. Отправка не создаёт договор и не открывает доступ к объектам.</p>
<form id="request" data-consent="${escape(env.PRIVACY_VERSION)}">
<label>Агентство<input name="company" required minlength="2" maxlength="160" autocomplete="organization"></label>
<label>Город<input name="city" required minlength="2" maxlength="120" autocomplete="address-level2"></label>
<label>Ваше имя<input name="name" required minlength="2" maxlength="120" autocomplete="name"></label>
<label>Рабочий email<input name="email" type="email" required maxlength="254" autocomplete="email"></label>
<label><input name="consent" type="checkbox" required> Согласен с обработкой данных для ответа на запрос по <a href="${escape(env.PRIVACY_NOTICE_URL)}" target="_blank" rel="noopener noreferrer">уведомлению о конфиденциальности</a>.</label>
<div class="cf-turnstile" data-sitekey="${escape(env.TURNSTILE_SITE_KEY)}" data-action="mira_intake"></div>
<button id="send" type="submit">Отправить запрос</button></form>
<p id="message" role="status" aria-live="polite"></p><button id="refresh" type="button" hidden>Проверить ответ</button>
<small>Ответ оператора появится на этой странице после проверки статуса. Автоматические письма не отправляются. Сохраняйте эту вкладку: номер без секретного ключа не даёт доступа к ответу.</small><noscript>Для отправки и получения квитанции требуется JavaScript. Данные без него не отправляются.</noscript>
</main></body></html>`;}
export const intakeClient=String.raw`
const form=document.getElementById('request'),message=document.getElementById('message'),send=document.getElementById('send'),refresh=document.getElementById('refresh');
const storageKey='mira-intake-receipt-v1';let saved;
try{saved=JSON.parse(sessionStorage.getItem(storageKey)||'null');}catch{}
if(!saved||!/^\w{8}-[\w-]{27}$/.test(saved.key||'')||! /^[0-9a-f]{64}$/.test(saved.token||'')){
 saved={key:crypto.randomUUID(),token:Array.from(crypto.getRandomValues(new Uint8Array(32)),n=>n.toString(16).padStart(2,'0')).join(''),id:null};
}
function retain(){try{sessionStorage.setItem(storageKey,JSON.stringify(saved));return true;}catch{return false;}}
const labels={received:'Получен',review:'На рассмотрении',needs_information:'Нужно уточнение',responded:'Есть ответ',closed:'Обработка завершена'};
function show(data){saved.id=data.id;const kept=retain();form.hidden=true;refresh.hidden=false;message.textContent='Номер запроса: '+data.id+'\nСтатус: '+(labels[data.status]||data.status)+(data.response?'\nОтвет оператора: '+data.response:'\nОтвет пока не опубликован.')+'\nЭто не активация агентства.'+(kept?'':'\nХранилище браузера недоступно. Не закрывайте и не обновляйте вкладку.');}
async function api(path,payload){const r=await fetch('/mira/request/'+path,{method:'POST',credentials:'omit',headers:{'Content-Type':'application/json','Authorization':'Bearer '+saved.token,'Idempotency-Key':saved.key},body:JSON.stringify(payload)});const data=await r.json();if(!r.ok)throw Error(data.error||'request_failed');return data;}
function failure(e){const known={intake_rate_limit:'Слишком много попыток. Повторите позже.',challenge_rejected:'Пройдите проверку ещё раз.',intake_disabled:'Приём временно закрыт.',intake_operator_unavailable:'Приём временно закрыт: оператор недоступен.',receipt_not_found:'Квитанция не найдена. Не создавайте повторный запрос, пока не проверен результат.',idempotency_payload_mismatch:'Эта попытка уже связана с другими данными. Повторная заявка не создана.'};message.textContent=known[e.message]||'Не удалось подтвердить результат. Повторите с теми же данными: повторная попытка не создаст дубликат.';}
form.addEventListener('submit',async e=>{e.preventDefault();if(!form.reportValidity())return;const values=new FormData(form);const challenge=values.get('cf-turnstile-response');if(!challenge){message.textContent='Сначала пройдите проверку безопасности.';return;}send.disabled=true;retain();try{show(await api('submit',{company:values.get('company'),city:values.get('city'),name:values.get('name'),email:values.get('email'),consent_version:form.dataset.consent,challenge}));}catch(error){failure(error);window.turnstile?.reset();}finally{send.disabled=false;}});
refresh.addEventListener('click',async()=>{refresh.disabled=true;try{show(await api('status',{id:saved.id}));}catch(error){failure(error);}finally{refresh.disabled=false;}});
if(saved.id){form.hidden=true;refresh.hidden=false;message.textContent='Сохранён номер запроса: '+saved.id+'. Нажмите «Проверить ответ».';}
`;
