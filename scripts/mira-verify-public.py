#!/usr/bin/env python3
"""Verify exact built bytes and bounded GET concurrency on the owner's site."""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor
import argparse,hashlib,json,time,statistics
ROOT=Path(__file__).resolve().parents[1]
PATHS=['mira/start/index.html','mira/growth/index.html','mira/business/index.html','mira/variants/index.html','mira/phuket/index.html','mira/data/phuket.json','mira/launch/launch.mjs','mira/launch/launch.css','mira/phuket/catalogue.mjs','mira/documents/index.html','mira/documents/agency-agreement.html','mira/expo/banner.svg','mira/expo/qr.svg']
def main(base,out,load):
 assert urlsplit(base).hostname in {'wegc.fund','glistening-baklava-2ca58f.netlify.app','bespoke-elf-196a9d1.netlify.app','127.0.0.1','localhost'}
 checks=[]
 def fetch(path):
  start=time.monotonic()
  with urlopen(Request(base+'/'+path,headers={'User-Agent':'MIRA-owned-site-release-check/1.0'}),timeout=25)as r:body=r.read();status=r.status
  return body,status,1000*(time.monotonic()-start)
 for path in PATHS:
  expected=hashlib.sha256((ROOT/path).read_bytes()).hexdigest();error=None
  for attempt in range(8):
   try:
    body,status,elapsed=fetch(path)
    if hashlib.sha256(body).hexdigest()!=expected:raise AssertionError('published bytes differ: '+path)
    checks.append({'path':path,'status':status,'sha256':expected,'ms':round(elapsed,2)});error=None;break
   except Exception as e:error=str(e);time.sleep(3)
  if error:raise RuntimeError(error)
 for path in ['mira/documents/downloads/agency-agreement.pdf','mira/documents/downloads/agency-agreement.docx','mira/expo/banner.pdf']:
  b,status,ms=fetch(path);assert b.startswith(b'PK'if path.endswith('.docx')else b'%PDF');checks.append({'path':path,'status':status,'bytes':len(b)})
 metrics=None
 if load:
  targets=['mira/start/','mira/data/phuket.json','mira/business/','mira/documents/']*20
  # 80 requests, concurrency4: a bounded smoke load, NOT a capacity or DDoS test.
  with ThreadPoolExecutor(max_workers=4)as pool:values=list(pool.map(fetch,targets))
  timings=sorted(v[2]for v in values);metrics={'requests':len(values),'concurrency':4,'successful':sum(v[1]==200 for v in values),'p50_ms':round(statistics.median(timings),2),'p95_ms':round(timings[int(.95*(len(timings)-1))],2),'scope':'bounded GET smoke only; not maximum capacity'}
 report={'base':base,'checks':checks,'bounded_load':metrics,'actual_registration_tested':False}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'base':base,'files_verified':len(checks),'load':metrics}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',default='https://wegc.fund');p.add_argument('--out',type=Path,default=Path('/tmp/mira-public.json'));p.add_argument('--load',action='store_true');a=p.parse_args();main(a.base.rstrip('/'),a.out,a.load)
