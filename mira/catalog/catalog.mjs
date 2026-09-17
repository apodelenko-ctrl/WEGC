import {validateCatalogue,selectProjects,paginate,safeSelection,toggleSelection} from './catalog-core.mjs';
const $=s=>document.querySelector(s), KEY='mira-research-selection-v1';
const kinds={condo:'Кондоминиум',villa:'Вилла'};
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let data,selection=[],timer;
function toast(message){if($('#toast')){$('#toast').textContent=message;clearTimeout(timer);timer=setTimeout(()=>{$('#toast').textContent='';},5000);}}
function persist(){try{sessionStorage.setItem(KEY,JSON.stringify(selection));}catch{ /* Selection remains usable in memory. */ }}
function selected(){return data.projects.filter(p=>selection.includes(p.id));}
function updateSelection(){
 document.querySelectorAll('[data-add]').forEach(b=>{const yes=selection.includes(b.dataset.add);b.disabled=false;b.setAttribute('aria-pressed',String(yes));b.textContent=yes?'В подборке ✓':'В подборку +';});
 $('#shortlist-open').hidden=!selection.length;$('#shortlist-count').textContent=selection.length;
 $('#shortlist-items').innerHTML=selected().map(p=>`<div class="selection-row"><a href="/mira/catalog/projects/${p.id}/">${esc(p.name)}</a><button class="secondary" data-remove="${p.id}" type="button" aria-label="Убрать ${esc(p.name)}">Убрать ×</button></div>`).join('')||'<p>Подборка пуста. Выберите проекты в каталоге.</p>';
 $('#shortlist-download').disabled=!selection.length;
}
function visual(p){return p.image?`<figure><img src="${esc(p.image)}" alt="Архивная визуализация ${esc(p.name)}" width="800" height="500" loading="lazy" decoding="async"><figcaption>Архивная визуализация</figcaption></figure>`:`<div class="no-image"><span>${esc(kinds[p.kind]||'Проект')}</span><b>${esc(p.district||'Пхукет')}</b><small>Изображение не проверено</small></div>`;}
function card(p){return `<article class="project-card">${visual(p)}<div class="card-body"><p class="tag">${esc(p.district||'Район уточняется')} · ${esc(kinds[p.kind]||'Тип уточняется')}</p><h2><a href="/mira/catalog/projects/${p.id}/">${esc(p.name)}</a></h2><p class="family">${esc(p.family||'Группа девелопера уточняется')}</p><div class="card-actions"><a href="/mira/catalog/projects/${p.id}/">Подробнее ↗</a><button class="add secondary" data-add="${p.id}" aria-pressed="false" type="button">В подборку +</button></div></div></article>`;}
function filters(){return {q:$('#search').value,district:$('#district').value,kind:$('#kind').value,family:$('#family').value};}
function render(requested=1,writeURL=true){
 const f=filters(), result=paginate(selectProjects(data.projects,f),requested);
 $('#cards').innerHTML=result.rows.map(card).join('')||'<section class="empty"><h2>По такому запросу пока ничего нет</h2><p>Попробуйте часть названия или сбросьте фильтры.</p></section>';
 $('#result-count').textContent=`Найдено ${result.total} из ${data.projects.length} · показано ${result.rows.length}`;
 $('#page-status').textContent=`${result.page} / ${result.pages}`;
 $('#prev').disabled=result.page<=1;$('#next').disabled=result.page>=result.pages;
 $('#prev').onclick=()=>{render(result.page-1);$('#cards').scrollIntoView({block:'start'});};
 $('#next').onclick=()=>{render(result.page+1);$('#cards').scrollIntoView({block:'start'});};
 if(writeURL){const u=new URL(location.href);u.search='';for(const[k,v]of Object.entries(f))if(v)u.searchParams.set(k,v);if(result.page>1)u.searchParams.set('page',result.page);history.replaceState({},'',u);}
 updateSelection();
}
function readURL(){const q=new URLSearchParams(location.search);for(const[id,key]of [['search','q'],['district','district'],['kind','kind'],['family','family']]){const el=$('#'+id);el.value=(q.get(key)||'').slice(0,120);if(el.tagName==='SELECT'&&el.selectedIndex<0)el.value='';}render(q.get('page')||1,false);}
function setup(){
 if(!$('#cards'))return;
 for(const [id,key] of [['district','district'],['kind','kind'],['family','family']]){
   const select=$('#'+id);[...new Set(data.projects.map(p=>p[key]).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'ru')).forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=kinds[v]||v;select.append(o);});
 }
 let debounce;['search','district','kind','family'].forEach(id=>{const el=$('#'+id);el.disabled=false;el.addEventListener('input',()=>{clearTimeout(debounce);debounce=setTimeout(()=>render(1),id==='search'?100:0);});});
 $('#filters-reset').disabled=false;$('#filters-reset').onclick=()=>{clearTimeout(debounce);['search','district','kind','family'].forEach(id=>{$('#'+id).value='';});render(1);};
 addEventListener('popstate',readURL);readURL();
}
document.addEventListener('click',e=>{
 const add=e.target.closest('[data-add]'),remove=e.target.closest('[data-remove]');
 if(!data||(!add&&!remove))return;
 try{selection=toggleSelection(selection,(add||remove).dataset[add?'add':'remove'],data.projects);persist();updateSelection();}catch(err){toast(err.message);}
});
document.addEventListener('error',e=>{if(e.target.tagName==='IMG'){e.target.hidden=true;const figure=e.target.closest('figure');if(figure?.querySelector('figcaption'))figure.querySelector('figcaption').textContent='Изображение временно недоступно. Карточка работает.';}},true);
$('#shortlist-open')?.addEventListener('click',()=>$('#shortlist').showModal());
$('#shortlist-close')?.addEventListener('click',()=>$('#shortlist').close());
$('#shortlist-clear')?.addEventListener('click',()=>{selection=[];persist();updateSelection();});
$('#shortlist-download')?.addEventListener('click',()=>{
 if(!data||!selection.length)return;
 const lines=['МИРА / Подборка для предварительного изучения','Не отправлена. Наличие, цена и условия требуют подтверждения.','',...selected().flatMap(p=>[p.name,`${p.district||'Район уточняется'} · ${kinds[p.kind]||'Тип уточняется'}`,`https://wegc.fund/mira/catalog/projects/${p.id}/`,''])];
 const u=URL.createObjectURL(new Blob([lines.join('\n')],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=u;a.download='mira-phuket-selection.txt';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);$('#shortlist-message').textContent='Список подготовлен. Ничего не отправлено МИРА или застройщику.';
});
try{
 const response=await fetch('/mira/catalog/data.json',{cache:'no-cache'});if(!response.ok)throw new Error('Интерактивный каталог временно недоступен.');data=validateCatalogue(await response.json());
 try{selection=safeSelection(JSON.parse(sessionStorage.getItem(KEY)||'[]'),data.projects);}catch{selection=[];}
 setup();updateSelection();
}catch(err){const node=$('#load-error');if(node){node.hidden=false;node.textContent=err.message+' Статические карточки и алфавитный список остаются доступны.';}if($('#result-count'))$('#result-count').textContent='Показаны статические карточки. Полный список — по ссылке рядом.';}
