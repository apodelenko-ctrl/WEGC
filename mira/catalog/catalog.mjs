import {validateCatalogue,selectProjects,paginate,safeSelection,toggleSelection} from './catalog-core.mjs';
const $=s=>document.querySelector(s), KEY='mira-research-selection-v1';
const kinds={condo:'Кондоминиум',villa:'Вилла'};
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let data,selection=[],timer;
function toast(message){if($('#toast')){$('#toast').textContent=message;clearTimeout(timer);timer=setTimeout(()=>{$('#toast').textContent='';},5000);}}
function persist(){try{localStorage.setItem(KEY,JSON.stringify(selection));sessionStorage.removeItem(KEY);}catch{try{sessionStorage.setItem(KEY,JSON.stringify(selection));}catch{ /* In-memory selection remains usable. */ }}}
function restoreSelection(){try{selection=safeSelection(JSON.parse(localStorage.getItem(KEY)??sessionStorage.getItem(KEY)??'[]'),data.projects);}catch{selection=[];}}
const cover=p=>'/images/hero/hero-phuket-'+(p.kind==='villa'?'aerial-sunset':'bay-karst')+'-m.jpg';
function restoreBackLink(){try{const u=new URL(sessionStorage.getItem('mira-catalog-return')||'/mira/catalog/',location.origin);if(u.origin===location.origin&&u.pathname==='/mira/catalog/')document.querySelectorAll('[data-catalog-back]').forEach(a=>a.href=u.pathname+u.search);}catch{}}

function selected(){return data.projects.filter(p=>selection.includes(p.id));}
function updateSelection(){
 document.querySelectorAll('[data-add]').forEach(b=>{const yes=selection.includes(b.dataset.add);b.disabled=false;b.setAttribute('aria-pressed',String(yes));b.textContent=yes?'В подборке ✓':'В подборку +';});
 $('#shortlist-open').hidden=!selection.length;$('#shortlist-count').textContent=selection.length;
 $('#shortlist-items').innerHTML=selected().map(p=>`<div class="selection-row"><a href="/mira/catalog/projects/${p.id}/">${esc(p.name)}</a><button class="secondary" data-remove="${p.id}" type="button" aria-label="Убрать ${esc(p.name)}">Убрать ×</button></div>`).join('')||'<p>Подборка пуста. Выберите проекты в каталоге.</p>';
 $('#shortlist-download').disabled=!selection.length;
}
function visual(p){return `<figure class="card-image"><img src="${esc(p.image||cover(p))}" data-fallback="${cover(p)}" alt="${esc(p.image?'Визуализация '+p.name:'Иллюстрация МИРА — Пхукет')}" width="1200" height="750" loading="lazy" decoding="async"><figcaption>${p.image?'Визуализация проекта':'МИРА / Пхукет · обложка каталога'}</figcaption></figure>`;}
function card(p){const url=`/mira/catalog/projects/${p.id}/`;return `<article class="project-card"><a class="visual-link" href="${url}" aria-label="Подробнее: ${esc(p.name)}">${visual(p)}</a><div class="card-body"><p class="tag">${esc(p.district||'Пхукет')} · ${esc(kinds[p.kind]||'Недвижимость')}</p><h2><a href="${url}">${esc(p.name)}</a></h2><p class="family">${esc(p.family||'Коллекция проектов Пхукета')}</p><p class="availability">Наличие и условия — по запросу</p><div class="card-actions"><a href="${url}">Подробнее ↗</a><button class="add secondary" data-add="${p.id}" aria-pressed="false" type="button">В подборку +</button></div></div></article>`;}
function filters(){return {q:$('#search').value,district:$('#district').value,kind:$('#kind').value,family:$('#family').value};}
function render(requested=1,writeURL=true){
 const f=filters(), result=paginate(selectProjects(data.projects,f),requested);
 $('#cards').innerHTML=result.rows.map(card).join('')||'<section class="empty"><h2>По такому запросу пока ничего нет</h2><p>Попробуйте часть названия или сбросьте фильтры.</p></section>';
 $('#result-count').textContent=`Найдено ${result.total} из ${data.projects.length} · показано ${result.rows.length}`;
 $('#page-status').textContent=`${result.page} / ${result.pages}`;
 $('#prev').disabled=result.page<=1;$('#next').disabled=result.page>=result.pages;
 $('#prev').onclick=()=>{render(result.page-1);$('#cards').scrollIntoView({block:'start'});};
 $('#next').onclick=()=>{render(result.page+1);$('#cards').scrollIntoView({block:'start'});};
 if(writeURL){const u=new URL(location.href);u.search='';for(const[k,v]of Object.entries(f))if(v)u.searchParams.set(k,v);if(result.page>1)u.searchParams.set('page',result.page);if(u.href!==location.href)history.pushState({},'',u);}
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
 const link=e.target.closest('a[href]');
 if(link&&location.pathname==='/mira/catalog/'){try{sessionStorage.setItem('mira-catalog-return',location.pathname+location.search);}catch{}}

 const add=e.target.closest('[data-add]'),remove=e.target.closest('[data-remove]');
 if(!data||(!add&&!remove))return;
 try{selection=toggleSelection(selection,(add||remove).dataset[add?'add':'remove'],data.projects);persist();updateSelection();}catch(err){toast(err.message);}
});
function recoverImage(img){
 if(img.tagName!=='IMG'||!img.dataset.fallback)return;
 const figure=img.closest('figure');
 if(!img.dataset.recovered){img.dataset.recovered='true';img.src=img.dataset.fallback;img.alt='Иллюстрация МИРА — Пхукет';if(figure?.querySelector('figcaption'))figure.querySelector('figcaption').textContent='МИРА / Пхукет · обложка каталога';}
 else{img.hidden=true;figure?.classList.add('branded-cover');}
}
document.addEventListener('error',e=>recoverImage(e.target),true);
addEventListener('storage',e=>{if(data&&(e.key===KEY||e.key===null)){restoreSelection();updateSelection();}});
addEventListener('pageshow',()=>{if(data){restoreSelection();updateSelection();}restoreBackLink();});
restoreBackLink();
$('#shortlist-open')?.addEventListener('click',()=>$('#shortlist').showModal());
$('#shortlist-close')?.addEventListener('click',()=>$('#shortlist').close());
$('#shortlist-clear')?.addEventListener('click',()=>{selection=[];persist();updateSelection();});
$('#shortlist-download')?.addEventListener('click',()=>{
 if(!data||!selection.length)return;
 const lines=['МИРА / Подборка для предварительного изучения','Не отправлена. Наличие и условия — по запросу.','',...selected().flatMap(p=>[p.name,`${p.district||'Район уточняется'} · ${kinds[p.kind]||'Тип уточняется'}`,`https://wegc.fund/mira/catalog/projects/${p.id}/`,''])];
 const u=URL.createObjectURL(new Blob([lines.join('\n')],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=u;a.download='mira-phuket-selection.txt';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);$('#shortlist-message').textContent='Подборка сохранена в файл. Вы можете поделиться ею, когда будете готовы.';
});
try{
 const response=await fetch('/mira/catalog/data.json',{cache:'no-cache'});if(!response.ok)throw new Error('Интерактивный каталог временно недоступен.');data=validateCatalogue(await response.json());
 restoreSelection();
 setup();updateSelection();document.querySelectorAll('img[data-fallback]').forEach(img=>{if(img.complete&&!img.naturalWidth)recoverImage(img);});
}catch(err){const node=$('#load-error');if(node){node.hidden=false;node.textContent=err.message+' Статические карточки и алфавитный список остаются доступны.';}if($('#result-count'))$('#result-count').textContent='Показаны статические карточки. Полный список — по ссылке рядом.';}
