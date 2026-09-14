"""Deterministic fixtures, deliberately restricted to the three bundled examples."""
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parent.parent/'examples'
FILES = ['01_equipment_register.txt','02_drive_arrangement.txt','03_subsystem_correction.txt']


def proposal(store, document, evidence):
    content=(store.root/'originals'/document['sha256']).read_bytes()
    stage=next((i+1 for i,name in enumerate(FILES) if (EXAMPLES/name).read_bytes()==content),None)
    if not stage: raise ValueError('Offline walkthrough supports only the three bundled sample documents. Connect an API for your own documents.')
    model=store.model()
    entities={e['label']:e['id'] for e in model['entities'] if e['canonical_id']==e['id']}
    ont={o['key'] for o in model['ontology']}
    ops=[]
    def support(quote,origin='explicit',confidence=.98):
        ev=next(e for e in evidence if quote in e['text'])
        return {'confidence':confidence,'origin':origin,'evidence':[{'evidence_id':ev['id'],'quote':quote}]}
    def define(key,kind,definition,quote,value_type='string',cardinality='many'):
        if key not in ont:
            ops.append(dict(op='define',key=key,kind=kind,definition=definition,value_type=value_type,cardinality=cardinality,**support(quote,'inferred',.93)))
            ont.add(key)
    def entity(label,quote):
        if label not in entities:
            entities[label]='tmp_'+label.replace('-','_')
            ops.append(dict(op='entity',id=entities[label],label=label,**support(quote)))
        return entities[label]
    def fact(subject,predicate,value,quote,relation=False,unit=None):
        op=dict(op='assert',subject=entities[subject],predicate=predicate,**support(quote))
        op['object_entity' if relation else 'value']=entities[value] if relation else value
        if unit: op['unit']=unit
        ops.append(op)
    if stage==1:
        if 'BC-04' in entities: raise ValueError('The first sample has already been committed. Continue with the next sample.')
        quote='BC-04 is an item of equipment in the coal handling plant.'
        define('equipment','entity_type','A physical plant asset.',quote)
        entity('BC-04',quote)
        fact('BC-04','instance_of','equipment',quote)
        quote='BC-04 rated capacity: 800 t/h.'
        define('rated_capacity','property','Rated material throughput; source disagreements are retained.',quote,'number','one')
        fact('BC-04','rated_capacity',800,quote,unit='t/h')
        summary='Introduce BC-04 with a general equipment classification and 800 t/h rated capacity.'
    elif stage==2:
        if 'BC-04' not in entities: raise ValueError('Accept sample 1 first.')
        if 'M-04' in entities: raise ValueError('Sample 2 has already been committed.')
        quote='BC-04, also called BC4 and Belt Conveyor 04, is a belt conveyor.'
        define('belt_conveyor','entity_type','Belt-based bulk material transport equipment.',quote)
        for a in model['assertions']:
            if a['canonical_subject']==entities['BC-04'] and a['predicate']=='instance_of' and not a['retirement']:
                ops.append(dict(op='retire',assertion_id=a['id'],reason='The later drawing establishes the more specific belt conveyor type.',**support(quote)))
        fact('BC-04','instance_of','belt_conveyor',quote)
        for alias in ['BC4','Belt Conveyor 04']: ops.append(dict(op='alias',entity=entities['BC-04'],alias=alias,**support(quote)))
        for label,typ,quote in [('M-04','motor','Motor M-04 drives Gearbox GB-04.'),('GB-04','gearbox','Motor M-04 drives Gearbox GB-04.'),('ZSS-04','monitoring_device','ZSS-04 monitors BC-04.')]:
            define(typ,'entity_type',typ.replace('_',' ').capitalize()+'.',quote)
            entity(label,quote)
            if label!='ZSS-04': fact(label,'instance_of',typ,quote)
            else:
                fact(label,'instance_of',typ,quote)
                ops[-1]['origin']='inferred'; ops[-1]['confidence']=.82
        define('drives','relation','Mechanical drive transmission from subject to object.','Motor M-04 drives Gearbox GB-04.','entity')
        define('monitors','relation','Subject observes or monitors object.','ZSS-04 monitors BC-04.','entity')
        fact('M-04','drives','GB-04','Motor M-04 drives Gearbox GB-04.',True)
        fact('GB-04','drives','BC-04','GB-04 drives BC-04.',True)
        fact('ZSS-04','monitors','BC-04','ZSS-04 monitors BC-04.',True)
        fact('M-04','part_of','BC-04','M-04 is part of BC-04.',True)
        fact('BC-04','rated_capacity',1000,'BC-04 rated capacity: 1000 t/h.',unit='t/h')
        summary='Recognize BC4 as BC-04, refine its type, add drive and monitoring relationships, and retain the capacity conflict.'
    else:
        if 'M-04' not in entities: raise ValueError('Accept sample 2 first.')
        if 'DS-04' in entities: raise ValueError('The walkthrough is complete.')
        quote='DS-04 is the drive subsystem of BC-04.'
        define('drive_subsystem','entity_type','Subsystem containing drive components.',quote)
        entity('DS-04',quote)
        fact('DS-04','instance_of','drive_subsystem',quote)
        fact('DS-04','part_of','BC-04',quote,True)
        quote='The previous direct parent assignment of M-04 to BC-04 is incomplete; use DS-04 as its immediate parent.'
        for a in model['assertions']:
            if a['canonical_subject']==entities['M-04'] and a['predicate']=='part_of' and not a['retirement']:
                ops.append(dict(op='retire',assertion_id=a['id'],reason='Clarification identifies the immediate parent as DS-04.',**support(quote)))
        for label in ['M-04','GB-04']: fact(label,'part_of','DS-04','M-04 and GB-04 are components of DS-04.',True)
        summary='Introduce drive subsystem DS-04 and revise the component hierarchy without deleting the earlier interpretation.'
    return {'summary':summary,'operations':ops}
