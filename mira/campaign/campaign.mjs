import {createPlan,briefText} from '../agency/qualification.mjs';
const form=document.querySelector('#campaign-form');
let current=null;
if(form){
 const result=document.querySelector('#plan'),msg=document.querySelector('#form-message');
 form.addEventListener('submit',e=>{e.preventDefault();if(!form.reportValidity())return;try{
 current=Object.fromEntries(new FormData(form));const p=createPlan(current);
 document.querySelector('#plan-title').textContent=p.title;document.querySelector('#plan-description').textContent=p.description;
 document.querySelector('#plan-steps').replaceChildren(...p.steps.map(text=>{const li=document.createElement('li');li.textContent=text;return li;}));
 document.querySelector('#plan-boundary').textContent=p.boundary;result.hidden=false;msg.textContent='План готов. Ничего не отправлено.';document.querySelector('#plan-title').focus();
 }catch{current=null;result.hidden=true;msg.textContent='Выберите ответы из предложенных вариантов.';}});
 form.addEventListener('change',()=>{current=null;result.hidden=true;msg.textContent='';});
 document.querySelector('#download').addEventListener('click',()=>{if(!current)return;const text=briefText(current);const u=URL.createObjectURL(new Blob(['\uFEFF',text],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=u;a.download='mira-agency-brief.txt';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);msg.textContent='Бриф подготовлен. Он не отправлялся в МИРА.';});
 form.querySelector('fieldset').disabled=false;
}
const reduced=matchMedia('(prefers-reduced-motion: reduce)'),button=document.querySelector('#motion-toggle');
let paused=false,inView=true;
function state(){const disabled=paused||reduced.matches||navigator.connection?.saveData||document.hidden;document.body.classList.toggle('motion-on',!disabled);document.body.classList.toggle('hero-active',inView);if(button){button.setAttribute('aria-pressed',String(paused));button.textContent=paused?'Включить движение':reduced.matches?'Движение отключено системой':'Остановить движение';button.disabled=reduced.matches;}}
button?.addEventListener('click',()=>{paused=!paused;state();});
reduced.addEventListener('change',state);document.addEventListener('visibilitychange',state);
if('IntersectionObserver' in window){const hero=document.querySelector('.hero');if(hero)new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;state();}).observe(hero);
 const io=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('arrived');io.unobserve(e.target);}}),{threshold:.12});
 document.querySelectorAll('.section-heading,.project-strip,.documents-band,.start').forEach(el=>io.observe(el));}
state();
