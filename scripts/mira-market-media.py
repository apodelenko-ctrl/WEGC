#!/usr/bin/env python3
"""Bounded, explicit public-media acquisition and reviewed local publishing.
No network by default. No authentication, proxy tricks or forced rights approval.
Downloaded candidates are NOT automatically used by the public catalogue.
"""
from pathlib import Path
from urllib.parse import urlsplit,urljoin
from urllib.request import Request,urlopen,build_opener,HTTPRedirectHandler
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
import argparse,hashlib,html,io,ipaddress,json,re,socket,time
ROOT=Path(__file__).resolve().parents[1]
SOURCE='project-bible/mira/data/markets/dubai-bali-30.json'
class Images(HTMLParser):
 def __init__(self,base):super().__init__();self.base=base;self.candidates=[]
 def handle_starttag(self,tag,attrs):
  a={k:v or '' for k,v in attrs};values=[]
  if tag=='meta' and (a.get('property') or a.get('name')) in ['og:image','og:image:url','twitter:image']:values.append((a.get('content',''),100,'social'))
  if tag in ['img','source']:
   for k in ['data-original','data-src','src','data-lazy-src']:values.append((a.get(k,''),40,'image'))
   for k in ['srcset','data-srcset']:
    for part in a.get(k,'').split(','):values.append((part.strip().split(' ')[0],50,'srcset'))
  if tag=='a' and re.search(r'\.(?:webp|jpe?g|png)(?:\?|$)',a.get('href',''),re.I):values.append((a['href'],20,'gallery'))
  for value,score,kind in values:
   if not value or value.startswith(('data:','blob:','#')):continue
   url=urljoin(self.base,html.unescape(value))
   if re.search(r'\.svg(?:[?#]|$)',url,re.I) or any(x in url.lower() for x in ['facebook.com/tr','mc.yandex.','counter?','/rt.gif','favicon','logo','sprite','pixel','placeholder','/resize/20x','/resize/20/','/20x/']):continue
   self.candidates.append({'url':url,'score':score,'method':kind,'alt':a.get('alt','')})
def safe_url(url,resolve=False):
 u=urlsplit(url)
 if u.scheme!='https' or not u.hostname or u.username or u.password or (u.port not in [None,443]) or u.hostname.lower().endswith(('.local','.internal','.localhost')):raise ValueError('Unsafe media URL')
 try:
  ip=ipaddress.ip_address(u.hostname)
  if not ip.is_global:raise ValueError('Private address blocked')
 except ValueError as e:
  if str(e)=='Private address blocked':raise
  if u.hostname.lower()=='localhost':raise ValueError('Local address blocked')
 if resolve:
  addresses=socket.getaddrinfo(u.hostname,443,type=socket.SOCK_STREAM)
  if not addresses or any(not ipaddress.ip_address(x[4][0]).is_global for x in addresses):raise ValueError('Non-public DNS address')
 return url
class Redirects(HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  safe_url(newurl,True);n=getattr(req,'redirect_count',0)+1
  if n>4:raise ValueError('Too many redirects')
  result=super().redirect_request(req,fp,code,msg,headers,newurl)
  if result:result.redirect_count=n
  return result
def fetch(url,limit):
 safe_url(url,True)
 request=Request(url,headers={'User-Agent':'MIRA-Public-Research/1.0','Accept':'text/html,image/*;q=0.9,*/*;q=0.5'})
 with build_opener(Redirects).open(request,timeout=12) as r:
  body=r.read(limit+1)
  if len(body)>limit:raise ValueError('Response exceeds size limit')
  return body,r.headers.get_content_type(),r.geturl()
def inventory(root,out):
 source=json.loads((root/SOURCE).read_text());out.mkdir(parents=True,exist_ok=True)
 records=[{'id':p['id'],'project':p['name'],'sourcePage':p['media']['sourcePage'],'candidateURL':p['media']['candidateUrl'],'rightsStatus':p['media']['rightsStatus'],'approvedForPublication':False} for p in source['projects']]
 report={'projects':len(records),'directImageURLs':sum(bool(x['candidateURL']) for x in records),'networkPerformed':False,'items':records}
 (out/'inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));return source

def acquire(root,out,do_fetch=False):
 source=inventory(root,out)
 if not do_fetch:return {'networkPerformed':False,'projects':len(source['projects'])}
 from PIL import Image,ImageOps
 Image.MAX_IMAGE_PIXELS=50000000
 def one(p):
  result={'id':p['id'],'name':p['name'],'market':p['market'],'sourcePage':p['media']['sourcePage'],'targetPath':p['media']['localPath'],'rightsStatus':p['media']['rightsStatus'],'approvedForPublication':False,'visualReviewed':False,'rightsReference':'','errors':[],'candidates':[]}
  candidates=[]
  if p['media']['candidateUrl']:candidates.append({'url':p['media']['candidateUrl'],'score':1000,'method':'explicit_primary_project_gallery'})
  # Only read project page when the original pass did not identify the image URL.
  if not candidates:
   try:
    body,mime,url=fetch(result['sourcePage'],2000000);parser=Images(url);parser.feed(body.decode('utf-8',errors='replace'))
    terms=[x for x in re.findall('[a-z]{4,}',p['slug']) if x not in ['residences','apartments','canggu','bali','dubai']]
    for c in parser.candidates:c['score']+=sum(15 for t in terms if t in (c['url']+' '+c.get('alt','')).lower())
    candidates=sorted(parser.candidates,key=lambda c:-c['score'])
   except Exception as e:result['errors'].append('source-page: '+str(e)[:250])
  seen=set();candidates=[c for c in candidates if not(c['url'] in seen or seen.add(c['url']))][:8];result['candidates']=candidates
  for candidate in candidates[:3]:
   try:
    body,mime,actual=fetch(candidate['url'],12000000)
    if not mime.startswith('image/'):raise ValueError('Non-image response '+mime)
    with Image.open(io.BytesIO(body)) as img:
     if max(img.size)<600 or min(img.size)<240:raise ValueError('Thumbnail too small for project cover')
     if img.width*img.height>50000000:raise ValueError('Image too large')
     img=ImageOps.exif_transpose(img).convert('RGB');img.thumbnail((1400,1100));f=out/(p['id']+'.webp');img.save(f,'WEBP',quality=84,method=6)
     result.update({'acquisitionStatus':'downloaded_candidate_not_publication_approved','localFile':f.name,'width':img.width,'height':img.height,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'originalSHA256':hashlib.sha256(body).hexdigest(),'sourceImageURL':actual,'selectionMethod':candidate['method']})
    break
   except Exception as e:result['errors'].append('image: '+str(e)[:250])
  result.setdefault('acquisitionStatus','unavailable_in_this_runtime');return result
 with ThreadPoolExecutor(max_workers=3) as ex:results=list(ex.map(one,source['projects']))
 report={'scope':'Reference media acquired for review; no external publication or licensing clearance','networkPerformed':True,'projects':30,'downloadedCandidates':sum('localFile' in r for r in results),'approvedProjectImages':0,'items':results}
 (out/'media-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 cards=[]
 for r in results:
  im='<img src="'+html.escape(r['localFile'],quote=True)+'" alt="'+html.escape(r['name'],quote=True)+'">' if 'localFile' in r else '<div class="missing">Файл не получен</div>'
  cards.append('<article>'+im+'<h2>'+html.escape(r['name'])+'</h2><p>'+html.escape(r['acquisitionStatus'])+'</p><a href="'+html.escape(r['sourcePage'],quote=True)+'">Страница источника</a><p>Проверка изображения и разрешения на публикацию: не завершена.</p></article>')
 (out/'review.html').write_text('<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>МИРА — проверка изображений</title><style>body{font:16px system-ui;margin:30px;background:#f5f6f7;color:#162830}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}article{padding:15px;background:white;border:1px solid #ddd}img,.missing{width:100%;height:220px;object-fit:contain}h2{font-size:20px}.missing{display:grid;place-items:center;background:#eee}p{font-size:13px}</style><h1>Материалы 30 проектов: лист проверки</h1><p>Не выдавать случайный OG-кадр за изображение проекта. Утверждение должно соответствовать конкретной карточке и правилам источника.</p><main>'+''.join(cards)+'</main></html>')
 return {k:v for k,v in report.items() if k!='items'}
def publish(root,review):
 report=json.loads(review.read_text());items=report.get('items',[]);approved={};pending=[]
 # Validate all candidates before any write. No automatic rights or visual approval.
 for r in items:
  if r.get('approvedForPublication') is not True:continue
  assert r.get('visualReviewed') is True and str(r.get('rightsReference','')).strip(),'Review and rights reference are mandatory'
  source=(review.parent/r['localFile']).resolve();assert source.is_relative_to(review.parent.resolve()) and source.is_file()
  assert hashlib.sha256(source.read_bytes()).hexdigest()==r['sha256']
  target=r['targetPath'];assert re.fullmatch(r'/images/mira-markets/(bali|dubai)/[a-z0-9-]+\.webp',target)
  dest=root/target.lstrip('/');assert not dest.exists() or hashlib.sha256(dest.read_bytes()).hexdigest()==r['sha256'],'Existing different asset'
  approved[r['id']]={'path':target,'sha256':r['sha256'],'sourceURL':r['sourceImageURL'],'approvedForPublication':True,'visualReviewed':True,'rightsReference':r['rightsReference']};pending.append((source,dest))
 for a,b in pending:b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(a.read_bytes())
 dest=root/'mira/catalog/markets/media-approved.json';dest.parent.mkdir(parents=True,exist_ok=True)
 existing=json.loads(dest.read_text()) if dest.exists() else {};existing.update(approved);dest.write_text(json.dumps(existing,ensure_ascii=False,indent=2)+'\n')
 return {'copied':len(pending),'cloudDeployed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['inventory','acquire','publish']);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,default=Path('/private/tmp/mira-market-media'));p.add_argument('--fetch',action='store_true');p.add_argument('--review',type=Path);a=p.parse_args()
 result=publish(a.root,a.review) if a.command=='publish' and a.review else (acquire(a.root,a.out,a.fetch) if a.command=='acquire' else inventory(a.root,a.out))
 if a.command=='inventory':result={'projects':len(result['projects']),'networkPerformed':False}
 print(json.dumps(result,ensure_ascii=False))
