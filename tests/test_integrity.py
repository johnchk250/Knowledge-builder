import contextlib
import copy
import hashlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from chp.store import Store, dumps, uid, now, normalize
from chp.ingest import ingest, chunks
from chp.service import Service
from chp.patches import validate, commit
from chp import demo


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=Store(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def sample(self,index=0):
        file=demo.EXAMPLES/demo.FILES[index]
        doc=ingest(self.store,file.name,file.read_bytes(),str(index),'Training')['document']
        ev=self.store.rows('SELECT * FROM evidence WHERE document_id=?',(doc['id'],))
        return doc,ev,demo.proposal(self.store,doc,ev)
    def proposal(self,body,document,base=None):
        base=self.store.version() if base is None else base
        rid,pid=uid('run'),uid('prop')
        with self.store.transaction() as db:
            db.execute('INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?)',(rid,document,'complete',base,'test',now(),'done',None,'{}'))
            db.execute('INSERT INTO proposals VALUES(?,?,?,?,?,?,?,?,?)',(pid,rid,document,base,dumps(body),'pending',dumps(validate(self.store,body,document,base,db)),now(),None))
        return pid
    def accepted_sample(self,index):
        doc,ev,body=self.sample(index)
        findings=validate(self.store,body,doc['id'],self.store.version())
        self.assertEqual(findings['errors'],[])
        commit(self.store,self.proposal(body,doc['id']))
        return doc,ev,body
    def test_progressive_identity_conflict_and_restructure(self):
        original=[]
        for i in range(3):
            d,e,b=self.accepted_sample(i)
            original.extend(e)
        m=self.store.model()
        self.assertEqual(len(m['entities']),5)
        bc=next(e for e in m['entities'] if e['label']=='BC-04')
        self.assertIn('BC4',bc['aliases'])
        self.assertEqual(len(m['conflicts']),1)
        capacity=[a for a in m['assertions'] if a['predicate']=='rated_capacity']
        self.assertEqual({a['value'] for a in capacity},{800,1000})
        motor=next(e for e in m['entities'] if e['label']=='M-04')
        subsystem=next(e for e in m['entities'] if e['label']=='DS-04')
        parents=[a for a in m['assertions'] if a['subject']==motor['id'] and a['predicate']=='part_of']
        self.assertEqual(len(parents),2)
        self.assertEqual([a['object_entity'] for a in parents if not a['retirement']],[subsystem['id']])
        self.assertEqual([len(self.store.model(v)['entities']) for v in range(4)],[0,1,4,5])
        self.assertEqual(self.store.rows('SELECT * FROM evidence ORDER BY rowid'),original)
        self.assertEqual(Store(self.tmp.name).model()['version'],3)
        # Neighborhood retrieval resolves normalized tags without automatically inventing a merge.
        relevant=self.store.relevant(['BC4'],['rated capacity'])
        self.assertIn(bc['id'],[e['id'] for e in relevant['entities']])
        self.assertLessEqual(len(dumps(relevant)),24000)
        self.assertIn(bc['id'],[e['id'] for e in self.store.relevant(['Conveyor No. 4'])['entities']])
    def test_duplicate_source_and_no_silent_metadata_rewrite(self):
        doc,ev,body=self.sample()
        data=(demo.EXAMPLES/demo.FILES[0]).read_bytes()
        result=ingest(self.store,'renamed.txt',data,'different','new authority')
        self.assertTrue(result['duplicate'])
        self.assertEqual(result['document']['id'],doc['id'])
        self.assertEqual(result['document']['revision'],'0')
        self.assertEqual(len(self.store.rows('SELECT * FROM evidence')),len(ev))
    def test_immutable_records(self):
        self.accepted_sample(0)
        for table in ['documents','evidence','entities','aliases','ontology','assertions','versions']:
            with self.subTest(table=table),self.assertRaises(sqlite3.IntegrityError):
                with self.store.transaction() as db: db.execute('DELETE FROM '+table)
    def test_reject_fabricated_or_foreign_evidence(self):
        d,e,b=self.sample()
        b['operations'][0]['evidence'][0]['quote']='not in the source'
        self.assertTrue(validate(self.store,b,d['id'],0)['errors'])
        b['operations'][0]['evidence'][0]={'evidence_id':'ev_fake','quote':'BC-04'}
        self.assertTrue(validate(self.store,b,d['id'],0)['errors'])
        self.assertEqual(self.store.version(),0)
    def test_validation_rejects_malformed_and_bad_reference(self):
        d,e,b=self.sample()
        fixtures=[None,[],{'summary':'x','operations':'not list'},{'summary':'x','operations':[{'op':'sql','query':'DELETE FROM entities'}]}]
        for body in fixtures:
            self.assertTrue(validate(self.store,body,d['id'],0)['errors'])
        b['operations'][-1]['subject']='missing'
        self.assertTrue(validate(self.store,b,d['id'],0)['errors'])
    def test_stale_proposals_and_double_accept(self):
        d,e,b=self.sample()
        p1=self.proposal(b,d['id']); p2=self.proposal(b,d['id'])
        commit(self.store,p1)
        with self.assertRaises(ValueError): commit(self.store,p1)
        with self.assertRaisesRegex(ValueError,'changed'): commit(self.store,p2)
        self.assertEqual(self.store.version(),1)
    def test_atomic_rollback_on_mid_commit_sql_failure(self):
        d,e,b=self.sample(); pid=self.proposal(b,d['id'])
        with self.store.transaction() as db:
            db.execute("CREATE TRIGGER fail_assertion BEFORE INSERT ON assertions BEGIN SELECT RAISE(ABORT,'simulated disk write failure'); END")
        with self.assertRaises(sqlite3.IntegrityError): commit(self.store,pid)
        self.assertEqual(self.store.version(),0)
        self.assertFalse(self.store.rows('SELECT * FROM entities'))
        self.assertEqual(len(self.store.rows('SELECT * FROM ontology')),2)
        self.assertEqual(self.store.rows('SELECT status FROM proposals')[0]['status'],'pending')
        self.assertTrue(self.store.rows('SELECT * FROM evidence'))
    def test_normalized_duplicate_entity_blocked(self):
        self.accepted_sample(0)
        d=ingest(self.store,'note.txt',b'BC4 is equipment.')['document']
        e=self.store.rows('SELECT * FROM evidence WHERE document_id=?',(d['id'],))[0]
        body={'summary':'duplicate','operations':[{'op':'entity','id':'tmp_dup','label':'BC4','confidence':.99,'origin':'explicit','evidence':[{'evidence_id':e['id'],'quote':e['text']}]}]}
        self.assertTrue(any('matches' in s for s in validate(self.store,body,d['id'],1)['errors']))
        self.assertEqual(normalize('BC_04'),normalize('BC-4'))
    def test_hierarchy_and_merge_cycles_blocked(self):
        self.accepted_sample(0);self.accepted_sample(1)
        d,ev,body=self.sample(2)
        ids={e['label']:e['id'] for e in self.store.model()['entities']}
        support=body['operations'][0]
        prov={k:support[k] for k in ['confidence','origin','evidence']}
        cycle={'summary':'bad parent','operations':[dict(op='assert',subject=ids['BC-04'],predicate='part_of',object_entity=ids['M-04'],**prov)]}
        self.assertTrue(any('cycle' in s for s in validate(self.store,cycle,d['id'],2)['errors']))
        cycle={'summary':'bad merge','operations':[dict(op='merge',source=ids['M-04'],target=ids['GB-04'],reason='test',**prov),dict(op='merge',source=ids['GB-04'],target=ids['M-04'],reason='test',**prov)]}
        self.assertTrue(any('cycle' in s for s in validate(self.store,cycle,d['id'],2)['errors']))
    def test_merge_preserves_old_ids_and_historical_graph(self):
        d=ingest(self.store,'aliases.txt',b'MOTOR-A and M-04 are names of the same motor.')['document']
        e=self.store.rows('SELECT * FROM evidence')[0]
        prov={'confidence':.9,'origin':'explicit','evidence':[{'evidence_id':e['id'],'quote':e['text']}]}
        b={'summary':'initial','operations':[dict(op='entity',id='tmp_a',label='MOTOR-A',**prov),dict(op='entity',id='tmp_b',label='M-04',**prov)]}
        commit(self.store,self.proposal(b,d['id']))
        ids={e['label']:e['id'] for e in self.store.model()['entities']}
        b={'summary':'reviewed identity','operations':[dict(op='merge',source=ids['MOTOR-A'],target=ids['M-04'],reason='Explicit alias evidence',**prov)]}
        commit(self.store,self.proposal(b,d['id']))
        self.assertEqual(len(self.store.model()['entities']),2)
        self.assertEqual(len([e for e in self.store.model()['entities'] if e['id']==e['canonical_id']]),1)
        self.assertTrue(all(e['id']==e['canonical_id'] for e in self.store.model(1)['entities']))
    def test_invalid_visual_support_blocked(self):
        d,e,b=self.sample();b['operations'][0]['evidence']=[{'evidence_id':e[0]['id'],'quote':'','region':[0,0,1,1]}]
        self.assertTrue(validate(self.store,b,d['id'],0)['errors'])
    def test_no_text_loss_across_chunks(self):
        text=('a'*100+'\n')*200
        self.assertEqual(''.join(chunks(text)),text)
        self.assertTrue(all(len(s)<=6000 for s in chunks(text)))
    def test_export_contains_evidence_history_and_no_credentials(self):
        self.accepted_sample(0)
        data=self.store.export()
        self.assertEqual(data['model']['version'],1)
        self.assertIn('evidence',data)
        self.assertIn('versions',data)
        self.assertNotIn('api_key',dumps(data))


class ParserTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.store=Store(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def test_pdf_render_and_text_provenance(self):
        try:import fitz
        except ImportError:self.skipTest('Optional PyMuPDF not installed')
        doc=fitz.open();p=doc.new_page();p.insert_text((72,72),'Motor M-04 drives Gearbox GB-04.')
        b=doc.tobytes();doc.close()
        d=ingest(self.store,'drawing.pdf',b)['document'];e=self.store.rows('SELECT * FROM evidence')[0]
        self.assertIn('M-04',e['text']);self.assertTrue((self.store.root/'renders'/e['image']).exists())
        self.assertEqual((self.store.root/'originals'/d['sha256']).read_bytes(),b)
    def test_xlsx_formulas_preserved_not_executed(self):
        try:import openpyxl
        except ImportError:self.skipTest('Optional openpyxl not installed')
        book=openpyxl.Workbook();book.active.append(['equipment','capacity']);book.active.append(['BC4','=400+400'])
        out=io.BytesIO();book.save(out)
        ingest(self.store,'register.xlsx',out.getvalue())
        e=self.store.rows('SELECT * FROM evidence')[0]
        self.assertIn('=400+400',e['text']);self.assertIn('Row 2',e['text'])
    def test_csv_cells_and_rows(self):
        ingest(self.store,'register.csv',b'tag,notes\nBC4,"rated, nominal"\n')
        text=self.store.rows('SELECT * FROM evidence')[0]['text']
        self.assertIn('Row 2',text);self.assertIn('rated, nominal',text)
    def test_unsupported_and_bad_encoding_fail_before_registration(self):
        for name,data in [('note.doc',b'a'),('note.txt',b'\xff\xfe')]:
            with self.assertRaises(ValueError):ingest(self.store,name,data)
        self.assertFalse(self.store.rows('SELECT * FROM documents'))


class ServiceTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.s=Service(self.tmp.name)
    def tearDown(self):self.s.jobs.join();self.tmp.cleanup()
    def test_offline_queue_isolated_from_real_plant(self):
        self.s.next_demo();self.s.jobs.join()
        p=self.s.state('demo')['proposals'][0]
        self.assertEqual(p['findings']['errors'],[])
        self.assertEqual(self.s.store('demo').version(),0)
        commit(self.s.store('demo'),p['id'])
        self.assertEqual(self.s.store('plant').version(),0)
        self.assertFalse(self.s.state('plant')['documents'])
    def test_review_edit_audit_and_reject_no_model_change(self):
        self.s.next_demo();self.s.jobs.join();p=self.s.state('demo')['proposals'][0]
        b=copy.deepcopy(p['body']);b['summary']='Human clarification'
        self.s.edit_proposal('demo',p['id'],b)
        self.assertEqual(len(self.s.store('demo').rows('SELECT * FROM proposal_edits')),1)
        self.s.reject('demo',p['id'])
        self.assertEqual(self.s.store('demo').version(),0)
        self.assertTrue(self.s.store('demo').rows('SELECT * FROM evidence'))
    def test_session_key_not_written(self):
        self.s.save_settings({'provider':'openai','base_url':'','model':'test','vision':False,'api_key':'TEST_SECRET_DO_NOT_SAVE'})
        self.assertNotIn('TEST_SECRET',self.s.config_path.read_text())
        self.assertNotIn('TEST_SECRET',dumps(self.s.settings()))
        self.assertTrue(self.s.settings()['has_key'])
    def test_interrupted_run_detected_on_restart(self):
        store=self.s.store('plant');d=ingest(store,'note.txt',b'BC-04 exists.')['document']
        with store.transaction() as db:
            db.execute('INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?)',('run_test',d['id'],'running',0,'test',now(),'working',None,'{}'))
        s2=Service(self.tmp.name)
        self.assertEqual(s2.store('plant').rows('SELECT status FROM runs')[0]['status'],'interrupted')
    def test_failed_api_does_not_commit_or_create_partial_proposal(self):
        store=self.s.store('plant');d=ingest(store,'note.txt',b'BC-04 exists.')['document']
        class Broken:
            def ask(self,*a,**kw):raise ValueError('simulated provider failure')
        with patch('chp.service.APIProvider',return_value=Broken()):self.s.start('plant',d['id'])
        self.s.jobs.join()
        self.assertEqual(store.rows('SELECT status FROM runs')[0]['status'],'failed')
        self.assertEqual(store.version(),0);self.assertFalse(store.rows('SELECT * FROM proposals'))
        self.assertTrue(store.rows('SELECT * FROM evidence'))

if __name__=='__main__':unittest.main()
