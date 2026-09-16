"""Source-quality regressions. All TEST records are synthetic non-business fixtures."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('launch_quality',Path(__file__).resolve().parents[1]/'scripts/mira-launch-build.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class SourceQualityTests(unittest.TestCase):
    def fixture(self):
        c=[dict(rank='1',company='TEST',city='A',website='https://example.test',why_relevant='new-build')]
        r=[dict(company='TEST AGENCY',city='A',primary_segment='newbuild_regional',readiness='ready_for_owner_review',secondary_signal='named_owner')]
        a=[dict(cohort_company='TEST',cohort_city='A',review_company='TEST AGENCY',review_city='A',official_domain='example.test',scope='same_city_brand_alias',source_url='https://example.test/about',checked_at='2026-09-16',reviewer='TEST',reason='Synthetic exact identity link')]
        return c,r,a
    def test_explicit_alias_joins_review_and_wave_without_new_approval(self):
        c,r,a=self.fixture(); w=[dict(company='TEST AGENCY',city='A',send_status='not_approved',next_action='TEST follow-up')]
        out,exceptions=m.segment_agencies(c,r,w,a)
        self.assertEqual(exceptions,[]);self.assertEqual(out[0]['review_join'],'reviewed_alias')
        self.assertEqual(out[0]['owner_review_wave'],'true');self.assertEqual(out[0]['send_status'],'not_approved')
        self.assertEqual(out[0]['alias_source_url'],a[0]['source_url'])
        self.assertEqual(out[0]['greenfield_confirmed'],'false')
    def test_alias_not_inferred_when_table_is_absent(self):
        c,r,a=self.fixture(); out,exc=m.segment_agencies(c,r,[])
        self.assertEqual(len(exc),1);self.assertEqual(out[0]['live_reviewed'],'false')
    def test_cross_domain_alias_fails(self):
        c,r,a=self.fixture();a[0]['source_url']='https://unrelated.test/'
        with self.assertRaises(ValueError):m.segment_agencies(c,r,[],a)
    def test_cross_city_brand_alias_fails(self):
        c,r,a=self.fixture();r[0]['city']=a[0]['review_city']='B'
        with self.assertRaises(ValueError):m.segment_agencies(c,r,[],a)
    def test_hq_scope_requires_same_company(self):
        c,r,a=self.fixture();a[0]['scope']='hq_city_scope'
        with self.assertRaises(ValueError):m.segment_agencies(c,r,[],a)
    def test_hq_scope_retains_single_network_record(self):
        c,r,a=self.fixture();r[0]['company']=a[0]['review_company']='TEST';r[0]['city']=a[0]['review_city']='A / HQ';a[0]['scope']='hq_city_scope'
        out,exc=m.segment_agencies(c,r,[],a);self.assertEqual(len(out),1);self.assertEqual(exc,[])
    def test_duplicate_alias_fails(self):
        c,r,a=self.fixture()
        with self.assertRaises(ValueError):m.segment_agencies(c,r,[],a+a)
    def test_missing_alias_provenance_fails(self):
        c,r,a=self.fixture();a[0]['reason']=''
        with self.assertRaises(ValueError):m.segment_agencies(c,r,[],a)
    def test_csv_extra_cell_is_not_silently_discarded(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.csv';p.write_text('a,b\n1,2,3\n')
            with self.assertRaisesRegex(ValueError,'width mismatch'):m.rows(Path(d),'test.csv')
    def test_csv_missing_cell_is_not_silently_defaulted(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.csv';p.write_text('a,b\n1\n')
            with self.assertRaisesRegex(ValueError,'width mismatch'):m.rows(Path(d),'test.csv')
    def test_csv_duplicate_header_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.csv';p.write_text('a,a\n1,2\n')
            with self.assertRaisesRegex(ValueError,'header'):m.rows(Path(d),'test.csv')
    def test_quoted_comma_remains_one_field(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.csv';p.write_text('a,b\n"Company Co., Ltd.",2\n')
            self.assertEqual(m.rows(Path(d),'test.csv')[0]['a'],'Company Co., Ltd.')
    def test_p0_shifted_source_date_fails(self):
        row=dict(developer_group='TEST',checked_at='2026-09-16',source_url='not a URL',partner_route='manual routing',next_action='TEST')
        with self.assertRaises(ValueError):m.validate_p0([row])
        row['source_url']='https://example.test/';row['checked_at']='https://example.test/'
        with self.assertRaises(ValueError):m.validate_p0([row])

if __name__=='__main__':unittest.main()
