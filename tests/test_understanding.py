import copy
import io
import json
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from chp import understanding as u, demo
from chp.service import Service
from chp.store import Store, dumps
from chp.ingest import ingest
from chp.patches import commit


class UnderstandingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.s=Service(self.tmp.name);self.store=self.s.store('plant')
    def tearDown(self):self.s.jobs.join();self.tmp.cleanup()
    def add(self,text='Treat maintenance observations as time-specific, not nameplate specifications.',scope=None,kind='lesson'):
        return u.update(self.store,{'action':'note','text':text,'scope':scope or [],'kind':kind,'expected_revision':u.current(self.store)['revision']})
    def test_charter_preloaded_and_workspace_isolation(self):
        memory=u.current(self.store)
        self.assertIn('retain shift and breakdown history',memory['brief'])
        self.assertIn('network',memory['brief']);self.assertIn('original evidence',memory['brief'])
        self.add();self.assertEqual(len(u.current(self.s.store('demo'))['notes']),0)
        self.assertEqual(self.store.version(),0)
    def test_migration_preserves_existing_model_and_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            old=Store(tmp+'/plant');file=demo.EXAMPLES/demo.FILES[0]
            ingest(old,file.name,file.read_bytes())
            before=old.rows('SELECT * FROM evidence')
            upgraded=Service(tmp)
            self.assertEqual(upgraded.store('plant').rows('SELECT * FROM evidence'),before)
            self.assertEqual(upgraded.store('plant').rows("SELECT value FROM meta WHERE key='schema_version'")[0]['value'],'4')
            self.assertEqual(u.current(upgraded.store('plant'))['revision'],1)
            self.assertEqual(u.current(Service(tmp).store('plant'))['revision'],1)
    def test_versioned_edit_retire_and_concurrent_save(self):
        self.add();memory=u.current(self.store);nid=memory['notes'][0]['id']
        with self.assertRaisesRegex(ValueError,'changed'):u.update(self.store,{'action':'brief','brief':'Changed purpose','expected_revision':1})
        u.update(self.store,{'action':'retire','id':nid,'expected_revision':2})
        self.assertFalse(u.current(self.store)['notes'])
        self.assertEqual(len(json.loads(self.store.rows('SELECT notes FROM context_revisions WHERE revision=2')[0]['notes'])),1)
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store.transaction() as db:db.execute('DELETE FROM context_revisions')
    def test_scope_selection_and_questions_are_tentative(self):
        self.add('GB-04 ratio remains unknown.',['GB-04'],'question')
        self.add('Do not equate PLC command with motor running feedback.',kind='convention')
        snap=u.current(self.store)
        unrelated=u.context(snap,self.store,['BC-04'])
        self.assertEqual(len(unrelated['reviewed_notes']),1)
        related=u.context(snap,self.store,['Gearbox 04'])
        self.assertEqual(len(related['reviewed_notes']),2)
        self.assertEqual(related['reviewed_notes'][0]['kind'],'question')
        self.assertIn('Hypothesis notes remain tentative',u.CONTEXT_RULES)
        self.assertFalse(self.store.model()['assertions'])
    def test_context_budget_stops_instead_of_dropping_applicable_rules(self):
        for i in range(14):self.add('x'*1100+str(i),['BC-04'])
        with self.assertRaisesRegex(ValueError,'exceeds'):u.context(u.current(self.store),self.store,['BC4'])
        self.assertEqual(len(u.context(u.current(self.store),self.store,['GB-04'])['reviewed_notes']),0)
    def test_correction_becomes_reviewable_lesson_not_automatic_rule(self):
        self.s.next_demo();self.s.jobs.join();p=self.s.state('demo')['proposals'][0]
        self.s.edit_proposal('demo',p['id'],p['body'],{'kind':'lesson','text':'Keep observations separate from nameplate specifications.','scope':[]})
        store=self.s.store('demo');mem=u.state(store)
        self.assertFalse(mem['notes']);self.assertEqual(mem['suggestions'][0]['author'],'operator correction')
        commit(store,p['id'])
        sid=mem['suggestions'][0]['id'];u.decide(store,{'id':sid,'decision':'approve','expected_revision':1})
        self.assertEqual(len(u.current(store)['notes']),1)
        self.assertEqual(store.version(),1)
        with self.assertRaises(ValueError):u.decide(store,{'id':sid,'decision':'approve','expected_revision':2})
    def test_guidance_change_blocks_old_model_proposal(self):
        self.s.next_demo();self.s.jobs.join();p=self.s.state('demo')['proposals'][0];store=self.s.store('demo')
        u.update(store,{'action':'note','text':'Check component-level names before treating them as aliases.','kind':'convention','scope':[],'expected_revision':1})
        with self.assertRaisesRegex(ValueError,'understanding changed'):commit(store,p['id'])
        self.assertEqual(store.version(),0)
    def test_bad_memory_evidence_is_blocked_and_rejection_keeps_it_inactive(self):
        self.s.next_demo();self.s.jobs.join();p=self.s.state('demo')['proposals'][0];store=self.s.store('demo')
        body={'kind':'convention','text':'Invented rule','scope':[],'reason':'test','evidence':[{'evidence_id':'unknown','quote':'invented'}]}
        sid=u.suggest(store,p['run_id'],p['id'],body)
        with self.assertRaisesRegex(ValueError,'failed evidence'):u.decide(store,{'id':sid,'decision':'approve','expected_revision':1})
        u.decide(store,{'id':sid,'decision':'reject'})
        self.assertFalse(u.current(store)['notes']);self.assertEqual(u.current(store)['revision'],1)
    def test_every_api_stage_gets_purpose_notes_and_recap_with_audit(self):
        self.add('Never infer that a stopped motor is electrically isolated.',kind='convention')
        self.s.save_settings({'provider':'openai','model':'test','base_url':'','vision':False,'api_key':'test-key'})
        requests=[]
        class Opener:
            def open(inner,request,timeout):
                wire=json.loads(request.data);payload=json.loads(wire['messages'][1]['content'][0]['text']);requests.append(payload)
                if 'CURRENT_PLANT_CONTEXT' not in payload:out={'mentions':['BC-04'],'concepts':['equipment']}
                else:out={'summary':'Review source','operations':[],'memory_suggestions':[{'kind':'question','text':'Is BC-04 an installed asset or only planned?','scope':['BC-04'],'reason':'The source does not establish installation status.','evidence':[{'evidence_id':payload['evidence']['id'],'quote':'BC-04 is equipment.'}]}]}
                if 'operations' in out: out['intake_assessment']={'route':'reference','purpose':'Source review','questions':[],'gaps':[],'reviewed_evidence_ids':[payload['evidence']['id']]}
                return io.BytesIO(dumps({'choices':[{'message':{'content':dumps(out)},'finish_reason':'stop'}]}).encode())
        d=ingest(self.store,'test.txt',b'BC-04 is equipment.')['document']
        with patch('urllib.request.build_opener',return_value=Opener()):self.s.start('plant',d['id']);self.s.jobs.join()
        self.assertEqual(len(requests),2)
        for r in requests:
            self.assertIn('PROJECT_UNDERSTANDING',r)
            self.assertIn('Coal Handling Plant',r['PROJECT_UNDERSTANDING']['project_brief'])
            self.assertEqual(len(r['PROJECT_UNDERSTANDING']['reviewed_notes']),1)
            self.assertEqual(r['PROJECT_UNDERSTANDING']['derived_model_recap']['plant_version'],0)
        mem=u.state(self.store);self.assertEqual(len(mem['suggestions']),1);self.assertFalse(mem['suggestions'][0]['errors'])
        self.assertEqual(len(mem['notes']),1)
        audit=json.loads(self.store.rows("SELECT request FROM run_steps WHERE stage='propose'")[0]['request'])
        self.assertEqual(audit['PROJECT_UNDERSTANDING']['revision'],2)
        self.assertIn('context_revisions',self.s.export('plant'))
    def test_memory_change_mid_analysis_fails_without_partial_commit(self):
        self.s.save_settings({'provider':'openai','model':'test','base_url':'','vision':False,'api_key':'test-key'})
        d=ingest(self.store,'test.txt',b'BC-04 is equipment.')['document'];owner=self
        class Provider:
            def ask(self,*args):
                owner.add('Use approved naming conventions.')
                return {'mentions':['BC-04'],'concepts':['equipment']}
        with patch('chp.service.APIProvider',return_value=Provider()):self.s.start('plant',d['id']);self.s.jobs.join()
        self.assertEqual(self.store.rows('SELECT status FROM runs')[0]['status'],'failed')
        self.assertFalse(self.store.rows('SELECT * FROM proposals'));self.assertEqual(self.store.version(),0)

if __name__=='__main__':unittest.main()
