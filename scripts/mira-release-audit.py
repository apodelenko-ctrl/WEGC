#!/usr/bin/env python3
"""Bounded read-only release audit on the owner's site; never a registration.

Verifies published code/data bytes, every project URL and all document downloads.
Optional stress is restricted to loopback; public calls never exceed concurrency4.
"""
from pathlib import Path
from urllib.parse import urlsplit,urljoin
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import argparse,hashlib,json,os,statistics,time,datetime
ROOT=Path(__file__).resolve().parents[1]
OWNERS={'wegc.fund','localhost','127.0.0.1'}
PAGES=['mira/go/index.html','mira/practical/index.html','mira/corporate/index.html',
       'mira/launch/index.html','mira/exhibition/index.html','mira/catalog/index.html','mira/catalog/list.html']
FILES=PAGES+['mira/campaign/accessibility.css','mira/campaign/campaign.css','mira/campaign/campaign.mjs','mira/agency/qualification.mjs',
       'mira/catalog/catalog.css','mira/catalog/catalog.mjs','mira/catalog/catalog-core.mjs',
       'mira/catalog/data.json','mira/catalog/build-report.json','mira/exhibition/banner-landscape.svg',
       'mira/exhibition/banner-rollup.svg','mira/exhibition/qr.svg']
DOCS=['agency-agreement','project-rules','data-processing','privacy','data-consent',
      'marketing-consent','materials-policy','payment-support','site-terms']
FILES += ['mira/documents/'+name+'.html' for name in DOCS]
class Links(HTMLParser):
    def __init__(self,s):super().__init__();self.links=[];self.ids=set();self.feed(s)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id'in a:self.ids.add(a['id'])
        if tag=='a' and a.get('href'):self.links.append(a['href'])
def request(base,path,method='GET'):
    url=urljoin(base+'/',path)
    if urlsplit(url).netloc!=urlsplit(base).netloc:raise ValueError('External audit target rejected')
    start=time.monotonic()
    with urlopen(Request(url,method=method,headers={'User-Agent':'MIRA-owner-release-audit/1.0'}),timeout=25)as r:
        b=r.read(5_000_001);status=r.status
        if len(b)>5_000_000:raise ValueError('Audit response exceeds bound')
        if urlsplit(r.url).netloc!=urlsplit(base).netloc:raise ValueError('Cross-origin redirect rejected')
    return b,status,round((time.monotonic()-start)*1000,2)
def run(base,out,local_stress=False):
    host=urlsplit(base).hostname
    if host not in OWNERS:raise ValueError('Only owner domain or loopback allowed')
    if local_stress and host not in {'localhost','127.0.0.1'}:raise ValueError('Stress requires loopback')
    report={'base':base,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'source_commit':os.environ.get('GITHUB_SHA','local-uncommitted'),'passed':False,
       'files':[],'links':[],'documents':[],'qr':[],'actual_registration_tested':False,
       'scope':'bounded own-site GET/HEAD audit; optional loopback stress; not maximum capacity'}
    try:
        for path in FILES:
            expected=hashlib.sha256((ROOT/path).read_bytes()).hexdigest();last=None
            for attempt in range(8):
                try:
                    b,status,ms=request(base,path)
                    if hashlib.sha256(b).hexdigest()!=expected:raise AssertionError('Published source mismatch: '+path)
                    last=None;break
                except Exception as exc:last=exc;time.sleep(3)
            if last:raise last
            report['files'].append({'path':path,'status':status,'bytes':len(b),'sha256':expected,'ms':ms})
        # Check every generated project URL and every own link from the new surfaces.
        records=json.loads((ROOT/'mira/catalog/data.json').read_text())['projects']
        paths={f'/mira/catalog/projects/{p["id"]}/'for p in records}
        for path in PAGES:
            doc=Links((ROOT/path).read_text())
            for href in doc.links:
                u=urlsplit(urljoin(base+'/'+path,href))
                if u.netloc!=urlsplit(base).netloc:continue
                paths.add(u.path)
                if u.fragment:
                    target=ROOT/u.path.lstrip('/')
                    if target.is_dir():target=target/'index.html'
                    if target.is_file() and u.fragment not in Links(target.read_text()).ids:raise AssertionError('Broken fragment '+href+' in '+path)
        def head(path):
            # Smooth the crawl: four workers, HEAD only, no external target.
            time.sleep(.05);_,status,ms=request(base,path,'HEAD');return {'path':path,'status':status,'ms':ms}
        with ThreadPoolExecutor(max_workers=4)as pool:report['links']=list(pool.map(head,sorted(paths)))
        assert all(v['status']==200 for v in report['links'])
        report['project_pages_checked']=len(records)
        for name in DOCS:
            path='mira/documents/downloads/'+name+'.pdf';b,status,ms=request(base,path)
            assert b.startswith(b'%PDF'),path
            import fitz
            doc=fitz.open(stream=b,filetype='pdf');text=' '.join(p.get_text() for p in doc)
            assert len(text)>100 and len(doc)>=1,path
            report['documents'].append({'path':path,'status':status,'pages':len(doc),'bytes':len(b)})
        b,status,_=request(base,'mira/documents/downloads/agency-agreement.docx');assert b.startswith(b'PK')
        report['documents'].append({'path':'mira/documents/downloads/agency-agreement.docx','status':status,'bytes':len(b)})
        import cv2,numpy as np
        for name in ['qr.png','banner-landscape.png','banner-rollup.png']:
            b,status,_=request(base,'mira/exhibition/'+name)
            image=cv2.imdecode(np.frombuffer(b,np.uint8),cv2.IMREAD_COLOR)
            decoded,points,_=cv2.QRCodeDetector().detectAndDecode(image)
            assert decoded=='https://wegc.fund/mira/go/',(name,decoded)
            report['qr'].append({'path':name,'decoded':decoded,'status':status})
        if local_stress:
            targets=['mira/catalog/data.json','mira/go/','mira/practical/','mira/corporate/']*50
            with ThreadPoolExecutor(max_workers=8)as pool:values=list(pool.map(lambda path:request(base,path),targets))
            timings=sorted(v[2]for v in values)
            report['local_bounded_load']={'requests':len(values),'concurrency':8,'successful':sum(v[1]==200 for v in values),
              'p50_ms':round(statistics.median(timings),2),'p95_ms':timings[int(.95*(len(timings)-1))],
              'scope':'loopback static server; not production capacity or D1 stress'}
        report['passed']=True
    except Exception as exc:
        report['failure']=str(exc);raise
    finally:
        out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'base':base,'passed':report['passed'],'files':len(report['files']),'links':len(report['links']),'real_registration':False}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--local-stress',action='store_true');a=p.parse_args();run(a.base.rstrip('/'),a.out,a.local_stress)
