#!/usr/bin/env python3
"""Sanitize the existing seed for the PUBLIC demo. No commercial facts inferred."""
from pathlib import Path
import argparse, csv, hashlib, json, re
ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'project-bible/mira/data/phuket-project-master-seed-45.csv'
def build(root=ROOT):
    raw=(root/SOURCE).read_bytes()
    rows=list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
    projects=[]
    for row in rows:
        name=row['project_name'].strip()
        ident=re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-') or hashlib.sha256(name.encode()).hexdigest()[:16]
        projects.append(dict(id=ident,name=name,district=row['district'],kind=row['kind'],developerFamily=row['developer_family']))
    if len({p['id'] for p in projects}) != len(projects):
        raise ValueError('Duplicate public project id: resolve before publishing')
    provenance=dict(sourceType='Внутренний исследовательский каталог WEGC; не коммерческая проверка',sourcePath=SOURCE,sourceSha256=hashlib.sha256(raw).hexdigest(),verifiedAt=None,status='discovery_only')
    output=dict(schemaVersion=1,mode='demo',provenance=provenance,projects=projects)
    dest=root/'mira/data/catalog.json';dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'public_demo_projects':len(projects),'commercially_enabled':0}))
    return output
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);args=parser.parse_args();build(args.root)
