/** MIRA MVP domain rules. Demo drafts are never developer registrations. */
export const UNKNOWN = 'Не подтверждено';
export const labels = Object.freeze({draft_local:'Локальный демо-черновик',submitted:'Получено МИРА',review:'Проверка МИРА',needs_information:'Нужно уточнение',developer_submitted:'Передано застройщику',developer_confirmed:'Подтверждено застройщиком',duplicate:'Дубликат',conflict:'Спор',rejected:'Отклонено',closed:'Закрыто',requested:'Запрошено',cancelled:'Отменено'});
export function text(value){ return value == null || value === '' ? UNKNOWN : String(value); }
export function safeURL(value, base='https://wegc.fund') {
  try { const u = new URL(value,base); return ['https:','http:'].includes(u.protocol) && !u.username && !u.password ? u.href : null; } catch { return null; }
}
export function filterProjects(projects, filters={}) {
  const q = (filters.search || '').trim().toLocaleLowerCase('ru');
  return projects.filter(p => (!filters.district || p.district === filters.district) && (!filters.kind || p.kind === filters.kind) && (!filters.developerFamily || p.developerFamily === filters.developerFamily) && (!q || [p.name,p.district,p.developerFamily].join(' ').toLocaleLowerCase('ru').includes(q)));
}
export function createDemoLead(project, reference, existing, now=new Date().toISOString()) {
  if (!project?.id) throw new Error('Выберите проект.');
  if (!/^DEMO-[A-Z0-9-]{1,40}$/i.test(reference)) throw new Error('В демо разрешены только условные ID вида DEMO-CLIENT-1. Не вводите данные клиента.');
  const clientRef=reference.toUpperCase();
  if (existing.some(x=>x.projectId===project.id && x.clientRef===clientRef)) throw new Error('Такой демо-черновик уже есть для этого проекта.');
  return {id:crypto.randomUUID(),environment:'demo',projectId:project.id,projectName:project.name,clientRef,status:'draft_local',createdAt:now,protection:{status:'unconfirmed',until:null,evidence:null},deal:{status:'not_started'},commission:{status:'not_accrued',amount:null,currency:null},history:[{at:now,status:'draft_local',note:'Создано только в этом браузере. Не отправлено МИРА или застройщику.'}]};
}
export function createDemoPayment(lead, now=new Date().toISOString()) {
  if (!lead || lead.environment !== 'demo') throw new Error('Выберите демо-черновик клиента.');
  return {id:crypto.randomUUID(),leadId:lead.id,environment:'demo',status:'draft_local',createdAt:now,quote:null,execution:null};
}
export function canRegister(project, now=Date.now()) {
  const g=project?.registrationGate;
  return Boolean(g?.enabled===true && g.legalSeller && g.termsRef && g.registrationRulesRef && g.inventoryRef && g.verifiedAt && g.expiresAt && Date.parse(g.verifiedAt)<=now && Date.parse(g.expiresAt)>now);
}
export function protectionLabel(lead, now=Date.now()) {
  const p=lead.protection;
  if (lead.status !== 'developer_confirmed' || p?.status !== 'confirmed' || !p.evidence || !p.until) return 'Не подтверждена застройщиком';
  return Date.parse(p.until)>now ? `Подтверждена до ${p.until}` : 'Срок истёк / нужна повторная проверка';
}
