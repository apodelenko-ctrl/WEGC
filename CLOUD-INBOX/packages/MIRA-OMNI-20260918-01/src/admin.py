"""Private local administration. Never expose this CLI as an unauthenticated API."""
import argparse, json, os
from core import Store

if __name__=='__main__':
    os.umask(0o077)
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True)
    sub=p.add_subparsers(dest='command',required=True)
    b=sub.add_parser('bind'); b.add_argument('private_bindings_json')
    r=sub.add_parser('resolve'); r.add_argument('event_id')
    a=sub.add_parser('resume'); a.add_argument('contact'); a.add_argument('--operator',required=True); a.add_argument('--reason',required=True)
    q=sub.add_parser('counts')
    args=p.parse_args(); store=Store(args.db)
    if args.command=='bind':
        with open(args.private_bindings_json,encoding='utf-8') as f: rows=json.load(f)
        for r in rows: store.bind(r['contact'],r['context'],r['channel'],r['account'],str(r['peer']),r['evidence'])
        print(json.dumps({'bound':len(rows)}))
    elif args.command=='resolve': store.resolve(args.event_id); print('resolved')
    elif args.command=='resume': store.resume(args.contact,args.operator,args.reason); print('resumed; suppression retained')
    else:
        from collections import Counter
        print(json.dumps({t:dict(Counter(r.get('state','stored') for r in store.rows(t))) for t in ['inbox','outbox']},indent=2))
