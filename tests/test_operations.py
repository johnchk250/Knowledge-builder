import copy
import json
import tempfile
import unittest
from unittest.mock import patch
from chp.store import Store, dumps, conflicts
from chp import demo, understanding, operating_model as ops, usage_intake
from chp.ingest import ingest
from chp.patches import validate, commit
from chp.reviewed_ingestion import stage
from chp.service import Service
from chp.existing_migration import legacy_context, plan as migration_plan


class OperationsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(self.tmp.name)
        understanding.initialize(self.store)
        self.doc = ingest(self.store, 'register.txt', b'BC-04 feeds CH-04. CH-04 feeds BC-05. Motor capacity 800 t/h. Operator reviewed correction.')['document']
        self.ev = self.store.rows('SELECT * FROM evidence')[0]
        self.prov = {'origin':'explicit','confidence':1,'evidence':[{'evidence_id':self.ev['id'],'quote':self.ev['text']}]}
        self.accept([
            {'op':'entity','id':'tmp_a','label':'BC-04'}, {'op':'entity','id':'tmp_b','label':'CH-04'}, {'op':'entity','id':'tmp_c','label':'BC-05'},
            {'op':'define','key':'feeds','kind':'relation','definition':'Subject feeds object','cardinality':'many','value_type':'entity'},
            {'op':'define','key':'capacity','kind':'property','definition':'Rated mass flow','cardinality':'one','value_type':'number'}])
        self.ids = {e['label']:e['id'] for e in self.store.model()['entities']}

    def tearDown(self): self.tmp.cleanup()

    def accept(self, operations):
        envelope = {'summary':'Reviewed source', 'operations':[{**o,**self.prov} for o in operations],
            'intake_assessment':{'route':'mixed','purpose':'Equipment evidence','questions':['What connects to this equipment?'],'gaps':[], 'reviewed_evidence_ids':[self.ev['id']]}}
        staged = stage(self.store, self.doc['id'], envelope)
        return commit(self.store, staged['proposal_id'])

    def edge(self, source, target, **context):
        return {'op':'assert','subject':self.ids[source],'predicate':'feeds','object_entity':self.ids[target], 'context':{'kind':'connection','network':'material','verification':'documented',**context}}

    def test_units_conditions_and_exclusive_validity(self):
        a = {'id':'a','subject':'x','predicate':'capacity','value':800,'unit':'t/h','context':{'kind':'specification'},'retirement':None}
        b = {**a,'id':'b','value':800000,'unit':'kg/h'}
        ontology = [{'key':'capacity','cardinality':'one'}]
        self.assertEqual(conflicts([a,b],ontology),[])
        b['value'] = 900000
        self.assertEqual(len(conflicts([a,b],ontology)),1)
        b['context'] = {'kind':'specification','condition':'test'}
        self.assertEqual(conflicts([a,b],ontology),[])
        a['context'] = {'kind':'specification','valid_to':'2026-01-01T00:00:00+00:00'}
        b['context'] = {'kind':'specification','valid_from':'2026-01-01T00:00:00+00:00'}
        self.assertEqual(conflicts([a,b],ontology),[])
        self.assertIsNone(ops.quantity(10, 'unknown'))
        self.assertEqual(ops.quantity(45, 'mwc'), {'dimension':'hydraulic_head','unit':'mH2O','value':45.0})

    def test_network_direction_condition_cycle_and_evidence(self):
        self.accept([self.edge('BC-04','CH-04'), self.edge('CH-04','BC-05',condition='gate A'), self.edge('BC-05','BC-04')])
        r = ops.trace(self.store, self.ids['BC-04'], direction='downstream')
        self.assertEqual([x['label'] for x in r['paths']], ['CH-04'])
        self.assertEqual(len(r['excluded']),1)
        r = ops.trace(self.store, self.ids['BC-04'], direction='downstream',condition='gate A')
        self.assertEqual(len(r['paths']),2)
        self.assertEqual(len(r['edges']),3)
        self.assertFalse(r['complete'])
        self.assertEqual(r['paths'][0]['steps'][0]['evidence'],self.prov['evidence'])
        self.assertEqual(ops.trace(self.store,self.ids['BC-04'],network='electrical')['paths'],[])

    def test_alias_retraction_invalidation_and_historical_restore(self):
        entity = self.ids['BC-04']
        self.accept([self.edge('BC-04','CH-04'), {'op':'alias','entity':entity,'alias':'WRONG-99'}])
        before = self.store.version()
        alias = next(a for a in self.store.model()['aliases'] if a['alias']=='WRONG-99')
        self.accept([{'op':'retract_alias','alias_id':alias['id'],'reason':'Wrong tag'}])
        self.assertEqual(self.store.relevant(['WRONG-99'])['entities'],[])
        self.assertIn('WRONG-99',next(e for e in self.store.model(before)['entities'] if e['id']==entity)['aliases'])
        self.accept([{'op':'invalidate_entity','entity':entity,'reason':'False extraction'}])
        self.assertEqual(self.store.relevant(['BC-04'])['entities'],[])
        self.assertEqual(ops.trace(self.store,self.ids['CH-04'])['paths'],[])
        self.accept([{'op':'restore_entity','entity':entity,'reason':'Correction reversed after source review'}])
        self.assertEqual(len(ops.trace(self.store,self.ids['CH-04'])['paths']),1)

    def test_unmerge_restores_original_fact_ownership_and_can_remerge(self):
        a,b=self.ids['BC-04'],self.ids['CH-04']
        self.accept([{'op':'merge','source':a,'target':b,'reason':'Reviewed identity match'}])
        self.assertEqual(next(e for e in self.store.model()['entities'] if e['id']==a)['canonical_id'],b)
        self.accept([{'op':'unmerge','entity':a,'reason':'Different equipment'}])
        self.assertEqual(next(e for e in self.store.model()['entities'] if e['id']==a)['canonical_id'],a)
        self.accept([{'op':'merge','source':a,'target':b,'reason':'Reviewed identity match'}])

    def test_qualification_preserves_raw_fact_and_prior_context(self):
        self.accept([self.edge('BC-04','CH-04',verification='unverified')])
        raw=self.store.rows('SELECT * FROM assertions')
        fact=self.store.model()['assertions'][0]
        old_version=self.store.version()
        self.accept([{'op':'qualify','assertion_id':fact['id'],'context':{'kind':'connection','network':'material','verification':'documented'},'reason':'Checked direction'}])
        self.assertEqual(self.store.rows('SELECT * FROM assertions'),raw)
        self.assertEqual(self.store.model(old_version)['assertions'][0]['context']['verification'],'unverified')
        self.assertEqual(len(ops.trace(self.store,self.ids['CH-04'])['paths']),1)

    def test_event_history_and_followup_do_not_replace_specification(self):
        a=self.ids['BC-04']
        self.accept([{'op':'event','equipment':a,'event_type':'breakdown','occurred_at':'2026-09-14T08:00:00+06:00','summary':'Noise at drive','status':'open'}])
        event=ops.events(self.store)[0]
        before=self.store.version()
        self.accept([{'op':'event','equipment':a,'event_type':'outcome','occurred_at':'2026-09-14T09:00:00+06:00','summary':'Inspection completed','status':'closed','related_event':event['id']}])
        self.assertEqual(next(e for e in ops.events(self.store) if e['id']==event['id'])['current_status'],'closed')
        self.assertEqual(ops.events(self.store,version=before)[0]['current_status'],'open')
        self.assertEqual(self.store.rows('SELECT * FROM assertions'),[])
        bad={'op':'event','equipment':a,'event_type':'reading','occurred_at':'2026-09-14T08:00:00','summary':'Missing timezone',**self.prov}
        self.assertTrue(validate(self.store,{'summary':'bad','operations':[bad]},self.doc['id'],self.store.version())['errors'])

    def test_missing_intake_and_context_cannot_be_committed(self):
        with self.assertRaisesRegex(ValueError,'Every new intake'):
            stage(self.store,self.doc['id'],{'summary':'bad','operations':[]})
        with self.assertRaisesRegex(ValueError,'context'):
            self.accept([{'op':'assert','subject':self.ids['BC-04'],'predicate':'capacity','value':800,'unit':'t/h'}])

    def test_legacy_migration_is_conservative_and_future_intake_stays_strict(self):
        self.accept([self.edge('BC-04','CH-04')])
        model=self.store.model()
        edge=next(a for a in model['assertions'] if a['predicate']=='feeds')
        # Unknown entity-valued relations are not guessed into a network by the legacy planner.
        edge['context']={}
        self.assertIsNone(legacy_context(edge,{e['id']:e for e in model['entities']}))
        # Scalar equipment properties are safe to retain as specifications.
        scalar={'context':{},'predicate':'capacity','canonical_object':None,'canonical_subject':self.ids['BC-04']}
        self.assertEqual(legacy_context(scalar,{e['id']:e for e in model['entities']}),{'kind':'specification'})
        # Current accepted data in this fixture is already qualified, so the plan does not rewrite it.
        self.assertEqual(migration_plan(self.store)['operations'],[])

    def test_classified_inverse_relation_is_not_left_in_network_review(self):
        self.accept([{'op':'define','key':'conveys_from','kind':'relation','definition':'Subject conveys material from object','cardinality':'many','value_type':'entity'}])
        a,b=self.ids['BC-04'],self.ids['CH-04']
        self.accept([{'op':'assert','subject':a,'predicate':'conveys_from','object_entity':b,'context':{'kind':'classification'}}])
        self.assertEqual(ops.migration_report(self.store)['network_review'],[])

    def test_search_returns_exact_source_and_revision(self):
        result=usage_intake.search_sources(self.store,'BC-04 feeds')
        self.assertEqual(result['results'][0]['document_id'],self.doc['id'])
        self.assertIn('BC-04 feeds',result['results'][0]['snippet'])

    def test_retract_primary_label_and_reassign_alias_in_one_review(self):
        a,b=self.ids['BC-04'],self.ids['CH-04']
        alias=next(x for x in self.store.model()['aliases'] if x['alias']=='BC-04')
        self.accept([{'op':'retract_alias','alias_id':alias['id'],'reason':'Incorrect primary tag'},
            {'op':'alias','entity':a,'alias':'BC-NEW'}, {'op':'alias','entity':b,'alias':'BC-04'}])
        model=self.store.model()
        self.assertEqual(next(e for e in model['entities'] if e['id']==a)['label'],'BC-NEW')
        self.assertEqual(next(e for e in model['entities'] if e['id']==a)['original_label'],'BC-04')
        with self.assertRaisesRegex(ValueError,'collid'):
            self.accept([{'op':'restore_alias','alias_id':alias['id'],'reason':'Would collide'}])

    def test_document_links_and_inferred_connections_not_promoted_to_network(self):
        self.accept([{'op':'define','key':'depicted_in','kind':'relation','definition':'Document reference','cardinality':'many','value_type':'entity'}])
        with self.assertRaisesRegex(ValueError,'Document references'):
            self.accept([{**self.edge('BC-04','CH-04'),'predicate':'depicted_in'}])
        self.accept([{'op':'define','key':'conveys_from','kind':'relation','definition':'Subject conveys material from object','cardinality':'many','value_type':'entity'}])
        with self.assertRaisesRegex(ValueError,'inverse-origin'):
            self.accept([{**self.edge('BC-04','CH-04'),'predicate':'conveys_from'}])
        op={**self.edge('BC-04','CH-04'),**self.prov,'origin':'inferred'}
        self.assertTrue(validate(self.store,{'summary':'bad','operations':[op]},self.doc['id'],self.store.version())['errors'])

    def test_readings_export_and_retrieval_include_operational_context(self):
        self.accept([{'op':'event','equipment':self.ids['BC-04'],'event_type':'reading','occurred_at':'2026-09-14T08:00:00+06:00','summary':'Temperature','measurements':[{'quantity':'bearing temperature','value':40,'unit':'degC','condition':'unloaded','instrument':'T-1'}]}])
        event=ops.events(self.store)[0]
        self.assertEqual(event['measurements'][0]['normalized_quantity']['value'],313.15)
        self.assertEqual(len(self.store.export()['event_measurements']),1)
        self.assertEqual(self.store.relevant(['BC-04'])['operating_history'][0]['id'],event['id'])
        with self.assertRaisesRegex(ValueError,'finite'):
            self.accept([{'op':'event','equipment':self.ids['BC-04'],'event_type':'reading','occurred_at':'2026-09-14T08:00:00Z','summary':'bad','measurements':[{'quantity':'temperature','unit':'degC','value':True}]}])

    def test_reference_index_and_proposal_edit_cannot_add_plant_facts(self):
        envelope={'summary':'Source index','operations':[{'op':'source_note','text':'Searchable drive arrangement',**self.prov}],
            'intake_assessment':{'route':'reference','purpose':'Locate source','questions':['Where is the drive arrangement?'],'gaps':[],'reviewed_evidence_ids':[self.ev['id']]}}
        staged=stage(self.store,self.doc['id'],envelope)
        commit(self.store,staged['proposal_id'])
        self.assertEqual(usage_intake.search_sources(self.store,'drive arrangement')['results'][0]['support'],self.prov['evidence'][0])
        staged=stage(self.store,self.doc['id'],envelope)
        with self.store.transaction() as db:
            changed={'summary':'Bad edit','operations':[{'op':'entity','id':'tmp_wrong','label':'WRONG',**self.prov}]}
            db.execute('UPDATE proposals SET body=? WHERE id=?',(dumps(changed),staged['proposal_id']))
        before=self.store.version()
        with self.assertRaisesRegex(ValueError,'Reference intake'): commit(self.store,staged['proposal_id'])
        self.assertEqual(self.store.version(),before)

    def test_table_intake_preserves_row_and_header_candidates(self):
        doc=ingest(self.store,'ratings.csv',b'tag,capacity,unit\nBC-04,800,t/h\n')['document']
        e=self.store.rows('SELECT * FROM evidence WHERE document_id=?',(doc['id'],))[0]
        metadata=json.loads(e['metadata'])
        self.assertEqual(metadata['table_header_candidate'],['tag','capacity','unit'])
        self.assertEqual(metadata['table_rows'][1],{'row':2,'cells':['BC-04','800','t/h']})

    def test_expected_version_and_policy_are_checked_at_commit(self):
        envelope={'summary':'Reference','operations':[], 'intake_assessment':{'route':'reference','purpose':'Source lookup','questions':[],'gaps':[],'reviewed_evidence_ids':[self.ev['id']]}}
        with self.assertRaisesRegex(ValueError,'changed'):
            stage(self.store,self.doc['id'],envelope,expected_version=0)
        staged=stage(self.store,self.doc['id'],envelope)
        with self.store.transaction() as db:
            row=self.store.rows('SELECT manifest FROM runs WHERE id=?',(staged['run_id'],),db)[0]
            manifest=json.loads(row['manifest']);manifest.pop('intake_policy')
            db.execute('UPDATE runs SET manifest=? WHERE id=?',(dumps(manifest),staged['run_id']))
        with self.assertRaisesRegex(ValueError,'predates'):commit(self.store,staged['proposal_id'])

    def test_app_ingestion_contract_and_operator_record(self):
        with tempfile.TemporaryDirectory() as root:
            service=Service(root)
            store=service.store('plant')
            doc=ingest(store,'reference.txt',b'BC-04 drawing index')['document']
            class Provider:
                def ask(inner,system,payload,images):
                    if 'CURRENT_PLANT_CONTEXT' not in payload: return {'mentions':['BC-04'],'concepts':[]}
                    self.assertIn('USAGE-FOCUSED INTAKE',system)
                    self.assertNotIn('reconstruction_intake.GUIDE',system)
                    return {'summary':'Index only','operations':[{'op':'entity','id':'tmp_bc','label':'BC-04','origin':'explicit','confidence':1,'evidence':[{'evidence_id':payload['evidence']['id'],'quote':'BC-04'}]}],
                        'intake_assessment':{'route':'register','purpose':'Equipment index','questions':['Which tag?'],'gaps':[],'reviewed_evidence_ids':[payload['evidence']['id']]}}
            service.config.update({'provider':'openai','model':'fixture','vision':False})
            with patch('chp.service.APIProvider',return_value=Provider()):
                service.start('plant',doc['id']);service.jobs.join()
            proposal=store.rows('SELECT * FROM proposals')[0]
            commit(store,proposal['id'])
            entity=store.model()['entities'][0]['id']
            service.record_operation('plant',{'expected_version':1,'author':'Shift engineer','reason':'Reported noise', 'event':{'op':'event','equipment':entity,'event_type':'observation','occurred_at':'2026-09-14T06:00:00Z','summary':'Drive noise'}})
            self.assertEqual(len(ops.events(store)),1)
            self.assertEqual(len(store.export()['operational_events']),1)


if __name__=='__main__': unittest.main()
