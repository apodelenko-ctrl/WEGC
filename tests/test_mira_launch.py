import importlib.util
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('launch',Path(__file__).resolve().parents[1]/'scripts/mira-launch-build.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class LaunchTests(unittest.TestCase):
    def test_read_catalog_and_reject_non_catalog(self):
        raw='window.WEGC_CATALOG = [\n'+ '{"slug":"test","name":"TEST"},\n];'
        self.assertEqual(len(m.read_catalog(raw)),1)
        with self.assertRaises(ValueError):m.read_catalog('window.OTHER = [];')
    def test_duplicate_source_slugs_fail(self):
        item='{"slug":"test","name":"TEST"},\n'
        with self.assertRaises(ValueError):m.read_catalog('window.WEGC_CATALOG = [\n'+item*2+'];')
    def test_generator_does_not_create_legal_seller(self):
        p=[{'slug':'test','name':'TEST','developer':'Foo','district':'x','kind':'villa'}]
        a=[{'alias':'Foo','canonical_group':'Foo group','legal_entity_status':'partially_resolved'}]
        r=m.normalize_phuket(p,[],a,[])[0]
        self.assertEqual(r['developer_family'],'Foo group');self.assertEqual(r['mapping_confidence'],'low');self.assertEqual(r['legal_contracting_seller'],'unknown');self.assertEqual(r['registration_enabled'],'false')
    def test_operator_is_not_a_developer(self):
        p=[{'slug':'test','name':'TEST','developer':'Brand'}]
        a=[{'alias':'Brand','canonical_group':'Hotel brand','legal_entity_status':'operator_or_brand_only'}]
        r=m.normalize_phuket(p,[],a,[])[0]
        self.assertEqual(r['developer_family'],'unknown');self.assertEqual(r['operator_or_brand_signal'],'Hotel brand')
    def test_missing_seed_fails_instead_of_silent_drop(self):
        s=[{'project_name':'missing','developer_family':'Foo','developer_mapping_confidence':'high'}]
        with self.assertRaises(ValueError):m.normalize_phuket([],s,[],[])
    def test_alias_conflicts_fail(self):
        a=[{'alias':'Foo','canonical_group':'A'},{'alias':'foo','canonical_group':'B'}]
        with self.assertRaises(ValueError):m.normalize_phuket([],[],a,[])
    def test_same_company_other_city_does_not_join(self):
        c=[{'rank':'1','company':'TEST','city':'A','website':'https://example.test','why_relevant':'new-build'}]
        r=[{'company':'TEST','city':'B','primary_segment':'existing_phuket_direction','readiness':'ready_for_owner_review'}]
        output,exc=m.segment_agencies(c,r,[])
        self.assertEqual(output[0]['live_reviewed'],'false');self.assertEqual(output[0]['overseas_status'],'unknown');self.assertEqual(len(exc),1)
    def test_greenfield_never_inferred_from_missing_foreign_evidence(self):
        c=[{'rank':'1','company':'TEST','city':'A','website':'https://example.test','why_relevant':'regional agency'}]
        r=[{'company':'TEST','city':'A','primary_segment':'newbuild_regional','readiness':'ready_for_owner_review','secondary_signal':'named_owner'}]
        output,_=m.segment_agencies(c,r,[])
        self.assertEqual(output[0]['greenfield_confirmed'],'false');self.assertEqual(output[0]['overseas_status'],'unknown');self.assertEqual(output[0]['send_status'],'not_approved')
    def test_generated_section_is_idempotent_and_preserves_manual_text(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'status';p.write_text('manual historical baseline\n');m.replace_generated_section(p,'NEW');m.replace_generated_section(p,'NEW')
            self.assertEqual(p.read_text().count('NEW'),1);self.assertTrue(p.read_text().startswith('manual historical baseline'))
if __name__=='__main__':unittest.main()
