/** DOM harness, not a rendered browser test. All input values are synthetic. */
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {intakeClient} from '../cloudflare-worker/mira/intake-ui.mjs';
function harness({stored=null,storageFails=false,responses=[],paused=false}={}){
 const el=()=>({hidden:false,disabled:false,textContent:'',events:{},addEventListener(name,fn){this.events[name]=fn;}});
 const form={...el(),dataset:{consent:'test-v1',paused:String(paused)},reportValidity:()=>true},message=el(),send=el(),refresh=el();
 const fields={company:'TEST',city:'TEST',name:'TEST',email:'synthetic@example.test','cf-turnstile-response':'synthetic-challenge'};
 const nodes={request:form,message,send,refresh},requests=[];let reset=0;
 const storage={value:stored?JSON.stringify(stored):null,getItem(){return this.value;},setItem(k,v){if(storageFails)throw Error('disabled');this.value=v;}};
 const context={document:{getElementById:id=>nodes[id]},crypto,sessionStorage:storage,FormData:class{get(k){return fields[k];}},window:{turnstile:{reset(){reset++;}}},fetch:async(url,init)=>{requests.push({url,...init});const r=responses.shift();if(r instanceof Error)throw r;return Response.json(r?.body||{id:'test-id',status:'received',response:null},{status:r?.status||201});}};
 vm.runInNewContext(intakeClient,context);
 return{...nodes,fields,requests,storage,get reset(){return reset;},submit:()=>form.events.submit({preventDefault(){}}),refreshStatus:()=>refresh.events.click()};
}
test('client records receipt only after server success; no token in URL',async()=>{
 const h=harness();await h.submit();assert.equal(h.request.hidden,true);assert.equal(h.refresh.hidden,false);assert.match(h.message.textContent,/test-id/);assert.equal(h.requests[0].url,'/mira/request/submit');assert.match(h.requests[0].headers.Authorization,/^Bearer [0-9a-f]{64}$/);assert.equal(h.requests[0].credentials,'omit');assert.equal(JSON.parse(h.storage.value).id,'test-id');
});
test('network retry preserves key and receipt secret, with no false success',async()=>{
 const h=harness({responses:[Error('connection lost'),{status:201,body:{id:'test-id',status:'received'}}]});await h.submit();assert.equal(h.request.hidden,false);assert.equal(JSON.parse(h.storage.value).id,null);await h.submit();assert.equal(h.requests[0].headers['Idempotency-Key'],h.requests[1].headers['Idempotency-Key']);assert.equal(h.requests[0].headers.Authorization,h.requests[1].headers.Authorization);assert.equal(h.reset,1);
});
test('operator text displayed literally; refresh uses secret-bearing POST',async()=>{
 const h=harness({responses:[{body:{id:'test-id',status:'received'}},{status:200,body:{id:'test-id',status:'responded',response:'<img src=x onerror=alert(1)>'}}]});await h.submit();await h.refreshStatus();assert.match(h.message.textContent,/<img src=x onerror=alert\(1\)>/);assert.equal(h.requests[1].method,'POST');assert.equal(h.requests[1].url,'/mira/request/status');assert.equal(h.refresh.disabled,false);
});
test('reload restores only receipt metadata without resubmitting',()=>{
 const stored={key:crypto.randomUUID(),token:'a'.repeat(64),id:'saved-test-id'},h=harness({stored});assert.equal(h.request.hidden,true);assert.equal(h.refresh.hidden,false);assert.match(h.message.textContent,/saved-test-id/);assert.equal(h.requests.length,0);
});
test('storage denied retains current-tab status and email contact path',async()=>{
 const h=harness({storageFails:true});await h.submit();assert.equal(h.request.hidden,true);assert.match(h.message.textContent,/email/);assert.doesNotMatch(h.message.textContent,/Хранилище|секретн/);await h.refreshStatus();assert.equal(h.requests.length,2);
});
test('missing challenge and invalid form never call the API',async()=>{
 const h=harness();h.fields['cf-turnstile-response']='';await h.submit();assert.equal(h.requests.length,0);h.fields['cf-turnstile-response']='test';h.request.reportValidity=()=>false;await h.submit();assert.equal(h.requests.length,0);
});
test('paused client blocks a new submission but restores and refreshes a receipt',async()=>{
 const h=harness({paused:true,stored:{key:crypto.randomUUID(),token:'a'.repeat(64),id:'saved-test-id'},responses:[{status:200,body:{id:'saved-test-id',status:'responded',response:'TEST reply'}}]});
 await h.submit();assert.equal(h.requests.length,0);assert.match(h.message.textContent,/приостановлен/);
 await h.refreshStatus();assert.equal(h.requests.length,1);assert.match(h.message.textContent,/TEST reply/);
});
