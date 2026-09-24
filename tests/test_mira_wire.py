"""Landing integration must be idempotent and preserve the accepted content."""
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('wire',Path(__file__).resolve().parents[1]/'scripts/mira-wire-landing.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
FIXTURE='''<!doctype html><html><header>ACCEPTED HERO</header><section><a class="btn" href="#join">Запросить демонстрацию</a></section><section>Оставьте рабочий контакт. Для пилотной волны подключения обрабатываются вручную.<form onsubmit="sendLead(event)"><button>Submit</button></form></section><footer>ACCEPTED FOOTER</footer><script>
function val(id){return id}
function sendLead(e){ location.href='mailto:post@wegc.fund'; }
</script></html>'''
class WireTests(unittest.TestCase):
    def test_preserves_accepted_sections_and_links_actual_demo(self):
        out=m.transform(FIXTURE)
        self.assertIn('ACCEPTED HERO',out);self.assertIn('ACCEPTED FOOTER',out)
        self.assertIn('./marketplace.html',out);self.assertIn('./pilot.html',out)
        self.assertIn('https://pilot.wegc.fund/mira/request/',out)
        self.assertNotIn('принимается только через защищённый доступ',out)
        self.assertNotIn('mailto:',out);self.assertNotIn('sendLead',out)
    def test_idempotent(self):
        out=m.transform(FIXTURE);self.assertEqual(m.transform(out),out)
    def test_unexpected_structure_fails(self):
        with self.assertRaises(ValueError):m.transform(FIXTURE.replace('Запросить демонстрацию','changed'))
    def test_unexpected_script_fails(self):
        with self.assertRaises(ValueError):m.transform(FIXTURE.replace('function sendLead','function changed'))
if __name__=='__main__':unittest.main()
