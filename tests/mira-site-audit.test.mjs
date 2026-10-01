import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import path from 'node:path';
const {resolveReference,shouldIgnore}=createRequire(import.meta.url)('../scripts/audit-site.js');
const root=process.cwd(), page=path.join(root,'mira/catalog/index.html');
test('audit resolves versioned assets and query plus encoded fragments without hiding missing files',()=>{
 assert.deepEqual(resolveReference('../catalog/catalog.css?v=123',page),{path:path.join(root,'mira/catalog/catalog.css'),anchor:''});
 assert.deepEqual(resolveReference('?q=foo#main',page),{path:page,anchor:'main'});
 assert.deepEqual(resolveReference('/mira/go/?utm_source=test#st%61rt',page),{path:path.join(root,'mira/go/index.html'),anchor:'start'});
 assert.equal(resolveReference('missing.css?v=123',page).path,path.join(root,'mira/catalog/missing.css'));
 assert.equal(shouldIgnore('//example.com/file'),true);
 assert.equal(shouldIgnore('/mira/go/#start'),false);
});
