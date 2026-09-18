"""Bounded worker invocation. No scheduler is installed. Run under LOCAL's existing supervisor."""
import json, os, argparse, time
from concurrent.futures import ThreadPoolExecutor
from core import Store, Engine, Dispatcher
from adapters import AnthropicIntelligence, Sender

def run(store, engine, dispatcher, limit=100, workers=4):
    ids=[r['id'] for r in sorted(store.rows('inbox'),key=lambda r:r['created']) if r['state']=='pending'][:limit]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results=list(pool.map(engine.process,ids))
    # Sequential, conservatively paced outbound. Not a claim of 100-chat throughput.
    delivered=[]
    for row in sorted(store.rows('outbox'),key=lambda r:r['created']):
        if row['state']=='pending':
            delivered.append(dispatcher.dispatch(row['id']))
            if dispatcher.enabled: time.sleep(1.05)
    return {'processing':results,'delivery':delivered}

if __name__=='__main__':
    os.umask(0o077)
    parser=argparse.ArgumentParser(); parser.add_argument('--limit',type=int,default=100)
    args=parser.parse_args(); env=os.environ
    store=Store(env['MIRA_DB'],profile=env['MIRA_PROFILE'])
    with open(env['MIRA_KB'],encoding='utf-8') as f: kb=json.load(f)
    flow=None
    if env.get('MIRA_CATALOG_CONFIG'):
        from deal_flow import DealFlow,normalize_catalog
        with open(env['MIRA_CATALOG_CONFIG'],encoding='utf-8') as f: sources=json.load(f)
        catalog=[]
        for source in sources:
            with open(source['path'],encoding='utf-8') as f:
                catalog.extend(normalize_catalog(json.load(f),market=source['market'],source=source['source']))
        flow=DealFlow(store,catalog)
    engine=Engine(store,AnthropicIntelligence(),kb,deal_flow=flow)
    dispatcher=Dispatcher(store,Sender(),enabled=env.get('MIRA_SEND_ENABLED')=='true')
    print(json.dumps(run(store,engine,dispatcher,args.limit),ensure_ascii=False))
