/** Fixed-choice local qualification. No remote submissions. */
const form=document.querySelector('#brief-form'),plan=document.querySelector('#brief-result');
const choices={experience:['new','existing','thailand'],demand:['learning','current','team'],market:['phuket','bali']};
if(form){
 form.querySelector('fieldset').disabled=false;
 form.addEventListener('change',()=>{plan.hidden=true;});
 form.addEventListener('submit',event=>{
  event.preventDefault();
  const fields=new FormData(form),experience=fields.get('experience'),demand=fields.get('demand'),market=fields.get('market');
  if(!Object.entries(choices).every(([key,values])=>values.includes(fields.get(key))))return;
  const destination=market==='bali'?'Бали':'Пхукете';
  const next=demand==='current'
   ?`Выберите подходящие проекты на ${destination} и подайте заявку агентства. Команда МИРА свяжется с вами по email, уточнит задачу и согласует актуальное предложение, регистрацию клиента и комиссию.`
   :demand==='team'
    ?'Подайте заявку агентства. Обсудим задачи вашей команды, познакомим с проектами и согласуем условия сотрудничества.'
    :experience==='thailand'
     ?'Выберите проекты или этап сделки, с которым нужна помощь. Подайте заявку агентства — обсудим вашу задачу и порядок совместной работы.'
     :'Посмотрите проекты и условия сотрудничества. Подайте заявку агентства — команда МИРА поможет выбрать первый шаг для вашего зарубежного направления.';
  plan.querySelector('p').textContent=next;
  plan.querySelector('#plan-catalogue').href=market==='bali'?'/mira/catalog/bali/':'/mira/catalog/';
  plan.hidden=false;plan.focus();
 });
}
const sticky=document.querySelector('.sticky-action'),hero=document.querySelector('.hero'),start=document.querySelector('#start');
if(sticky&&hero&&'IntersectionObserver'in window){let heroOn=true,startOn=false;const obs=new IntersectionObserver(entries=>{for(const e of entries){if(e.target===hero)heroOn=e.isIntersecting;if(e.target===start)startOn=e.isIntersecting;}sticky.hidden=heroOn||startOn;});obs.observe(hero);if(start)obs.observe(start);}
