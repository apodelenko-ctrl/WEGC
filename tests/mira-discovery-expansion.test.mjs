import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {validateDiscovery,combineProjects,filterProjects,marketFromPath,safeReturnPath,safeSelection} from '../mira/catalog/markets/market-core.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL(p,import.meta.url)));
const base=read('../mira/catalog/data.json').projects,old=read('../mira/catalog/markets/data.json'),fresh=read('../mira/catalog/markets/discovery.json');
test('three cohorts remain distinct: 618 + 30 + 30 unique IDs',()=>{
 assert.equal(base.length,618);assert.equal(old.projects.length,30);assert.equal(validateDiscovery(fresh).projects.length,30);
 const all=combineProjects(base,old,fresh);assert.equal(all.length,678);assert.equal(new Set(all.map(p=>p.id)).size,678);
});
test('explicit mixed and hotel taxonomy does not change original formats',()=>{
 const rows=fresh.projects;assert.equal(rows.find(p=>p.id==='me-montis-mountain-resort').kind,'hotel');
 assert.ok(filterProjects(rows,{kind:'hotel'}).every(p=>p.market==='montenegro'));
 assert.ok(filterProjects(rows,{kind:'mixed'}).some(p=>p.id==='vn-the-global-city'));
 const input=read('../project-bible/mira/data/markets/vietnam-montenegro-30.json').projects;
 for(const p of rows)assert.deepEqual(p.propertyTypes,input.find(x=>x.id===p.id).propertyTypes);
});
test('new deep links and return paths preserve the correct country',()=>{
 for(const [market,id] of [['vietnam','vn-lumi-hanoi'],['montenegro','me-boka-place']]){
  assert.equal(marketFromPath(`/mira/catalog/projects/${id}/`),market);
  assert.equal(safeReturnPath(`/mira/catalog/${market}/?q=test`,market),`/mira/catalog/${market}/?q=test`);
  assert.equal(safeReturnPath('/mira/catalog/bali/',market),null);
 }
});
test('all five countries survive shared selection validation',()=>{
 const all=combineProjects(base,old,fresh),ids=[base[0].id,'bali-origins-nuanu','dubai-orla','vn-lumi-hanoi','me-boka-place'];
 assert.deepEqual(safeSelection(ids,all),ids);
});
test('discovery rejects invented commercial fields, media and seller',()=>{
 for(const [k,v] of [['price',100],['roi',9],['commission',2],['legalSeller','unchecked'],['image','https://example.com/project.jpg'],['commerciallyEnabled',true],['commercialStatus','active']]){
  const d=structuredClone(fresh);d.projects[0][k]=v;assert.throws(()=>validateDiscovery(d));
 }
});
test('discovery rejects duplicate IDs, missing records and unsafe URLs',()=>{
 let d=structuredClone(fresh);d.projects[1].id=d.projects[0].id;assert.throws(()=>validateDiscovery(d));
 d=structuredClone(fresh);d.projects.pop();assert.throws(()=>validateDiscovery(d));
 d=structuredClone(fresh);d.projects[0].sourceURL='https://u:p@example.com/';assert.throws(()=>validateDiscovery(d));
});
test('daily corrections keep precisely 3 partials and no verified seller',()=>{
 assert.deepEqual(fresh.projects.filter(p=>p.metadataStatus==='partial_for_validation').map(p=>p.id).sort(),['me-merit-starlit','me-porto-budva','vn-waterpoint']);
 assert.equal(fresh.projects.find(p=>p.id==='vn-lumi-hanoi').developerGroup,'CapitaLand Group');
 assert.ok(fresh.projects.every(p=>p.legalSeller===null));
});
