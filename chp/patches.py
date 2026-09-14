"""Untrusted AI output enters only through this validator and transaction boundary."""
import hashlib
import json
import math
import re
from .store import dumps, uid, now, normalize, conflicts
from . import operating_model as operating


PATCH_GUIDE = '''Return one JSON object {"summary":"...", "operations":[...]}.
Base operations (operational extensions are specified below):
define: {op:"define", key:"snake_case", kind:"entity_type"|"property"|"relation", definition:"...", cardinality:"one"|"many", value_type:"string"|"number"|"boolean"|"entity", ...provenance}
entity: {op:"entity", id:"tmp_UNIQUE", label:"BC-04", ...provenance}
alias: {op:"alias", entity:"existing_id_or_tmp", alias:"BC4", ...provenance}
assert: {op:"assert", subject:"existing_id_or_tmp", predicate:"ontology_key", value: JSON scalar OR object_entity:"entity_id", unit:optional string, ...provenance}
retire: {op:"retire", assertion_id:"existing_fact_id", reason:"...", ...provenance}
merge: {op:"merge", source:"existing_entity_id", target:"existing_entity_id", reason:"...", ...provenance}
Every operation needs provenance fields: confidence:0..1, origin:"explicit"|"inferred", evidence:[{evidence_id:"provided_id", quote:"EXACT substring of provided extracted text", region:optional [x0,y0,x1,y1]}].
For visual evidence quote may be empty, but region must bound the supporting area using normalized 0..1 coordinates. Only use visual support if you actually received that evidence's page image. Inferred operations still need supporting evidence. Do not invent quotes, evidence IDs or entity IDs.
Use instance_of assertions with value naming an entity_type. Define new types/properties/relations as needed before use; do not redefine existing ontology keys. Use part_of for hierarchy. Define relation value_type as entity; entity_type value_type as string and cardinality many. Properties hold scalar values. Units belong in unit, not number strings. Use context.condition for source-stated operating conditions. Cardinality one means different simultaneous values are a conflict, not permission to overwrite.
Existing entities must be referenced by their existing ID. Search results are candidates, not proof of identity. Avoid blind merges. A temporary ID may reference an entity in STAGED_OPERATIONS. Emit only NEW operations, never repeat staged ones. Every new temporary ID must start with the supplied tmp prefix. Alias names can be descriptive; preserve tag spelling in the label. Labels are identifiers, never physical specifications.
Retire assertions only with strong evidence that the prior interpretation is wrong or explicitly replaced. Disagreeing document values normally coexist as conflicts. Reclassification can retire an earlier general instance_of with a reason. Use assertions for specifications and relationships; use event operations for dated operational records.
Model revisions are not chronological unless source metadata establishes chronology. Document authority is contextual guidance, not automatic truth. Do not make up plant facts. Empty operations is valid when nothing is supported.
'''

FIELDS = {
    'define': {'op','key','kind','definition','cardinality','value_type'},
    'entity': {'op','id','label'},
    'alias': {'op','entity','alias'},
    'assert': {'op','subject','predicate','value','object_entity','unit','context'},
    'retire': {'op','assertion_id','reason'},
    'merge': {'op','source','target','reason'},
}
FIELDS.update(operating.EXTRA_FIELDS)
PROV = {'confidence','origin','evidence'}


def provenance(op):
    return {k:op[k] for k in PROV}


def visual_evidence_for_run(store, run_id, db=None):
    if not store.rows("SELECT name FROM sqlite_master WHERE type='table' AND name='run_steps'",db=db): return set()
    steps=store.rows("SELECT request FROM run_steps WHERE run_id=? AND stage='propose'",(run_id,),db)
    return {im['evidence_id'] for step in steps for im in json.loads(step['request']).get('images',[])}


def validate(store, body, document_id, base_version, db=None, visual_ids=()):
    errors, warnings = [], []
    def err(msg): errors.append(msg)
    if base_version != store.version(db):
        err('The plant model changed after this proposal was generated. Re-analyze against the current model.')
    if not isinstance(body, dict) or set(body) != {'summary','operations'} or not isinstance(body.get('summary'),str) or not isinstance(body.get('operations'),list):
        return {'errors': errors + ['Expected summary and operations only.'], 'warnings':[]}
    ops = body['operations']
    if len(ops) > 500 or len(dumps(body)) > 500000:
        return {'errors':errors+['Proposal exceeds the 500-operation / 500 KB limit. Split the document.'], 'warnings':[]}
    model = store.model(db=db)
    entities = {e['id']:e for e in model['entities']}
    ont = {o['key']:o for o in model['ontology']}
    assertions = {a['id']:a for a in model['assertions']}
    evidence = {e['id']:e for e in store.rows('SELECT * FROM evidence WHERE document_id=?',(document_id,),db)}
    retracting = {o.get('alias_id') for o in ops if isinstance(o,dict) and o.get('op')=='retract_alias'}
    invalidating = {o.get('entity') for o in ops if isinstance(o,dict) and o.get('op')=='invalidate_entity'}
    known_names = {a['normalized']:entities[a['entity_id']]['canonical_id'] for a in model['aliases'] if not a.get('retracted') and a['id'] not in retracting and not entities[a['entity_id']].get('inactive') and entities[a['entity_id']]['canonical_id'] not in invalidating}
    good = []
    for i, op in enumerate(ops):
        prefix = f'Operation {i+1}: '
        before = len(errors)
        if not isinstance(op,dict) or not isinstance(op.get('op'),str) or op['op'] not in FIELDS:
            err(prefix+'unknown operation'); continue
        name = op['op']
        if set(op) - (FIELDS[name] | PROV): err(prefix+'unexpected fields')
        required = (FIELDS[name] - operating.OPTIONAL) | PROV
        if not required <= set(op): err(prefix+'missing required fields'); continue
        for key in FIELDS[name] - operating.OPTIONAL:
            if not isinstance(op.get(key),str) or not op[key].strip() or len(op[key]) > 2000:
                err(prefix+f'{key} must be a nonempty string, at most 2000 characters')
        if not isinstance(op['confidence'],(float,int)) or isinstance(op['confidence'],bool) or not math.isfinite(op['confidence']) or not 0 <= op['confidence'] <= 1:
            err(prefix+'confidence must be between zero and one')
        if op['origin'] not in ('explicit','inferred'): err(prefix+'invalid origin')
        supports = op['evidence']
        if not isinstance(supports,list) or not supports or len(supports)>30:
            err(prefix+'1–30 evidence references required'); continue
        for s in supports:
            if not isinstance(s,dict) or set(s)-{'evidence_id','quote','region'} or not isinstance(s.get('evidence_id'),str) or not isinstance(s.get('quote',''),str):
                err(prefix+'invalid evidence reference'); continue
            ev = evidence.get(s['evidence_id'])
            if not ev: err(prefix+'evidence must belong to this source document'); continue
            quote = s.get('quote','')
            if quote and quote not in ev['text']: err(prefix+'quote does not exactly match the immutable extracted text')
            region = s.get('region')
            if region is not None:
                if s['evidence_id'] not in visual_ids: err(prefix+'visual evidence was not transmitted in this analysis run')
                if not ev['image'] or not isinstance(region,list) or len(region)!=4 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for v in region):
                    err(prefix+'invalid visual region')
                elif region[0]>=region[2] or region[1]>=region[3]: err(prefix+'visual region is empty or reversed')
            if not quote and region is None: err(prefix+'an exact supporting quote or rendered-page region is required')
        if len(errors)>before: continue
        if op['origin']=='inferred' or op['confidence']<0.85:
            warnings.append(prefix+'inferred or low-confidence change; inspect the supporting source')
        if name=='define':
            if not re.fullmatch('[a-z][a-z0-9_]{0,79}',op['key']): err(prefix+'invalid ontology key')
            if op['kind'] not in ('entity_type','property','relation') or op['cardinality'] not in ('one','many') or op['value_type'] not in ('string','number','boolean','entity'):
                err(prefix+'invalid ontology definition')
            elif (op['kind']=='relation') != (op['value_type']=='entity'):
                err(prefix+'only relationships have entity values')
            if op['key'] in ont: err(prefix+'ontology key already exists; reuse it or propose a distinctly named concept')
            else: ont[op['key']] = op
            warnings.append(prefix+'new ontology concept')
        elif name=='entity':
            if not re.fullmatch('tmp_[A-Za-z0-9_]{1,80}',op['id']) or op['id'] in entities: err(prefix+'new entity needs a unique temporary ID')
            if normalize(op['label']) in known_names: err(prefix+'label matches an existing entity or alias; reference that entity instead')
            else: known_names[normalize(op['label'])] = op['id']
            entities[op['id']] = {'id':op['id'],'label':op['label'],'canonical_id':op['id']}
        good.append((i,op))
    # Validate all references after collecting declarations; SQL commit orders dependencies explicitly.
    retire = set()
    redirects = {m['source']:m['target'] for m in model['merges']}
    new_facts = []
    alias_seen = set()
    correction_seen = set()
    for i, op in good:
        prefix=f'Operation {i+1}: '
        name=op['op']
        def check_entity(eid):
            if not isinstance(eid,str) or eid not in entities:
                err(prefix+'unknown entity reference'); return False
            if entities[eid].get('inactive') or eid in invalidating:
                err(prefix+'entity is invalidated; restore it through correction review first'); return False
            if entities[eid]['canonical_id'] != eid:
                err(prefix+'reference the current canonical entity, not a merged ID'); return False
            return True
        if name in operating.EXTRA_FIELDS:
            try:
                operating.validate_extra(op, store, model, entities, assertions, db)
                if name not in ('event', 'source_note'):
                    target = op.get('entity', op.get('alias_id', op.get('assertion_id')))
                    if target in correction_seen: raise ValueError('Only one correction per target in a proposal')
                    correction_seen.add(target)
                if name == 'qualify': assertions[op['assertion_id']]['context'] = op['context']
                warnings.append(prefix+'review operational record or correction and its effect on the current model')
                if name in ('invalidate_entity','restore_entity','unmerge'):
                    affected=[a for a in model['assertions'] if op['entity'] in (a['subject'],a['object_entity'],a['canonical_subject'],a['canonical_object'])]
                    warnings.append(prefix+f"{entities[op['entity']]['label']}: {len(affected)} historical facts reference this identity; inspect their ownership and visibility")
            except ValueError as exc: err(prefix+str(exc))
        elif name=='alias':
            if check_entity(op['entity']):
                match=known_names.get(normalize(op['alias']))
                if match and match != op['entity']: err(prefix+'alias collides with another entity; requires explicit identity review')
                if (op['entity'],op['alias']) in alias_seen: err(prefix+'duplicate alias operation')
                alias_seen.add((op['entity'],op['alias']))
                known_names[normalize(op['alias'])]=op['entity']
        elif name=='assert':
            check_entity(op['subject'])
            p=ont.get(op['predicate'])
            if not p or p['kind']=='entity_type': err(prefix+'predicate must be a defined property or relationship'); continue
            if ('value' in op)==('object_entity' in op): err(prefix+'provide exactly one value or object_entity'); continue
            if p['kind']=='relation':
                if 'object_entity' not in op or not check_entity(op.get('object_entity')): err(prefix+'relation requires a valid object entity')
                if op.get('unit') is not None: err(prefix+'relationships cannot have units')
            else:
                value=op.get('value')
                matches={'string':isinstance(value,str), 'number':isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value), 'boolean':isinstance(value,bool)}
                if not matches.get(p['value_type'],False): err(prefix+'value does not match the declared property type')
                if op.get('unit') is not None and (not isinstance(op['unit'],str) or len(op['unit'])>60 or p['value_type']!='number'): err(prefix+'units are short strings on numeric properties only')
            if op['predicate']=='instance_of' and (not isinstance(op.get('value'),str) or ont.get(op.get('value'),{}).get('kind')!='entity_type'):
                err(prefix+'classification must name a defined entity_type')
            try:
                operating.validate_context(op.get('context', {}), p['kind']=='relation')
                if op.get('context', {}).get('verification') == 'documented' and op['origin'] != 'explicit': raise ValueError('Inferred connections cannot be marked documented')
            except ValueError as exc: err(prefix+str(exc))
            new_facts.append({'id':f'proposed_{i+1}','subject':op['subject'],'predicate':op['predicate'],'value':op.get('value'),'object_entity':op.get('object_entity'),'unit':op.get('unit'),'context':op.get('context',{}),'retirement':None})
        elif name=='retire':
            a=assertions.get(op['assertion_id'])
            if not a or a['retirement'] or op['assertion_id'] in retire: err(prefix+'assertion is unknown, already retired, or repeated')
            retire.add(op['assertion_id'])
            warnings.append(prefix+'changes the current interpretation; historical assertion will be retained')
        elif name=='merge':
            if check_entity(op['source']) and check_entity(op['target']):
                if op['source']==op['target'] or op['source'] in redirects: err(prefix+'invalid or repeated merge')
                redirects[op['source']]=op['target']
            warnings.append(prefix+'entity merge redirects current facts and aliases; verify identity carefully')
    # Identity reversal/restoration is deliberately isolated from other identity edits.
    # Validate the resulting alias ownership and hierarchy before exposing the old identity.
    for _, op in good:
        if op['op'] == 'unmerge': redirects.pop(op['entity'], None)
    def resolve(eid):
        seen=set()
        while eid in redirects:
            if eid in seen: raise ValueError('Merge operations create a cycle')
            seen.add(eid); eid=redirects[eid]
        return eid
    if errors:
        return {'errors':list(dict.fromkeys(errors)), 'warnings':list(dict.fromkeys(warnings))}
    try:
        for eid in redirects: resolve(eid)
        _, inactive, retracted = operating.identity_state(store, model['version'], db)
        for _,o in good:
            if o['op']=='invalidate_entity': inactive.add(o['entity'])
            elif o['op']=='restore_entity': inactive.discard(o['entity'])
            elif o['op']=='retract_alias': retracted.add(o['alias_id'])
            elif o['op']=='restore_alias': retracted.discard(o['alias_id'])
        ownership={}
        aliases=list(model['aliases']) + [{'id':'new_'+str(i),'entity_id':o['id'] if o['op']=='entity' else o['entity'],'normalized':normalize(o['label'] if o['op']=='entity' else o['alias'])} for i,o in good if o['op'] in ('entity','alias')]
        for a in aliases:
            if a['id'] in retracted or resolve(a['entity_id']) in inactive: continue
            target=resolve(a['entity_id'])
            if a['normalized'] in ownership and ownership[a['normalized']]!=target: raise ValueError('Correction creates an alias collision; retract the incorrect alias first')
            ownership[a['normalized']]=target
        retired_ids={r['assertion_id'] for r in store.rows('SELECT assertion_id FROM retirements',db=db)} | retire
        live=[dict(a) for a in model['assertions'] if a['id'] not in retired_ids]+new_facts
        live=[a for a in live if resolve(a['subject']) not in inactive and (not a.get('object_entity') or resolve(a['object_entity']) not in inactive)]
        for a in live:
            a['retirement']=None
            a['canonical_subject']=resolve(a['subject'])
            a['canonical_object']=resolve(a['object_entity']) if a.get('object_entity') else None
        document_entities={a['canonical_subject'] for a in live if a['predicate']=='instance_of' and a['value'] in operating.DOCUMENT_TYPES}
        for a in live:
            if a.get('context',{}).get('network') and (a['predicate'] in operating.NON_NETWORK_RELATIONS or a['canonical_subject'] in document_entities or a['canonical_object'] in document_entities):
                raise ValueError('Document references, inverse-origin relations, location and hierarchy links cannot be operational network edges')
        graph={}
        for a in live:
            if a['predicate']=='part_of': graph.setdefault(a['canonical_subject'],set()).add(a['canonical_object'])
        def visit(node, path):
            if node in path: raise ValueError('The proposed part_of hierarchy contains a cycle')
            for parent in graph.get(node,()): visit(parent,path|{node})
        for node in graph: visit(node,set())
        for c in conflicts(live,list(ont.values())):
            warnings.append(f"Conflict retained: {entities[c['subject']]['label']} / {c['predicate']} has different active values")
    except (ValueError,RecursionError) as exc:
        err(str(exc) if isinstance(exc,ValueError) else 'Hierarchy too deep to validate safely')
    return {'errors':list(dict.fromkeys(errors)), 'warnings':list(dict.fromkeys(warnings))}


def commit(store, proposal_id):
    with store.transaction() as db:
        rows=store.rows('SELECT * FROM proposals WHERE id=?',(proposal_id,),db)
        if not rows: raise ValueError('Proposal not found')
        p=rows[0]
        from .understanding import check_run
        check_run(store,p['run_id'],db)
        if p['status']!='pending': raise ValueError('Proposal is no longer pending')
        body=json.loads(p['body'])
        from .usage_intake import check_policy
        check_policy(store, p['run_id'], body, db)
        findings=validate(store,body,p['document_id'],p['base_version'],db,visual_evidence_for_run(store,p['run_id'],db))
        if findings['errors']: raise ValueError('; '.join(findings['errors']))
        v=store.version(db)+1
        mapping={o['id']:uid('ent') for o in body['operations'] if o['op']=='entity'}
        def eid(x): return mapping.get(x,x)
        for kind in ['define','entity','alias','assert','retire','merge'] + list(operating.EXTRA_FIELDS):
            for o in body['operations']:
                if o['op']!=kind: continue
                prov=dumps(provenance(o))
                if kind=='define': db.execute('INSERT INTO ontology VALUES(?,?,?,?,?,?,?)',(o['key'],o['kind'],o['definition'],o['cardinality'],o['value_type'],v,prov))
                elif kind=='entity':
                    db.execute('INSERT INTO entities VALUES(?,?,?,?)',(eid(o['id']),o['label'],v,prov))
                    db.execute('INSERT INTO aliases VALUES(?,?,?,?,?,?)',(uid('alias'),eid(o['id']),o['label'],normalize(o['label']),v,prov))
                elif kind=='alias': db.execute('INSERT INTO aliases VALUES(?,?,?,?,?,?)',(uid('alias'),eid(o['entity']),o['alias'],normalize(o['alias']),v,prov))
                elif kind=='assert':
                    fact_id = uid('fact')
                    db.execute('INSERT INTO assertions VALUES(?,?,?,?,?,?,?,?,?,?)',(fact_id,eid(o['subject']),o['predicate'],dumps(o['value']) if 'value' in o else None,eid(o['object_entity']) if 'object_entity' in o else None,o.get('unit'),o['confidence'],o['origin'],dumps(o['evidence']),v))
                    if o.get('context'):
                        db.execute('INSERT INTO assertion_contexts VALUES(?,?,?,?,?,?)',(uid('ctx'),fact_id,dumps(o['context']),v,'Source intake context',prov))
                elif kind=='retire': db.execute('INSERT INTO retirements VALUES(?,?,?,?)',(o['assertion_id'],v,o['reason'],prov))
                elif kind=='merge': operating.write_extra(db, {**o,'source':eid(o['source']),'target':eid(o['target'])}, v, eid, prov)
                elif kind in operating.EXTRA_FIELDS: operating.write_extra(db, o, v, eid, prov)
        previous=store.rows('SELECT hash FROM versions ORDER BY version DESC LIMIT 1',db=db)
        previous_hash=previous[0]['hash'] if previous else '0'*64
        committed={'proposal':body,'entity_ids':mapping}
        timestamp=now()
        digest=hashlib.sha256(dumps([v,proposal_id,timestamp,committed,previous_hash]).encode()).hexdigest()
        db.execute('INSERT INTO versions VALUES(?,?,?,?,?,?,?)',(v,proposal_id,timestamp,body['summary'],dumps(committed),previous_hash,digest))
        db.execute("UPDATE meta SET value=? WHERE key='version'",(str(v),))
        db.execute("UPDATE proposals SET status='accepted',decision=? WHERE id=?",(now(),proposal_id))
        return {'version':v,'hash':digest}
