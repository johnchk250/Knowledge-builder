"""Loopback-only HTTP application with same-origin + session CSRF protection."""
import argparse
import contextlib
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .ingest import ingest, MAX_BYTES
from .patches import commit
from .service import Service
from . import understanding
from . import operating_model, usage_intake
from .store import dumps

STATIC=Path(__file__).resolve().parent.parent/'dist'
CLIENT_CLOSE_GRACE=4.0
CLIENT_LEASE_PING=0.5
CLIENT_STARTUP_GRACE=20.0
FAVICON_SVG=b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#1d665b"/><text x="16" y="21" text-anchor="middle" font-family="sans-serif" font-weight="700" font-size="12" fill="#fff">CHP</text></svg>'


def make_handler(service,token,port,close_grace=CLIENT_CLOSE_GRACE,lease_ping=CLIENT_LEASE_PING,keep_alive=False):
    lifecycle_lock=threading.Lock()
    lifecycle={'timer':None,'clients':set()}

    def cancel_close():
        with lifecycle_lock:
            timer=lifecycle['timer']
            lifecycle['timer']=None
            if timer: timer.cancel()

    def schedule_close(server,delay=close_grace):
        if keep_alive: return
        cancel_close()
        timer=threading.Timer(delay,server.shutdown)
        timer.daemon=True
        with lifecycle_lock: lifecycle['timer']=timer
        timer.start()

    def client_open(client_id):
        if not isinstance(client_id,str) or not re.fullmatch(r'[A-Za-z0-9._:-]{8,128}',client_id):
            raise ValueError('Invalid client session')
        cancel_close()
        with lifecycle_lock: lifecycle['clients'].add(client_id)

    def client_close(server,client_id):
        if not isinstance(client_id,str) or not re.fullmatch(r'[A-Za-z0-9._:-]{8,128}',client_id):
            raise ValueError('Invalid client session')
        with lifecycle_lock:
            lifecycle['clients'].discard(client_id)
            remaining=bool(lifecycle['clients'])
        if not remaining: schedule_close(server)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self,fmt,*args):
            # No request query strings, document names, headers or payloads in console logs.
            pass

        def begin_response(self,status,length,content_type,extra=None):
            self.send_response(status)
            self.send_header('Content-Type',content_type)
            self.send_header('Content-Length',str(length))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Referrer-Policy','no-referrer')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            for k,v in (extra or {}).items(): self.send_header(k,v)
            self.end_headers()

        def send(self,status,data,content_type='application/json; charset=utf-8',extra=None):
            if not isinstance(data,bytes): data=dumps(data).encode('utf-8')
            self.begin_response(status,len(data),content_type,extra)
            try: self.wfile.write(data)
            except (BrokenPipeError,ConnectionResetError): pass

        def send_file(self,path,content_type,extra=None):
            import shutil
            self.begin_response(200,path.stat().st_size,content_type,extra)
            try:
                with path.open('rb') as file: shutil.copyfileobj(file,self.wfile,1024*1024)
            except (BrokenPipeError,ConnectionResetError): pass

        def check(self,write=False):
            host=self.headers.get('Host','')
            if host not in (f'127.0.0.1:{port}',f'localhost:{port}'): raise PermissionError('Invalid local host')
            origin=self.headers.get('Origin')
            if origin and origin not in (f'http://127.0.0.1:{port}',f'http://localhost:{port}'): raise PermissionError('Cross-origin requests are not permitted')
            if self.headers.get('Sec-Fetch-Site')=='cross-site': raise PermissionError('Cross-site requests are not permitted')
            if write and not secrets.compare_digest(self.headers.get('X-CHP-Token',''),token): raise PermissionError('Refresh the page to obtain the local session token')

        def body(self,raw=False):
            length=int(self.headers.get('Content-Length','0'))
            limit = MAX_BYTES if raw else (8*1024*1024 if urllib.parse.urlsplit(self.path).path.startswith('/api/spatial/') else 1024*1024)
            if length<=0 or length>limit: raise ValueError('Invalid request size')
            if not raw and self.headers.get('Content-Type','').split(';')[0]!='application/json': raise ValueError('JSON requests are required')
            data=self.rfile.read(length)
            if len(data)!=length: raise ValueError('Incomplete upload')
            return data if raw else json.loads(data)

        def do_GET(self): self.dispatch(False)
        def do_HEAD(self): self.dispatch(False,True)
        def do_POST(self): self.dispatch(True)

        def dispatch(self,write,head=False):
            try:
                self.check(write)
                parsed=urllib.parse.urlsplit(self.path)
                path=parsed.path
                query=urllib.parse.parse_qs(parsed.query)
                workspace=self.headers.get('X-Workspace',query.get('workspace',['plant'])[0])
                store=service.store(workspace)
                if path.startswith('/api/spatial') or path.startswith('/api/reconstruction') or path in ('/viewer3d.js','/spatial-ui.js','/reconstruction.html','/reconstruction.js','/reconstruction.css'):
                    return self.send(410, {'error':'3D is paused in the operations-focused app. Historical assets remain in full backups.'})
                if not write:
                    if path=='/favicon.ico': return self.send(200,FAVICON_SVG,'image/svg+xml')
                    if path=='/api/bootstrap': return self.send(200,{'token':token,'settings':service.settings()})
                    if path=='/api/state': return self.send(200,service.state(workspace))
                    if path=='/api/proposal': return self.send(200,service.proposal(workspace,query.get('id',[''])[0]))
                    if path=='/api/search': return self.send(200,usage_intake.search_sources(store,query.get('q',[''])[0]))
                    if path=='/api/events': return self.send(200,operating_model.events(store,query.get('equipment',[None])[0],query.get('version',[None])[0]))
                    if path=='/api/migration': return self.send(200,operating_model.migration_report(store))
                    if path=='/api/network': return self.send(200,operating_model.trace(store,query.get('equipment',[''])[0],query.get('network',['material'])[0],query.get('direction',['upstream'])[0],query.get('condition',[''])[0],query.get('as_of',[None])[0],query.get('follow_all',['0'])[0]=='1'))
                    if path=='/api/revision':
                        return self.send(200,{'version':store.version(),'understanding':understanding.current(store)['revision'],
                            'memory_queue':store.rows('SELECT (SELECT count(*) FROM context_suggestions) suggestions,(SELECT count(*) FROM context_decisions) decisions')[0],
                            'documents':store.rows('SELECT count(*) n FROM documents')[0]['n'],
                            'proposals':store.rows('SELECT count(*) n,max(created) latest,max(decision) decision FROM proposals')[0],
                            'edits':store.rows('SELECT count(*) n FROM proposal_edits')[0]['n'],
                            'runs':store.rows('SELECT id,status,progress,error FROM runs ORDER BY created DESC LIMIT 10')})
                    if path=='/api/understanding/history':
                        rows=store.rows('SELECT * FROM context_revisions WHERE revision=?',(query.get('revision',[''])[0],))
                        if not rows: raise ValueError('Understanding revision not found')
                        return self.send(200,{**rows[0],'notes':json.loads(rows[0]['notes'])})
                    if path=='/api/understanding': return self.send(200,understanding.state(store))
                    if path=='/api/settings': return self.send(200,service.settings())
                    if path=='/api/models': return self.send(200,service.models(query.get('provider',[''])[0],query.get('refresh',['0'])[0]=='1'))
                    if path=='/api/model': return self.send(200,store.model(query.get('version',[None])[0]))
                    if path=='/api/transmission': return self.send(200,service.transmission(workspace,query.get('document',[''])[0]))
                    if path=='/api/evidence':
                        if 'id' in query: rows=store.rows('SELECT * FROM evidence WHERE id=?',(query['id'][0],))
                        else: rows=store.rows('SELECT * FROM evidence WHERE document_id=? ORDER BY page,rowid',(query.get('document',[''])[0],))
                        return self.send(200,rows)
                    if path=='/api/export': return self.send(200,service.export(workspace),extra={'Content-Disposition':'attachment; filename="chp-knowledge-export.json"'})
                    if path=='/api/backup':
                        # sqlite backup API captures a consistent database, including its WAL contents.
                        import zipfile,tempfile
                        with tempfile.TemporaryDirectory() as tmp:
                            dest=Path(tmp)/'plant.sqlite3'
                            with contextlib.closing(store.connect()) as src, contextlib.closing(sqlite3.connect(dest)) as target: src.backup(target)
                            backup=Path(tmp)/'backup.zip'
                            with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
                                z.write(dest,'plant.sqlite3')
                                for folder in ['originals','renders','meshes']:
                                    for file in (store.root/folder).iterdir():
                                        if file.is_file(): z.write(file,folder+'/'+file.name)
                                for file in (store.root/'reconstructions').rglob('*'):
                                    if file.is_file():z.write(file,str(file.relative_to(store.root)))
                            return self.send_file(backup,'application/zip',{'Content-Disposition':'attachment; filename="chp-workspace-backup.zip"'})
                    if path.startswith('/api/original/'):
                        rows=store.rows('SELECT * FROM documents WHERE id=?',(path.rsplit('/',1)[1],))
                        if not rows: raise ValueError('Document not found')
                        doc=rows[0]
                        orig_path=store.root/'originals'/doc['sha256']
                        if not orig_path.is_file(): raise ValueError('Original file is not present in this local folder')
                        if orig_path.stat().st_size==0: raise ValueError('Original file is empty in this local folder')
                        disposition='attachment' if query.get('download',['0'])[0]=='1' else 'inline'
                        extra={'Content-Disposition':disposition+"; filename*=UTF-8''"+urllib.parse.quote(doc['name'])}
                        content_type=doc['media_type'] or 'application/octet-stream'
                        if head: return self.begin_response(200,orig_path.stat().st_size,content_type,extra)
                        return self.send_file(orig_path,content_type,extra)
                    if path.startswith('/api/render/'):
                        rows=store.rows('SELECT image FROM evidence WHERE id=?',(path.rsplit('/',1)[1],))
                        if not rows or not rows[0]['image']: raise ValueError('Rendered evidence not found')
                        render_path=store.root/'renders'/rows[0]['image']
                        if not render_path.exists(): raise ValueError('Rendered page image is not present in this local folder')
                        return self.send(200,render_path.read_bytes(),'image/png')
                    if path.startswith('/api/evidence-detail/'):
                        from .evidence_view import detail_png
                        return self.send(200,detail_png(store,path.rsplit('/',1)[1],query.get('region',[''])[0]),'image/png')
                    if path.startswith('/api/run/'):
                        return self.send(200,store.rows('SELECT * FROM run_steps WHERE run_id=? ORDER BY created',(path.rsplit('/',1)[1],)))
                    if path in ('/','/index.html','/app.js','/style.css','/operations-ui.js','/plant-model.js','/plant-explorer.js','/plant-explorer.css','/plant-scene-model.js','/plant-yard-3d.js','/plant-scene.js','/plant-scene.css'):
                        file=STATIC/('index.html' if path=='/' else path[1:])
                        return self.send(200,file.read_bytes(),mimetypes.guess_type(str(file))[0] or 'text/plain')
                else:
                    if path=='/api/client/lease':
                        body=self.body()
                        if not isinstance(body,dict): raise ValueError('Request must be a JSON object')
                        client_id=body.get('client_id')
                        client_open(client_id)
                        self.send_response(200)
                        self.send_header('Content-Type','text/event-stream; charset=utf-8')
                        self.send_header('Cache-Control','no-store')
                        self.send_header('X-Content-Type-Options','nosniff')
                        self.send_header('Referrer-Policy','no-referrer')
                        self.end_headers()
                        try:
                            while True:
                                self.wfile.write(b': chp-client-lease\n\n');self.wfile.flush();time.sleep(lease_ping)
                        except (BrokenPipeError,ConnectionResetError,OSError):
                            pass
                        finally:
                            client_close(self.server,client_id)
                        return
                    if path=='/api/client/open':
                        body=self.body()
                        if not isinstance(body,dict): raise ValueError('Request must be a JSON object')
                        client_open(body.get('client_id'))
                        return self.send(200,{'status':'open'})
                    if path=='/api/client/close':
                        body=self.body()
                        if not isinstance(body,dict): raise ValueError('Request must be a JSON object')
                        client_close(self.server,body.get('client_id'))
                        return self.send(200,{'status':'closing','grace_seconds':close_grace})
                    if path=='/api/documents':
                        content=self.body(raw=True)
                        result=ingest(store,query.get('name',[''])[0],content,query.get('revision',[''])[0],query.get('authority',['Unclassified'])[0])
                        return self.send(200,result)
                    body=self.body()
                    if not isinstance(body,dict): raise ValueError('Request must be a JSON object')
                    if path=='/api/events': return self.send(200,service.record_operation(workspace,body))
                    if path=='/api/corrections': return self.send(200,service.record_operation(workspace,body,correction=True))
                    if path=='/api/understanding/update': return self.send(200,understanding.update(store,body))
                    if path=='/api/understanding/decide': return self.send(200,understanding.decide(store,body))
                    if path=='/api/settings': return self.send(200,service.save_settings(body))
                    if path=='/api/analyze': return self.send(200,service.start(workspace,body.get('document_id','')))
                    if path=='/api/demo/next': return self.send(200,service.next_demo())
                    if path=='/api/proposals/accept': return self.send(200,commit(store,body.get('id','')))
                    if path=='/api/proposals/reject': return self.send(200,service.reject(workspace,body.get('id','')))
                    if path=='/api/proposals/edit': return self.send(200,service.edit_proposal(workspace,body.get('id',''),body.get('body'),body.get('lesson')))
                self.send(404,{'error':'Not found'})
            except PermissionError as exc: self.send(403,{'error':str(exc)})
            except (ValueError,KeyError,TypeError) as exc: self.send(400,{'error':str(exc)[:1500]})
            except Exception:
                self.send(500,{'error':'Local operation failed. No partial knowledge commit was accepted. Check available disk space and file permissions.'})
    Handler.arm_startup_shutdown=staticmethod(lambda server,delay=CLIENT_STARTUP_GRACE:schedule_close(server,delay))
    return Handler


def main():
    parser=argparse.ArgumentParser(description='CHP Knowledge Builder — local evidence and plant model')
    parser.add_argument('--data',default=str(Path(__file__).resolve().parent.parent/'data'))
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--no-browser',action='store_true')
    parser.add_argument('--keep-alive',action='store_true',help='Keep the server running even when all browser tabs close')
    args=parser.parse_args()
    if not 1024<=args.port<=65535: parser.error('Port must be between 1024 and 65535')
    # Prevent two worker processes using the same data directory. OS releases the lock on exit.
    root=Path(args.data).resolve(); root.mkdir(parents=True,exist_ok=True)
    pid_path=root/'server.pid'
    lock=open(root/'app.lock','a+b')
    try:
        if __import__('os').name=='nt':
            import msvcrt
            lock.seek(0); lock.write(b'0'); lock.flush(); lock.seek(0)
            msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except OSError: parser.error('This data directory is already open in another CHP Knowledge Builder process.')
    service=Service(root)
    pid_path.write_text(str(os.getpid()),encoding='ascii')
    handler=make_handler(service,secrets.token_urlsafe(32),args.port,keep_alive=args.keep_alive)
    server=ThreadingHTTPServer(('127.0.0.1',args.port),handler)
    server.daemon_threads=True
    url=f'http://127.0.0.1:{args.port}'
    print(f'CHP Knowledge Builder: {url}\nData: {root}\nPress Ctrl+C to stop. API keys entered in Settings remain in memory only.',flush=True)
    if not args.no_browser:
        handler.arm_startup_shutdown(server)
        threading.Timer(.5,lambda:webbrowser.open(url)).start()
    try: server.serve_forever()
    except KeyboardInterrupt: print('\nStopped. Unfinished analyses can be retried on restart.')
    finally:
        server.server_close(); lock.close()
        try:
            if pid_path.read_text('ascii').strip()==str(os.getpid()): pid_path.unlink()
        except (OSError,ValueError): pass


if __name__=='__main__': main()
