import copy
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

import import_registry as imp

HERE=Path(__file__).parent
SCHEMA_ROOT=Path(os.environ.get('MIRA_SCHEMA_ROOT',str(HERE.parent/'source/cloudflare-worker/mira/migrations')))
SHA='a'*40

def fixture():
    agencies={'records':[
      {'agency_id':'a1','brand':"Agency O'Brien; DROP TABLE mira_applications; --",'city':'Test',
       'legacy_ids':['old-a1'],'general_email':None,'field_evidence':[
        {'field':'general_email','value':None,'verification_status':'not_found','source_url':'https://example.invalid/contact','checked_at':'2026-09-21T00:00:00Z'}],
       'direct_business_phone':'synthetic-phone','outreach_status':'not_authorized'},
      {'agency_id':'a2','brand':'Synthetic second','city':'Test','legacy_ids':[],'field_evidence':[]}]}
    developers=[{'developer_id':'d1','name':'Synthetic developer','contacts':[
       {'kind':'telegram','value':'https://t.me/synthetic','verification_status':'not_checked','direct_dialogue_verified':False}],
       'agreement_status':'unknown'}]
    links=[{'project_id':'p1','market':'phuket','developer_id':'d1','candidate_developer_ids':['d1'],
            'mapping_status':'inherited_group_match_needs_verification','legal_seller_verified':False,'contract_covered':None},
           {'project_id':'p2','market':'phuket','developer_id':None,'candidate_developer_ids':[],
            'mapping_status':'unresolved_no_family'}]
    native={'private_only':True,'rows':[
      {'crm_account_id':'n1','native_external_id':'legacy-a1','entity_type':'agency',
       'canonical_research_ids':['old-a1'],'status':'exact_stable_or_legacy_id'},
      {'crm_account_id':'n2','native_external_id':'legacy-d1','entity_type':'developer',
       'canonical_research_ids':['d1'],'status':'exact_native_source_hash_id',
       'canonical_registry_status':'domain_candidate_requires_entity_review','candidates':[{'developer_id':'d1'}]}]}
    return agencies,developers,links,native

class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'test.sqlite'
        self.db=sqlite3.connect(self.path)
        for name in ('0001_mira.sql','0002_operations.sql','0003_materials.sql'):
            self.db.executescript((SCHEMA_ROOT/name).read_text())
        self.db.execute("INSERT INTO mira_agencies(id,name,city,status,created_at) VALUES('existing','Existing agency','Test','pending','2026-09-21')")
        self.db.commit()
        self.before=self.operational_dump()
        self.db.executescript(imp.immutable_schema((HERE/'schema.base.sql').read_text()))
        self.a,self.d,self.p,self.n=fixture()

    def tearDown(self):self.db.close();self.temp.cleanup()
    def operational_dump(self):
        names=[r[0] for r in self.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        return {n:self.db.execute('SELECT * FROM '+n).fetchall() for n in names if not n.startswith(('mira_import','mira_research','mira_native'))}
    def build(self,native=True):return imp.build(self.a,self.d,self.p,SHA,self.n if native else None)
    def apply(self,native=True):
        sql,report,data=self.build(native);self.db.executescript(sql);return sql,report,data

    def test_existing_operational_data_and_schema_preserved(self):
        before_schema=self.db.execute("SELECT sql FROM sqlite_master WHERE name='mira_agencies'").fetchone()
        self.apply();self.assertEqual(self.before,self.operational_dump())
        self.assertEqual(before_schema,self.db.execute("SELECT sql FROM sqlite_master WHERE name='mira_agencies'").fetchone())

    def test_repeat_identical_import_no_duplicate_or_activation(self):
        sql,r,_=self.apply();self.db.executescript(sql)
        self.assertTrue(imp.verify(self.path,r['snapshot_id'])['passed'])
        self.assertEqual(1,self.db.execute('SELECT count(*) FROM mira_import_commits').fetchone()[0])
        self.assertEqual(0,self.db.execute("SELECT count(*) FROM mira_agencies WHERE status='active'").fetchone()[0])

    def test_interrupted_snapshot_hidden_then_replay_completes(self):
        sql,r,_=self.build();self.db.executescript(sql.rsplit('INSERT INTO mira_import_commits',1)[0])
        self.assertEqual(0,self.db.execute('SELECT count(*) FROM mira_published_research_entities').fetchone()[0])
        self.assertFalse(imp.verify(self.path,r['snapshot_id'])['passed'])
        self.db.executescript(sql);self.assertEqual(3,self.db.execute('SELECT count(*) FROM mira_published_research_entities').fetchone()[0])

    def test_incomplete_commit_rejected(self):
        sql,r,_=self.build();self.db.executescript(sql.splitlines()[0])
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute('INSERT INTO mira_import_commits VALUES(?)',(r['snapshot_id'],))

    def test_payload_edit_and_delete_rejected(self):
        self.apply()
        for sql in ["UPDATE mira_research_entities SET name='changed'",'DELETE FROM mira_research_entities']:
            with self.assertRaises(sqlite3.IntegrityError):self.db.execute(sql)

    def test_new_row_cannot_be_added_to_published_snapshot(self):
        _,r,_=self.apply()
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO mira_research_entities VALUES(?, 'agency','unexpected','Name',NULL,NULL,NULL,'{}','hash')",(r['snapshot_id'],))

    def test_changed_source_creates_new_snapshot_preserves_history(self):
        _,first,_=self.apply();self.a['records'][0]['brand']='Updated name'
        _,second,_=self.apply();self.assertNotEqual(first['snapshot_id'],second['snapshot_id'])
        self.assertEqual(2,self.db.execute('SELECT count(*) FROM mira_import_commits').fetchone()[0])
        self.assertEqual(6,self.db.execute('SELECT count(*) FROM mira_research_entities').fetchone()[0])

    def test_native_agency_legacy_resolves_but_developer_candidate_does_not(self):
        self.apply();rows=dict(self.db.execute('SELECT crm_account_id,resolved_source_id FROM mira_native_lineage'))
        self.assertEqual({'n1':'a1','n2':None},rows)
        self.assertEqual(1,self.db.execute("SELECT count(*) FROM mira_native_lineage WHERE row_json LIKE '%domain_candidate_requires_entity_review%'").fetchone()[0])

    def test_no_private_lineage_in_public_build(self):
        sql,r,_=self.build(False);self.assertFalse(r['contains_private']);self.assertEqual(0,r['expected']['native_lineage'])
        self.assertNotIn('legacy-d1',sql);self.assertNotIn('domain_candidate_requires_entity_review',sql)

    def test_duplicate_and_broken_identity_rejected(self):
        self.a['records'].append(copy.deepcopy(self.a['records'][0]))
        with self.assertRaises(ValueError):self.build()
        self.a,self.d,self.p,self.n=fixture();self.n['rows'][0]['canonical_research_ids']=['absent']
        with self.assertRaises(ValueError):self.build()

    def test_unknown_project_developer_rejected(self):
        self.p[0]['developer_id']='missing'
        with self.assertRaises(ValueError):self.build()

    def test_duplicate_native_id_rejected(self):
        self.n['rows'][1]['crm_account_id']='n1'
        with self.assertRaises(ValueError):self.build()

    def test_null_field_status_and_public_contact_not_dialogue_preserved(self):
        self.apply()
        self.assertEqual(('null','not_found'),self.db.execute("SELECT value_json,verification_status FROM mira_research_fields WHERE source_id='a1' AND field_key='general_email'").fetchone())
        scopes=dict(self.db.execute("SELECT field_key,conversation_scope FROM mira_research_fields WHERE source_id IN ('a1','d1')"))
        self.assertEqual('published_work_contact_not_dialogue',scopes['direct_business_phone'])
        self.assertEqual('public_contact_not_dialogue',scopes['contact:telegram'])

    def test_original_records_and_project_ids_roundtrip(self):
        self.apply()
        self.assertEqual(self.a['records'][0],json.loads(self.db.execute("SELECT row_json FROM mira_research_entities WHERE source_id='a1'").fetchone()[0]))
        self.assertEqual({'p1','p2'},{r[0] for r in self.db.execute('SELECT project_id FROM mira_research_project_links')})
        row=json.loads(self.db.execute("SELECT row_json FROM mira_research_project_links WHERE project_id='p1'").fetchone()[0])
        self.assertIsNone(row['contract_covered']);self.assertFalse(row['legal_seller_verified'])

    def test_wrong_database_fails_before_creating_research_tables(self):
        other=sqlite3.connect(':memory:')
        with self.assertRaises(sqlite3.OperationalError):other.executescript(imp.immutable_schema((HERE/'schema.base.sql').read_text()))
        self.assertEqual([],other.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall());other.close()

    def test_oversized_sql_record_rejected(self):
        self.a['records'][0]['untrusted_note']='x'*100000
        with self.assertRaises(ValueError):self.build()

if __name__=='__main__':unittest.main()
