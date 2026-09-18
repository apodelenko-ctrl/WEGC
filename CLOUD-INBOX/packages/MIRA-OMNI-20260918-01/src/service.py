"""Loopback-only staging HTTP ingress; put an authenticated TLS proxy in front for deployment."""
import json, os, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from adapters import normalize, checked_secret
from core import Store, packed

def handler(store, env):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_): pass # no credentials or PII in access logs
        def reply(self, status, value):
            data=packed(value).encode(); self.send_response(status)
            self.send_header('Content-Type','application/json'); self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
        def do_GET(self):
            path=urlparse(self.path)
            if path.path=='/health': return self.reply(200,{'service':'mira-communication','status':'staging'})
            if path.path=='/whatsapp':
                q=parse_qs(path.query)
                if q.get('hub.mode')==['subscribe'] and checked_secret(q.get('hub.verify_token',[''])[0],env.get('WA_VERIFY_TOKEN')):
                    data=q.get('hub.challenge',[''])[0].encode(); self.send_response(200); self.end_headers(); self.wfile.write(data); return
                return self.reply(403,{'error':'forbidden'})
            return self.reply(404,{'error':'not_found'})
        def do_POST(self):
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=262144: return self.reply(413,{'error':'body_size'})
                self.connection.settimeout(10)
                body=self.rfile.read(size)
                path=urlparse(self.path).path
                if path=='/bridge':
                    # Only the existing authenticated Worker/mail service can call this route.
                    if not checked_secret(self.headers.get('Authorization'), 'Bearer '+env['MIRA_INTERNAL_TOKEN']):
                        return self.reply(403,{'error':'forbidden'})
                    e=json.loads(body)
                    if e.get('channel') not in {'web','email'}: raise ValueError('bridge channel')
                    result=[store.ingest(e)]
                else:
                    channel=path.strip('/')
                    account=env.get({'telegram':'TELEGRAM_ACCOUNT_ID','whatsapp':'WA_PHONE_NUMBER_ID','max':'MAX_ACCOUNT_ID'}.get(channel,''))
                    if not account: return self.reply(404,{'error':'not_configured'})
                    events=normalize(channel,account,body,dict(self.headers),env)
                    result=[store.ingest(e) for e in events]
                return self.reply(200,{'accepted':result}) # durable insert completed before acknowledgement
            except PermissionError: return self.reply(403,{'error':'forbidden'})
            except (ValueError,KeyError,TypeError): return self.reply(400,{'error':'invalid_request'})
            except Exception: return self.reply(503,{'error':'temporary_failure'})
    return Handler

if __name__=='__main__':
    os.umask(0o077)
    env=os.environ
    if len(env.get('MIRA_INTERNAL_TOKEN',''))<32: raise SystemExit('Private MIRA_INTERNAL_TOKEN of at least 32 characters required')
    server=ThreadingHTTPServer(('127.0.0.1',int(env.get('MIRA_PORT','8789'))),handler(Store(env['MIRA_DB']),env))
    server.serve_forever()
