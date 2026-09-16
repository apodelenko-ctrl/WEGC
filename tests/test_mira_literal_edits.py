"""Synthetic literal-edit integrity tests; production/source files are untouched."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

s=importlib.util.spec_from_file_location('literal',Path(__file__).resolve().parents[1]/'scripts/mira-apply-reviewed-checkpoint.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class LiteralEdits(unittest.TestCase):
    def payload(self,old,new,edits):
        return {'kind':'reviewed-public-source','version':1,'files':[{'path':'mira/synthetic.txt','before_sha256':m.digest(old.encode()),'sha256':m.digest(new.encode()),'codec':'utf8-edits-v1','edits':edits}]}
    def run_case(self,old,new,edits):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'mira/synthetic.txt';p.parent.mkdir();p.write_text(old)
            result=m.prepare(root,self.payload(old,new,edits))
            self.assertEqual(p.read_text(),old)
            self.assertEqual(result[0][1].decode(),new)
            p.write_bytes(result[0][1]);self.assertFalse(m.prepare(root,self.payload(old,new,edits))[0][2])
    def test_unicode_exact_edits_are_hash_verified_and_idempotent(self):
        self.run_case('SYNTHETIC: старое\n','SYNTHETIC: новое\n',[{'old':'старое','new':'новое'}])
    def test_missing_or_multiple_match_rejected_without_writes(self):
        for match in ['missing','x','']:
            with self.assertRaises(ValueError):self.run_case('x x','z',[{'old':match,'new':'z'}])
    def test_output_hash_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,'hash mismatch'):self.run_case('old','expected',[{'old':'old','new':'different'}])
    def test_unknown_edit_fields_rejected(self):
        with self.assertRaises(ValueError):self.run_case('old','new',[{'old':'old','new':'new','run':'not executable'}])

if __name__=='__main__':unittest.main()
