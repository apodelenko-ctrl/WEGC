"""Extract observed contacts from supplied public HTML. No inferred messenger membership."""
import argparse, datetime, json, re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, unquote

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.json_ld=[]; self.in_json=False
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='a' and a.get('href'): self.links.append(a['href'])
        if tag=='script' and a.get('type')=='application/ld+json': self.in_json=True
    def handle_endtag(self, tag):
        if tag=='script': self.in_json=False
    def handle_data(self, data):
        if self.in_json: self.json_ld.append(data)

def phone(value):
    raw=unquote(value).strip(); digits=re.sub(r'[^0-9]','',raw)
    # Do not guess country code or strip extensions. Local-format numbers stay unnormalized.
    if re.search(r'(ext|доб|;|#)',raw,re.I): return None
    return '+'+digits if raw.startswith('+') and 7<=len(digits)<=15 else None

def extract(html, source, checked_at=None):
    p=Links(); p.feed(html); rows={}
    stamp=checked_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
    def add(channel, value, observed, normalized=None):
        if not value: return
        row={'channel':channel,'value':value,'normalized_phone':normalized,'observed':observed,
             'source':source,'checked_at':stamp,'status':'public_link_observed','membership_verified':False}
        rows[(channel,value)]=row
    for link in p.links:
        u=urlparse(urljoin(source,link)); host=(u.hostname or '').lower(); value=unquote(u.path)
        if u.scheme=='tel': add('phone',value,link,phone(value))
        elif u.scheme=='mailto': add('email',value,link)
        elif host in {'wa.me','api.whatsapp.com','www.whatsapp.com'}:
            digits=value.strip('/') if host=='wa.me' else ''
            add('whatsapp',u.geturl(),link,phone('+'+digits) if digits.isdigit() else None)
        elif host in {'t.me','telegram.me'}: add('telegram',u.geturl(),link)
        elif host in {'max.ru','www.max.ru'}: add('max',u.geturl(),link)
        elif host in {'vk.com','www.vk.com'}: add('vk',u.geturl(),link)
    def walk(obj):
        if isinstance(obj,list):
            for item in obj: walk(item)
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k in {'telephone','email'} and isinstance(v,str): add('phone' if k=='telephone' else 'email',v,'json-ld',phone(v) if k=='telephone' else None)
                elif isinstance(v,(dict,list)): walk(v)
    for text in p.json_ld:
        try: walk(json.loads(text))
        except ValueError: pass
    return list(rows.values())

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('html_file'); ap.add_argument('--source',required=True)
    a=ap.parse_args()
    with open(a.html_file,encoding='utf-8') as f: print(json.dumps(extract(f.read(),a.source),ensure_ascii=False,indent=2))
