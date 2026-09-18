/** Pure catalogue expansion helpers. No auth, network writes or commercial activation. */
export const MARKETS=Object.freeze({phuket:{name:'Пхукет',country:'Таиланд',path:'/mira/catalog/'},bali:{name:'Бали',country:'Индонезия',path:'/mira/catalog/bali/'},dubai:{name:'Дубай',country:'ОАЭ',path:'/mira/catalog/dubai/'},vietnam:{name:'Вьетнам',country:'Вьетнам',path:'/mira/catalog/vietnam/'},montenegro:{name:'Черногория',country:'Черногория',path:'/mira/catalog/montenegro/'}});
export const PROPERTY_TYPES=Object.freeze({apartment:'Апартаменты',studio:'Студии',villa:'Виллы',townhouse:'Таунхаусы',penthouse:'Пентхаусы',duplex:'Дуплексы',hotel_suite:'Гостиничные номера',serviced_apartment:'Сервисные апартаменты'});
export const PAGE_SIZE=24,MAX_SELECTION=12;
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
export const normalize=x=>String(x||'').normalize('NFKC').toLocaleLowerCase('ru').replace(/ё/g,'е').trim();
export function marketFromPath(path){const p=String(path).split('?')[0];for(const [m,prefix] of [['bali','bali'],['dubai','dubai'],['vietnam','vn'],['montenegro','me']])if(p.startsWith(`/mira/catalog/${m}/`)||p.startsWith(`/mira/catalog/projects/${prefix}-`))return m;return 'phuket';}
export function isCatalogueIndex(path){return /^\/mira\/catalog\/(?:bali\/|dubai\/|vietnam\/|montenegro\/)?(?:index\.html)?$/.test(path);}
export function safeReturnPath(value,market='phuket',origin='https://wegc.fund'){
 if(!own(MARKETS,market)||typeof value!=='string'||value.length>3000||!value.startsWith('/')||value.startsWith('//'))return null;
 try{const u=new URL(value,origin);return u.origin===origin&&isCatalogueIndex(u.pathname)&&marketFromPath(u.pathname)===market?u.pathname+u.search:null;}catch{return null;}
}
export function validateExpansion(d){
 if(!d||d.schemaVersion!==1||d.mode!=='public_research'||!Array.isArray(d.projects)||d.projects.length!==30||d.source?.recordCount!==30||d.source?.commerciallyEnabled!==0)throw Error('Invalid expansion envelope');
 const ids=new Set(),counts={bali:0,dubai:0};
 for(const p of d.projects){
  if(!p||!own(counts,p.market)||!new RegExp(`^${p.market}-[a-z0-9-]{1,170}$`).test(p.id)||ids.has(p.id))throw Error('Invalid project identity');ids.add(p.id);counts[p.market]++;
  for(const k of ['name','district','family','summary','typeLabel'])if(typeof p[k]!=='string'||!p[k].trim()||p[k].length>1500)throw Error('Missing description');
  if(p.commerciallyEnabled!==false||p.legalSeller!==null||p.availabilityStatus!=='on_request')throw Error('Unverified sale activation');
  for(const k of ['price','roi','availableUnits','bookingEnabled','commission','priceFrom'])if(own(p,k))throw Error('Unsupported commercial field');
  if(!Array.isArray(p.propertyTypes)||!p.propertyTypes.length||p.propertyTypes.some(t=>!own(PROPERTY_TYPES,t))||new Set(p.propertyTypes).size!==p.propertyTypes.length)throw Error('Invalid property types');
  if(!Array.isArray(p.amenities)||p.amenities.some(a=>typeof a!=='string'||a.length>200))throw Error('Invalid amenities');
  const u=new URL(p.sourceURL);if(u.protocol!=='https:'||u.username||u.password)throw Error('Invalid primary source');
  if(p.image!==null&&!new RegExp(`^/images/mira-markets/${p.market}/[a-z0-9-]+\\.webp$`).test(p.image))throw Error('Invalid image location');
 }
 if(counts.bali!==15||counts.dubai!==15)throw Error('Invalid market counts');return d;
}
export function validateDiscovery(d){
 if(!d||d.schemaVersion!==1||d.mode!=='public_research'||!Array.isArray(d.projects)||d.projects.length!==30||d.source?.recordCount!==30||d.source?.commerciallyEnabled!==0)throw Error('Invalid discovery envelope');
 const ids=new Set(),counts={vietnam:0,montenegro:0};
 for(const p of d.projects){
  const prefix=p&&own(counts,p.market)?{vietnam:'vn',montenegro:'me'}[p.market]:null;
  if(!prefix||!new RegExp(`^${prefix}-[a-z0-9-]{1,170}$`).test(p.id)||ids.has(p.id))throw Error('Invalid discovery identity');ids.add(p.id);counts[p.market]++;
  if(!['condo','villa','mixed','hotel'].includes(p.kind)||!Array.isArray(p.propertyTypes)||!p.propertyTypes.length||p.propertyTypes.some(t=>typeof t!=='string'||!/^[a-z_ -]{1,100}$/.test(t)))throw Error('Invalid discovery taxonomy');
  for(const k of ['name','district','family','summary','typeLabel'])if(typeof p[k]!=='string'||!p[k].trim()||p[k].length>1500)throw Error('Missing discovery description');
  if(p.commerciallyEnabled!==false||p.legalSeller!==null||p.commercialStatus!=='research_only'||p.availabilityStatus!=='on_request')throw Error('Unverified discovery sale activation');
  for(const k of ['price','roi','availableUnits','bookingEnabled','commission','priceFrom'])if(own(p,k))throw Error('Unsupported commercial field');
  const u=new URL(p.sourceURL);if(u.protocol!=='https:'||u.username||u.password)throw Error('Invalid discovery source');
  if(p.image!==null)throw Error('Discovery media not approved');
 }
 if(counts.vietnam!==15||counts.montenegro!==15)throw Error('Invalid discovery counts');return d;
}
export function combineProjects(base,extra,discovery=null){
 if(!Array.isArray(base)||base.length!==618)throw Error('Phuket source not reconciled');
 const all=[...base.map(p=>({...p,market:'phuket'})),...validateExpansion(extra).projects,...(discovery?validateDiscovery(discovery).projects:[])];
 if(new Set(all.map(p=>p.id)).size!==all.length)throw Error('Duplicate cross-market identifier');return all;
}
export function marketProjects(all,market){if(!own(MARKETS,market))return [];return all.filter(p=>(p.market||'phuket')===market);}
export function filterProjects(all,state={}){const words=normalize(state.q).split(/\s+/).filter(Boolean);return all.filter(p=>(!state.district||p.district===state.district)&&(!state.family||p.family===state.family)&&(!state.kind||(['vietnam','montenegro'].includes(p.market)?p.kind===state.kind:(p.propertyTypes?p.propertyTypes.includes(state.kind):p.kind===state.kind)))&&words.every(w=>normalize([p.name,p.district,p.family,p.summary].filter(Boolean).join(' ')).includes(w)));}
export function paginate(all,n=1){const pages=Math.max(1,Math.ceil(all.length/PAGE_SIZE)),page=Math.max(1,Math.min(pages,Math.floor(Number(n)||1)));return {items:all.slice((page-1)*PAGE_SIZE,page*PAGE_SIZE),page,pages,total:all.length};}
export function safeSelection(value,all){if(!Array.isArray(value))return [];const valid=new Set(all.map(p=>p.id));return [...new Set(value.filter(id=>typeof id==='string'&&valid.has(id)))].slice(0,MAX_SELECTION);}
export function toggleSelection(selection,id,all){const s=safeSelection(selection,all);if(s.includes(id))return s.filter(x=>x!==id);if(s.length>=MAX_SELECTION||!all.some(p=>p.id===id))return s;return [...s,id];}
