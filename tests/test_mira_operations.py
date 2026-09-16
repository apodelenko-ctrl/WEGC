import copy
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ops',ROOT/'scripts/mira-launch-operations.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
NOW=datetime(2026,9,16,12,tzinfo=timezone.utc)
KNOWN={'agency':{'RU-A-synthetic'},'developer':{'PHK-D-synthetic'}}

def event(stage='qualified',**kw):
    base={'id':'EVT-one','entity_type':'agency','entity_id':'RU-A-synthetic','stage':stage,'occurred_at':'2026-09-16T10:00:00Z','operator_ref':'OP-test','evidence_ref':'EVID-test','previous_event_id':None,'mode':'observation','next_action':'request_evidence'}
    return dict(base,**kw)

def journal(*events): return {'schema_version':1,'events':list(events)}

class OperatorTests(unittest.TestCase):
    def test_empty_does_not_invent_operations(self):
        last,reached=m.validate_journal(journal(),KNOWN,NOW)
        self.assertEqual(last,{});self.assertEqual(dict(reached),{})
    def test_historical_observation_does_not_backfill_stages(self):
        _,reached=m.validate_journal(journal(event('contract')),KNOWN,NOW)
        self.assertEqual(set(reached),{('agency','contract')})
    def test_transition_and_distinct_entity_count(self):
        one=event();two=event('contact_verified',id='EVT-two',previous_event_id=one['id'],mode='transition')
        last,reached=m.validate_journal(journal(one,two),KNOWN,NOW)
        self.assertEqual(last[('agency','RU-A-synthetic')]['stage'],'contact_verified')
        self.assertEqual(len(reached[('agency','contact_verified')]),1)
    def test_skipped_transition_rejected_but_explicit_observation_allowed(self):
        one=event();two=event('contract',id='EVT-two',previous_event_id=one['id'],mode='transition')
        with self.assertRaises(ValueError):m.validate_journal(journal(one,two),KNOWN,NOW)
        two['mode']='observation';m.validate_journal(journal(one,two),KNOWN,NOW)
    def test_unknown_entities_and_raw_pii_rejected(self):
        for item in [event(entity_id='RU-A-other'),dict(event(),email='synthetic@example.test'),event(entity_id=[]),event(operator_ref='person@example.test')]:
            with self.assertRaises(ValueError):m.validate_journal(journal(item),KNOWN,NOW)
    def test_no_duplicate_or_broken_chain(self):
        with self.assertRaises(ValueError):m.validate_journal(journal(event(),event()),KNOWN,NOW)
        with self.assertRaises(ValueError):m.validate_journal(journal(event(previous_event_id='EVT-missing')),KNOWN,NOW)
    def test_time_requires_zone_and_not_future(self):
        for when in ['2026-09-16T10:00:00','2026-09-17T10:00:00Z']:
            with self.assertRaises(ValueError):m.validate_journal(journal(event(occurred_at=when)),KNOWN,NOW)
    def test_external_observation_requires_approval_reference(self):
        with self.assertRaises(ValueError):m.validate_journal(journal(event('contacted')),KNOWN,NOW)
        m.validate_journal(journal(event('contacted',approval_ref='APR-owner')),KNOWN,NOW)
    def test_hold_cannot_advance_and_requires_resume(self):
        one=event();hold=event(id='EVT-two',previous_event_id=one['id'],mode='hold')
        step=event('contact_verified',id='EVT-three',previous_event_id=hold['id'],mode='transition')
        with self.assertRaises(ValueError):m.validate_journal(journal(one,hold,step),KNOWN,NOW)
        resume=event(id='EVT-three',previous_event_id=hold['id'],mode='resume')
        step.update(id='EVT-four',previous_event_id=resume['id'])
        m.validate_journal(journal(one,hold,resume,step),KNOWN,NOW)
    def test_append_only_rejects_edits_and_deletions(self):
        old=journal(event());new=journal(event(),event('contact_verified',id='EVT-two',previous_event_id='EVT-one'))
        m.require_append_only(old,new)
        with self.assertRaises(ValueError):m.require_append_only(old,journal())
        new['events'][0]['evidence_ref']='EVID-changed'
        with self.assertRaises(ValueError):m.require_append_only(old,new)
    def test_manifest_protects_manual_next_action(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);reg=root/m.REGISTER;reg.parent.mkdir(parents=True);reg.write_text('stage,operator\nidentified,\n')
            manifest=root/m.MANIFEST;manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({'generated_register_sha256':m.sha(reg.read_bytes())}))
            m.protect_generated_register(root)
            reg.write_text('stage,operator\nsigned,OP-test\n')
            with self.assertRaises(ValueError):m.protect_generated_register(root)
    def test_first_build_does_not_overwrite_unmigrated_operator_state(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);reg=root/m.REGISTER;reg.parent.mkdir(parents=True);reg.write_text('stage,operator\nsigned,OP-test\n')
            with self.assertRaises(ValueError):m.protect_generated_register(root)
    def test_private_overlay_refuses_repo_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaises(ValueError):m.private_overlay(root,root/'state.json',root.parent/'output',NOW)
            with self.assertRaises(ValueError):m.private_overlay(root,root.parent/'state.json',root/'output',NOW)
    def test_public_augmentation_has_19_product_rows_and_unknown_business(self):
        data=json.loads((ROOT/m.OPS/'launch-dashboard.json').read_text())
        self.assertEqual(len(m.product_rows(ROOT)),19)
        self.assertFalse(data['readiness']['marketplace_pilot'])
        self.assertTrue(all(v['value'] is None for v in data['operations'].values()))
    def test_private_overlay_persists_without_touching_public_register(self):
        before=(ROOT/m.REGISTER).read_bytes()
        agency=m.read_csv(ROOT/m.BASE/'sales/russia-launch-100-quality.csv')[0]['agency_id']
        with tempfile.TemporaryDirectory() as d:
            state=Path(d)/'source.json';out=Path(d)/'render'
            payload=journal(event('contract',entity_id=agency));state.write_text(json.dumps(payload))
            a=m.private_overlay(ROOT,state,out,NOW);b=m.private_overlay(ROOT,state,out,NOW)
            self.assertEqual(a,b);self.assertEqual(len(a['operator_stage_observations']),1)
            self.assertTrue(all(x['value'] is None for x in a['operations'].values()))
            self.assertFalse(a['readiness']['marketplace_pilot'])
            payload['events'][0]['evidence_ref']='EVID-edited';state.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):m.private_overlay(ROOT,state,out,NOW)
        self.assertEqual((ROOT/m.REGISTER).read_bytes(),before)

if __name__=='__main__':unittest.main()
