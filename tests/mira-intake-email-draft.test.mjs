import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {intakeEmailDraft,intakeAdminClient} from '../cloudflare-worker/mira/intake-admin-ui.mjs';
import {intakePage} from '../cloudflare-worker/mira/intake-ui.mjs';
test('email draft preserves complete reviewed text and exact recipient without sending',()=>{
 const reply='Здравствуйте!\nУсловия A & B: обсудим проект.';
 const d=intakeEmailDraft('agency+test@example.test','request-123',reply),u=new URL(d.href);
 assert.equal(decodeURIComponent(u.pathname),'agency+test@example.test');assert.equal(u.searchParams.get('subject'),d.subject);assert.equal(u.searchParams.get('body'),d.body);assert.ok(d.body.startsWith(reply));assert.equal(d.to,'agency+test@example.test');assert.equal(u.protocol,'mailto:');
});
test('email draft refuses multiple recipients, header injection and empty reply',()=>{
 for(const email of ['a@example.test,b@example.test','a@example.test; b@example.test','a@example.test\r\nBcc:other@example.test'])assert.throws(()=>intakeEmailDraft(email,'request-123','Ответ'));
 assert.throws(()=>intakeEmailDraft('a@example.test','request-123','  '));assert.throws(()=>intakeEmailDraft('a@example.test','request-123','x'.repeat(2001)));
});
test('browser operator client is valid JavaScript with the same draft helper',()=>{assert.doesNotThrow(()=>new vm.Script('(async()=>{'+intakeAdminClient+'})'));assert.ok(intakeAdminClient.includes(intakeEmailDraft.toString()));});
test('public form is email-first and keeps Russian Turnstile protection',()=>{
 const page=intakePage({PUBLIC_INTAKE_PRIVACY_VERSION:'test',PUBLIC_INTAKE_PRIVACY_NOTICE_URL:'/privacy',TURNSTILE_SITE_KEY:'test'});
 assert.match(page,/по рабочему email/);assert.doesNotMatch(page,/Автоматические письма|секретного ключа|Сохраняйте эту вкладку/);assert.match(page,/data-language="ru"/);assert.match(page,/data-appearance="interaction-only"/);assert.match(page,/cf-turnstile/);
});
