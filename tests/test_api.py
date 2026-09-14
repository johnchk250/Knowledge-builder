import contextlib
import io
import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import zipfile
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from chp.providers import APIProvider,SessionProvider,ProviderError,discover_session_models,_executable,_antigravity_tool_is_safe
from chp.service import Service
from chp.server import make_handler
from chp.store import dumps
from chp.ingest import ingest
from chp.patches import commit


class TransportTests(unittest.TestCase):
    def test_antigravity_persisted_cli_hint_works_without_launch_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);exe=root/'agy.exe';exe.write_bytes(b'fake');hint=root/'antigravity-cli.path';hint.write_text(str(exe),'utf-8')
            with patch('chp.providers.ANTIGRAVITY_CLI_HINT',hint),patch('chp.providers.shutil.which',return_value=None),patch.dict(os.environ,{},clear=True):
                self.assertEqual(Path(_executable('agy')),exe)

    def test_authenticated_session_transports_use_structured_results(self):
        expected={'mentions':['BC-04'],'concepts':['belt conveyor']}
        seen={}
        def codex_run(command,**kwargs):
            seen['codex']=command
            Path(command[command.index('--output-last-message')+1]).write_text(dumps(expected),'utf-8')
            return SimpleNamespace(returncode=0,stdout=dumps({'type':'item.completed','item':{'type':'agent_message'}}),stderr='')
        with patch('chp.providers._executable',return_value='codex'),patch('chp.providers.subprocess.run',side_effect=codex_run):
            result=SessionProvider({'provider':'codex_session','model':'gpt-test','effort':'low'}).ask('system',{'evidence':'BC-04'},[{'id':'ev_1','data':'aW1hZ2U='}])
        self.assertEqual(result,expected)
        self.assertIn('--image',seen['codex'])
        envelope={'event':'result','result':{'status':'SUCCESS','structured_output':expected}}
        def agy_run(command,**kwargs):
            seen['agy']={'command':command,'input':kwargs['input'],'env':kwargs['env'],'cwd':kwargs['cwd']}
            return SimpleNamespace(returncode=0,stdout=dumps(envelope),stderr='')
        with patch('chp.providers._executable',return_value='agy'),patch('chp.providers.subprocess.run',side_effect=agy_run):
            result=SessionProvider({'provider':'antigravity_session','model':'gemini-test','effort':'medium'}).ask('system',{'evidence':'BC-04'},[{'id':'ev_1','data':'aW1hZ2U='}])
        self.assertEqual(result,expected)
        self.assertIn('@image_0.png',seen['agy']['input'])
        self.assertIn('--new-project',seen['agy']['command'])
        self.assertIn('chp-analyzer',seen['agy']['command'])
        self.assertNotEqual(seen['agy']['env']['HOME'],str(Path.home()))
        self.assertEqual(Path(seen['agy']['cwd']).name,'workspace')
        self.assertEqual(Path(seen['agy']['env']['HOME']).parent,Path(seen['agy']['cwd']).parent)

    def test_antigravity_accepts_only_isolated_read_tools(self):
        expected={'mentions':['BC-04'],'concepts':['belt conveyor']}
        def event(step_index,state,name,parameters,error=None):
            info={'name':name,'parameters':parameters}
            if error: info['error']={'type':'TOOL_ERROR','message':error}
            return {'event':'step_update','step_update':{'step_index':step_index,'state':state,'step_type':'tool','tool_name':name,'tool_info':info}}
        def safe_run(command,**kwargs):
            root=Path(kwargs['cwd'])
            rows=[event(1,'DONE','view_file',{'AbsolutePath':str(root/'image_0.png')}),
                  event(2,'ERROR','run_command',{'CommandLine':'dir'},'permission denied'),
                  {'event':'result','result':{'status':'SUCCESS','structured_output':expected}}]
            return SimpleNamespace(returncode=0,stdout='\n'.join(dumps(x) for x in rows),stderr='')
        with patch('chp.providers._executable',return_value='agy'),patch('chp.providers.subprocess.run',side_effect=safe_run):
            result=SessionProvider({'provider':'antigravity_session','model':'gemini-test','effort':'medium'}).ask('system',{'evidence':'BC-04'},[{'id':'ev_1','data':'aW1hZ2U='}])
        self.assertEqual(result,expected)
        def unsafe_run(command,**kwargs):
            rows=[event(1,'DONE','run_command',{'CommandLine':'dir'}),{'event':'result','result':{'status':'SUCCESS','structured_output':expected}}]
            return SimpleNamespace(returncode=0,stdout='\n'.join(dumps(x) for x in rows),stderr='')
        with patch('chp.providers._executable',return_value='agy'),patch('chp.providers.subprocess.run',side_effect=unsafe_run),self.assertRaisesRegex(ProviderError,'outside the isolated'):
            SessionProvider({'provider':'antigravity_session','model':'gemini-test','effort':'medium'}).ask('system',{'evidence':'BC-04'})

    def test_antigravity_finish_marker_is_not_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(_antigravity_tool_is_safe(tmp,{'state':'ACTIVE','step_type':'tool','tool_name':'finish'}))
            self.assertTrue(_antigravity_tool_is_safe(tmp,{'state':'DONE','step_type':'finish'}))

    def test_antigravity_model_picker_is_parsed_dynamically(self):
        output='gemini-fast  Gemini Fast\nclaude-thinking\tClaude Thinking\n'
        with patch('chp.providers._executable',return_value='agy'),patch('chp.providers.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout=output,stderr='')):
            models=discover_session_models('antigravity_session')
        self.assertEqual([m['id'] for m in models],['gemini-fast','claude-thinking'])
        self.assertEqual(models[0]['efforts'],['medium'])

    def test_three_protocols_send_images_and_parse_json(self):
        expected={'summary':'No new evidence','operations':[]}
        responses={
            'openai':{'choices':[{'message':{'content':dumps(expected)},'finish_reason':'stop'}]},
            'anthropic':{'content':[{'type':'text','text':dumps(expected)}],'stop_reason':'end_turn'},
            'gemini':{'candidates':[{'content':{'parts':[{'text':dumps(expected)}]},'finishReason':'STOP'}]}}
        for kind in responses:
            with self.subTest(provider=kind):
                class Opener:
                    def open(inner,request,timeout):
                        inner.request=request
                        return io.BytesIO(dumps(responses[kind]).encode())
                opener=Opener()
                p=APIProvider({'provider':kind,'base_url':'','model':'test-model'},'test-secret')
                with patch('urllib.request.build_opener',return_value=opener):
                    result=p.ask('system',{'evidence':'BC-04'},[{'id':'ev_test','data':'aW1hZ2U='}])
                self.assertEqual(result,expected)
                body=json.loads(opener.request.data)
                self.assertIn('aW1hZ2U=',dumps(body))
                self.assertIn('ev_test',dumps(body))
                self.assertNotIn('test-secret',dumps(body))
                if kind=='openai':self.assertTrue(opener.request.full_url.endswith('/chat/completions'))
                elif kind=='anthropic':self.assertTrue(opener.request.full_url.endswith('/messages'))
                else:self.assertTrue(opener.request.full_url.endswith('/models/test-model:generateContent'))
    def test_errors_are_sanitized_and_truncation_rejected(self):
        class Opener:
            def open(self,*a,**kw):
                raise urllib.error.HTTPError('https://sensitive.example/key',401,'bad',{},io.BytesIO(b'source-secret'))
        p=APIProvider({'provider':'openai','model':'test'},'secret')
        with patch('urllib.request.build_opener',return_value=Opener()),self.assertRaises(ProviderError) as ctx:p.ask('x',{})
        self.assertNotIn('secret',str(ctx.exception));self.assertIn('401',str(ctx.exception))
        class Truncated:
            def open(self,*a,**kw):return io.BytesIO(b'{"choices":[{"finish_reason":"length","message":{"content":"{}"}}]}')
        with patch('urllib.request.build_opener',return_value=Truncated()),self.assertRaisesRegex(ProviderError,'truncated'):p.ask('x',{})
    def test_unsecured_remote_and_credential_urls_rejected(self):
        for url in ['http://example.com/v1','https://user:password@example.com/v1','https://example.com/v1?key=secret']:
            with self.assertRaises(ProviderError):APIProvider({'provider':'openai','base_url':url,'model':'test'},'secret')
    def test_real_orchestration_with_mock_api_transport(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=Service(tmp);store=s.store('plant');seen=[]
            s.save_settings({'provider':'openai','model':'test','base_url':'','vision':False,'api_key':'unit-test-key'})
            class Opener:
                def open(self,request,timeout):
                    body=json.loads(request.data);payload=json.loads(body['messages'][1]['content'][0]['text']);seen.append(payload)
                    if 'CURRENT_PLANT_CONTEXT' not in payload:out={'mentions':['BC-04'],'concepts':['equipment']}
                    else:
                        self_payload=payload['evidence'];prov={'confidence':.98,'origin':'explicit','evidence':[{'evidence_id':self_payload['id'],'quote':'BC-04 is equipment.'}]}
                        if payload['CURRENT_PLANT_CONTEXT']['entities']:
                            out={'summary':'Already known identity; no new fact','operations':[]}
                        else:out={'summary':'Introduce BC-04','operations':[dict(op='entity',id='tmp_b0_bc',label='BC-04',**prov)]}
                    if 'operations' in out: out['intake_assessment']={'route':'register','purpose':'Equipment index','questions':['Which equipment?'],'gaps':[],'reviewed_evidence_ids':[payload['evidence']['id']]}
                    return io.BytesIO(dumps({'choices':[{'message':{'content':dumps(out)},'finish_reason':'stop'}]}).encode())
            with patch('urllib.request.build_opener',return_value=Opener()):
                d=ingest(store,'one.txt',b'BC-04 is equipment.')['document']
                s.start('plant',d['id']);s.jobs.join()
                p=s.state('plant')['proposals'][0]
                self.assertEqual(p['findings']['errors'],[])
                self.assertEqual(store.version(),0)
                commit(store,p['id'])
                d2=ingest(store,'two.txt',b'Second record. BC-04 is equipment.')['document']
                s.start('plant',d2['id']);s.jobs.join()
                p2=s.state('plant')['proposals'][0]
                self.assertEqual(p2['findings']['errors'],[])
                self.assertEqual(len(seen),4)
                self.assertEqual(seen[-1]['CURRENT_PLANT_CONTEXT']['entities'][0]['label'],'BC-04')
                self.assertEqual(len(store.rows('SELECT * FROM run_steps')),4)
                self.assertNotIn('unit-test-key',dumps(s.export('plant')))


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.service=Service(self.tmp.name)
        self.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(self.service,'test-token',0))
        self.port=self.server.server_port
        self.server.RequestHandlerClass=make_handler(self.service,'test-token',self.port)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):
        self.service.jobs.join();self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
    def request(self,path,body=None,headers=None):
        data=None if body is None else body if isinstance(body,bytes) else dumps(body).encode()
        h={'X-CHP-Token':'test-token','Content-Type':'application/json',**(headers or {})}
        return urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{self.port}'+path,data=data,headers=h),timeout=5)
    def test_upload_analyze_review_and_download_backup_over_http(self):
        with self.request('/') as r:self.assertIn(b'CHP Operations Helper',r.read())
        with self.request('/api/bootstrap') as r:self.assertEqual(json.load(r)['token'],'test-token')
        with self.request('/api/documents?name=note.txt',b'BC-04 is equipment.',{'Content-Type':'application/octet-stream'}) as r:self.assertFalse(json.load(r)['duplicate'])
        with self.request('/api/demo/next',{}) as r:self.assertIn('run_id',json.load(r))
        self.service.jobs.join()
        with self.request('/api/state',headers={'X-Workspace':'demo'}) as r:p=json.load(r)['proposals'][0]
        with self.request('/api/proposals/accept',{'id':p['id']},{'X-Workspace':'demo'}) as r:self.assertEqual(json.load(r)['version'],1)
        with self.request('/api/backup',headers={'X-Workspace':'demo'}) as r:data=r.read()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            self.assertIn('plant.sqlite3',z.namelist());self.assertTrue(any(n.startswith('originals/') for n in z.namelist()))
        with self.request('/api/state') as r:self.assertEqual(json.load(r)['model']['version'],0)

    def test_authenticated_backend_model_picker_route(self):
        catalog={'provider':'codex_session','models':[{'id':'gpt-test','display_name':'GPT Test','description':'Test model','efforts':['low'],'default_effort':'low','default':True}],'cached':False}
        with patch.object(self.service,'models',return_value=catalog) as models:
            with self.request('/api/models?provider=codex_session&refresh=1') as response:self.assertEqual(json.load(response),catalog)
        models.assert_called_once_with('codex_session',True)


    def test_client_refresh_cancels_pending_shutdown(self):
        with self.request('/api/client/close',{'client_id':'client-old-0001'}) as response:self.assertEqual(json.load(response)['status'],'closing')
        with self.request('/api/client/open',{'client_id':'client-new-0001'}) as response:self.assertEqual(json.load(response)['status'],'open')
        with self.request('/api/state') as response:self.assertEqual(json.load(response)['workspace'],'plant')

    def test_client_close_shuts_down_server(self):
        tmp=tempfile.TemporaryDirectory();service=Service(tmp.name)
        server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(service,'close-token',0,.05));port=server.server_port
        server.RequestHandlerClass=make_handler(service,'close-token',port,.05)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            data=dumps({'client_id':'client-close-0001'}).encode();headers={'X-CHP-Token':'close-token','Content-Type':'application/json'}
            urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{port}/api/client/close',data=data,headers=headers),timeout=2).read()
            thread.join(1);self.assertFalse(thread.is_alive())
        finally:
            server.server_close();tmp.cleanup()

    def test_startup_without_client_shuts_down_server(self):
        tmp=tempfile.TemporaryDirectory();service=Service(tmp.name)
        handler=make_handler(service,'startup-token',0,.05)
        server=ThreadingHTTPServer(('127.0.0.1',0),handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            handler.arm_startup_shutdown(server,.05)
            thread.join(1);self.assertFalse(thread.is_alive())
        finally:
            server.server_close();tmp.cleanup()

    def test_closing_old_client_does_not_stop_new_client(self):
        tmp=tempfile.TemporaryDirectory();service=Service(tmp.name)
        server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(service,'client-token',0,.05));port=server.server_port
        server.RequestHandlerClass=make_handler(service,'client-token',port,.05)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        headers={'X-CHP-Token':'client-token','Content-Type':'application/json'}
        def post(path,client_id):
            data=dumps({'client_id':client_id}).encode()
            return urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{port}'+path,data=data,headers=headers),timeout=2)
        try:
            with post('/api/client/open','client-old-0002') as response:json.load(response)
            with post('/api/client/open','client-new-0002') as response:json.load(response)
            with post('/api/client/close','client-old-0002') as response:json.load(response)
            __import__('time').sleep(.12);self.assertTrue(thread.is_alive())
            with post('/api/client/close','client-new-0002') as response:json.load(response)
            thread.join(1);self.assertFalse(thread.is_alive())
        finally:
            server.server_close();tmp.cleanup()

    def test_client_lease_disconnect_shuts_down_server(self):
        tmp=tempfile.TemporaryDirectory();service=Service(tmp.name)
        server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(service,'lease-token',0,.05,.02));port=server.server_port
        server.RequestHandlerClass=make_handler(service,'lease-token',port,.05,.02)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        response=None
        try:
            data=dumps({'client_id':'client-lease-0001'}).encode();headers={'X-CHP-Token':'lease-token','Content-Type':'application/json'}
            response=urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{port}/api/client/lease',data=data,headers=headers),timeout=2)
            self.assertTrue(response.read(1));self.assertTrue(thread.is_alive())
            response.close();response=None
            thread.join(1);self.assertFalse(thread.is_alive())
        finally:
            if response: response.close()
            server.server_close();tmp.cleanup()

    def test_antigravity_session_can_be_selected(self):
        catalog={'provider':'antigravity_session','models':[{'id':'gemini-test','display_name':'Gemini Test','description':'Test model','efforts':['medium'],'default_effort':'medium','default':True}],'cached':False}
        with patch.object(self.service,'models',return_value=catalog):
            with self.request('/api/settings',{'provider':'antigravity_session','model':'gemini-test','effort':'medium','base_url':'','vision':True}) as response:
                saved=json.load(response)
        self.assertEqual(saved['provider'],'antigravity_session');self.assertTrue(saved['vision'])


    def test_3d_routes_paused_but_historical_assets_backed_up(self):
        folder=self.service.store('plant').root/'reconstructions'/'ent_a123'
        folder.mkdir(parents=True)
        (folder/'14DR2.step').write_bytes(b'preserved historical asset')
        for path in ('/api/spatial','/api/reconstruction','/viewer3d.js','/reconstruction.html'):
            with self.assertRaises(urllib.error.HTTPError) as caught: self.request(path)
            self.assertEqual(caught.exception.code,410)
            caught.exception.close()
        with self.request('/api/backup') as response:
            with zipfile.ZipFile(io.BytesIO(response.read())) as z:
                self.assertEqual(z.read('reconstructions/ent_a123/14DR2.step'),b'preserved historical asset')
        with self.request('/') as response:
            html=response.read()
            self.assertNotIn(b'data-nav="spatial"',html)
            self.assertIn(b'Operating history',html)

    def test_operational_read_routes(self):
        ingest(self.service.store('plant'),'index.txt',b'BC-04 feeder manual')
        with self.request('/api/search?q=BC-04') as response: self.assertEqual(json.load(response)['total'],1)
        with self.request('/api/migration') as response: self.assertEqual(json.load(response)['counts']['documents'],1)
        with self.request('/api/events') as response: self.assertEqual(json.load(response),[])
        with self.request('/operations-ui.js') as response: self.assertIn(b'Trace equipment connections',response.read())

    def test_understanding_http_routes_and_revision_history(self):
        with self.request('/api/understanding') as r:self.assertEqual(json.load(r)['revision'],1)
        body={'action':'note','kind':'convention','text':'Never infer electrical isolation from a stopped motor.','scope':[],'expected_revision':1}
        with self.request('/api/understanding/update',body) as r:self.assertEqual(json.load(r)['revision'],2)
        with self.request('/api/understanding/history?revision=1') as r:self.assertEqual(json.load(r)['notes'],[])
        with self.request('/api/revision') as r:self.assertEqual(json.load(r)['understanding'],2)
        with self.assertRaises(urllib.error.HTTPError) as ctx:self.request('/api/understanding/update',body)
        self.assertEqual(ctx.exception.code,400)

    def test_cross_origin_host_and_csrf_blocked(self):
        for headers in [{'Origin':'https://attacker.example'},{'Host':'attacker.example'},{'X-CHP-Token':''}]:
            # Header rejection happens before reading a body. An empty POST avoids
            # Windows resetting a socket with unread request bytes, while still
            # requiring 403 (rather than the 400 a valid token/host would receive).
            with self.assertRaises(urllib.error.HTTPError) as ctx:self.request('/api/demo/next',b'',headers)
            self.assertEqual(ctx.exception.code,403)
            ctx.exception.close()
    def test_demo_image_query_uses_correct_workspace(self):
        try:import fitz
        except ImportError:self.skipTest('Optional PyMuPDF not installed')
        doc=fitz.open();doc.new_page();pdf=doc.tobytes();doc.close()
        store=self.service.store('demo');ingest(store,'scan.pdf',pdf)
        ev=store.rows('SELECT * FROM evidence')[0]
        with self.request('/api/render/'+ev['id']+'?workspace=demo') as r:self.assertTrue(r.read().startswith(b'\x89PNG'))

if __name__=='__main__':unittest.main()
