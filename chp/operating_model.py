"""Operational semantics and append-only corrections; no inferred plant state."""
import json
import math
from datetime import datetime, timezone
from decimal import Decimal
import functools
from .store import dumps, uid, now, fast_loads

TABLES = ['assertion_contexts', 'identity_changes', 'operational_events', 'event_measurements', 'source_notes']
NETWORKS = ('material', 'mechanical', 'electrical', 'control', 'utility')
DOCUMENT_TYPES = {'engineering_drawing','email_condition_report','email_technical_inquiry','design_basis_report','technical_manual','standard_operating_procedure','drive_schedule','piping_specification','painting_specification','test_procedure','quality_assurance_plan','technical_comment_review_sheet','document','manual','drawing','report'}
REFERENCE_RELATIONS = {'depicted_in','report_about','references_drawing','located_at','part_of'}
INVERSE_NETWORK_RELATIONS = {'conveys_from'}
NON_NETWORK_RELATIONS = REFERENCE_RELATIONS | INVERSE_NETWORK_RELATIONS
DIMENSIONLESS_PROPERTIES = {'quantity','gear_ratio','duct_elbow_radius_ratio'}
EVENT_TYPES = ('observation', 'reading', 'breakdown', 'inspection', 'repair', 'replacement', 'action', 'outcome', 'lesson', 'correction')
CONTEXT_KEYS = {'kind', 'condition', 'valid_from', 'valid_to', 'observed_at', 'network', 'from_port', 'to_port', 'verification', 'functional_location', 'basis'}
EXTRA_FIELDS = {
    'invalidate_entity': {'op', 'entity', 'reason'},
    'restore_entity': {'op', 'entity', 'reason'},
    'retract_alias': {'op', 'alias_id', 'reason'},
    'restore_alias': {'op', 'alias_id', 'reason'},
    'unmerge': {'op', 'entity', 'reason'},
    'qualify': {'op', 'assertion_id', 'context', 'reason'},
    'event': {'op', 'equipment', 'event_type', 'occurred_at', 'summary', 'details', 'status', 'related_event', 'measurements'},
    'source_note': {'op', 'text'},
}
OPTIONAL = {'unit', 'value', 'object_entity', 'context', 'details', 'status', 'related_event', 'measurements'}


def initialize(db):
    db.executescript('''
    BEGIN IMMEDIATE;
    CREATE TABLE IF NOT EXISTS assertion_contexts(id TEXT PRIMARY KEY, assertion_id TEXT NOT NULL REFERENCES assertions(id), context TEXT NOT NULL, version INTEGER NOT NULL, reason TEXT NOT NULL, provenance TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS identity_changes(id TEXT PRIMARY KEY, kind TEXT NOT NULL, target TEXT NOT NULL, replacement TEXT, version INTEGER NOT NULL, reason TEXT NOT NULL, provenance TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS operational_events(id TEXT PRIMARY KEY, equipment TEXT NOT NULL REFERENCES entities(id), event_type TEXT NOT NULL, occurred_at TEXT NOT NULL, recorded_at TEXT NOT NULL, summary TEXT NOT NULL, details TEXT NOT NULL, status TEXT NOT NULL, related_event TEXT REFERENCES operational_events(id), provenance TEXT NOT NULL, version INTEGER NOT NULL);
    CREATE INDEX IF NOT EXISTS context_assertion ON assertion_contexts(assertion_id,version);
    CREATE INDEX IF NOT EXISTS events_equipment ON operational_events(equipment,occurred_at);
    CREATE TABLE IF NOT EXISTS event_measurements(id TEXT PRIMARY KEY,event_id TEXT NOT NULL REFERENCES operational_events(id),body TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS source_notes(id TEXT PRIMARY KEY,text TEXT NOT NULL,provenance TEXT NOT NULL,version INTEGER NOT NULL);
    ''')
    for table in TABLES:
        for action in ('UPDATE', 'DELETE'):
            db.execute(f"CREATE TRIGGER IF NOT EXISTS immutable_{table}_{action} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'immutable record'); END")
    db.execute("UPDATE meta SET value='4' WHERE key='schema_version'")


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('Time must be an ISO 8601 string with timezone')
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError('Time must be ISO 8601 with timezone')
    if parsed.tzinfo is None:
        raise ValueError('Time must include a timezone, for example +06:00')
    return parsed.astimezone(timezone.utc)


def validate_context(context, relation=False):
    if not isinstance(context, dict) or set(context) - CONTEXT_KEYS:
        raise ValueError('Context must contain supported operational fields only')
    for key, value in context.items():
        if not isinstance(value, str) or not value.strip() or len(value) > 1000:
            raise ValueError('Context values must be nonempty strings up to 1000 characters')
    if context.get('kind', 'specification') not in ('specification', 'observation', 'hypothesis', 'connection', 'classification'):
        raise ValueError('Unknown fact kind')
    if context.get('network') and (context['network'] not in NETWORKS or not relation):
        raise ValueError('Network requires an entity relationship and a supported network')
    if context.get('network') and context.get('kind') != 'connection':
        raise ValueError('Network context requires kind connection')
    if any(k in context for k in ('from_port', 'to_port', 'verification')) and not context.get('network'):
        raise ValueError('Connection ports and verification require a network')
    if context.get('verification', 'unverified') not in ('documented', 'unverified'):
        raise ValueError('Verification must be documented or unverified')
    for key in ('valid_from', 'valid_to', 'observed_at'):
        if key in context:
            timestamp(context[key])
    if 'valid_from' in context and 'valid_to' in context and timestamp(context['valid_from']) >= timestamp(context['valid_to']):
        raise ValueError('Validity end must be after its start (end is exclusive)')
    if context.get('kind') == 'observation' and 'observed_at' not in context:
        raise ValueError('An observation requires observed_at')


# Deliberately bounded and dimensional. Unknown units remain unresolved, never guessed.
UNITS = {}
for dimension, unit, scale, offset, aliases in [
    ('mass_flow', 'kg/h', '1', '0', ['kg/h', 'kg/hr']),
    ('mass_flow', 'kg/h', '1000', '0', ['t/h', 't/hr', 'tph', 'tonne/h']),
    ('power', 'W', '1', '0', ['w']), ('power', 'W', '1000', '0', ['kw']), ('power', 'W', '1000000', '0', ['mw']),
    ('length', 'm', '1', '0', ['m']), ('length', 'm', '.001', '0', ['mm']), ('length', 'm', '.01', '0', ['cm']),
    ('mass', 'kg', '1', '0', ['kg']), ('mass', 'kg', '1000', '0', ['t', 'tonne']),
    ('pressure', 'Pa', '1', '0', ['pa']), ('pressure', 'Pa', '1000', '0', ['kpa']), ('pressure', 'Pa', '100000', '0', ['bar']), ('pressure', 'Pa', '1000000', '0', ['mpa']),
    # Hydraulic head stays a length-of-water-column quantity. Do not silently
    # convert it to pressure, which would require density/gravity assumptions.
    ('hydraulic_head', 'mH2O', '1', '0', ['mwc', 'mh2o', 'm h2o']),
    ('temperature', 'K', '1', '273.15', ['°c', 'degc', 'celsius']), ('temperature', 'K', '1', '0', ['k']),
    ('current', 'A', '1', '0', ['a']), ('voltage', 'V', '1', '0', ['v']), ('voltage', 'V', '1000', '0', ['kv']),
    ('speed', 'm/s', '1', '0', ['m/s']), ('speed', 'm/s', str(1/60), '0', ['m/min']),
    ('rotation', 'rpm', '1', '0', ['rpm']), ('ratio', '%', '1', '0', ['%']),
    ('volume_flow', 'm3/h', '1', '0', ['m3/h','m3/hr','cmh','m³/h']),
    ('time', 's', '1', '0', ['s']), ('time', 's', '60', '0', ['min']), ('time', 's', '3600', '0', ['h']),
]:
    for alias in aliases:
        UNITS[alias] = (dimension, unit, Decimal(scale), Decimal(offset))


@functools.lru_cache(maxsize=65536)
def quantity(value, unit):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    spec = UNITS.get((unit or '').strip().lower())
    if not spec:
        return None
    dimension, canonical_unit, scale, offset = spec
    result = Decimal(str(value)) * scale + offset
    return {'dimension': dimension, 'unit': canonical_unit, 'value': float(result)}


def comparable(a, b):
    ca, cb = a.get('context', {}), b.get('context', {})
    if ca.get('kind', 'legacy') != cb.get('kind', 'legacy') or ca.get('condition', '') != cb.get('condition', '') or ca.get('basis', '') != cb.get('basis', ''):
        return False
    if ca.get('kind') == 'hypothesis':
        return False
    if ca.get('observed_at') != cb.get('observed_at'):
        return False
    for start, end in ((ca.get('valid_from'), cb.get('valid_to')), (cb.get('valid_from'), ca.get('valid_to'))):
        if start and end and timestamp(start) >= timestamp(end):
            return False
    return True


def equivalent(a, b):
    if a.get('canonical_object', a.get('object_entity')) != b.get('canonical_object', b.get('object_entity')):
        return False
    qa, qb = quantity(a.get('value'), a.get('unit')), quantity(b.get('value'), b.get('unit'))
    if qa and qb and qa['dimension'] == qb['dimension']:
        return math.isclose(qa['value'], qb['value'], rel_tol=1e-9, abs_tol=1e-12)
    return a.get('value') == b.get('value') and a.get('unit') == b.get('unit')


def identity_state(store, version, db=None):
    merges = {r['source']: r for r in store.rows('SELECT * FROM merges WHERE version<=? ORDER BY version', (version,), db)}
    inactive, retracted = set(), set()
    changes = store.rows('SELECT * FROM identity_changes WHERE version<=? ORDER BY version,rowid', (version,), db)
    for r in changes:
        kind, target = r['kind'], r['target']
        if kind == 'merge':
            merges[target] = {'source': target, 'target': r['replacement'], 'version': r['version'], 'reason': r['reason'], 'provenance': r['provenance']}
        elif kind == 'unmerge': merges.pop(target, None)
        elif kind == 'invalidate_entity': inactive.add(target)
        elif kind == 'restore_entity': inactive.discard(target)
        elif kind == 'retract_alias': retracted.add(target)
        elif kind == 'restore_alias': retracted.discard(target)
    return list(merges.values()), inactive, retracted


def context_map(store, version, db=None):
    raw = {}
    for row in store.rows('SELECT assertion_id, context, provenance, version, reason FROM assertion_contexts WHERE version<=? ORDER BY version,rowid', (version,), db):
        raw[row['assertion_id']] = row
    return {
        aid: {'context': fast_loads(r['context']), 'provenance': fast_loads(r['provenance']), 'version': r['version'], 'reason': r['reason']}
        for aid, r in raw.items()
    }


def validate_extra(op, store, model, entities, assertions, db=None):
    kind = op['op']
    inactive = {e['id'] for e in model['entities'] if e.get('inactive')}
    aliases = {a['id']: a for a in model['aliases']}
    if kind in ('invalidate_entity', 'restore_entity', 'unmerge'):
        entity = entities.get(op['entity'])
        if not entity: raise ValueError('Unknown entity')
        if kind == 'invalidate_entity' and (op['entity'] in inactive or entity['canonical_id'] != op['entity']): raise ValueError('Only active canonical entities can be invalidated')
        if kind == 'restore_entity' and op['entity'] not in inactive: raise ValueError('Entity is not invalidated')
        if kind == 'unmerge' and not any(m['source'] == op['entity'] for m in model['merges']): raise ValueError('Entity has no active merge to reverse')
    elif kind in ('retract_alias', 'restore_alias'):
        alias = aliases.get(op['alias_id'])
        if not alias: raise ValueError('Unknown alias')
        if (kind == 'restore_alias') != bool(alias.get('retracted')): raise ValueError('Alias is already in the requested state')
        if kind == 'restore_alias':
            target = entities[alias['entity_id']]['canonical_id']
            if any(a['normalized'] == alias['normalized'] and not a.get('retracted') and entities[a['entity_id']]['canonical_id'] != target and not entities[a['entity_id']].get('inactive') for a in aliases.values()):
                raise ValueError('Restored alias collides with another active identity')
    elif kind == 'qualify':
        fact = assertions.get(op['assertion_id'])
        if not fact or fact['retirement']: raise ValueError('Qualify requires an active assertion')
        if 'context' not in op: raise ValueError('Qualify requires context')
        validate_context(op['context'], bool(fact['object_entity']))
        if op['context'].get('verification') == 'documented' and (fact['origin'] == 'inferred' or op['origin'] == 'inferred'): raise ValueError('Inferred connections cannot be marked documented')
    elif kind == 'event':
        entity = entities.get(op['equipment'])
        if not entity or entity.get('inactive') or entity['canonical_id'] != op['equipment']: raise ValueError('Event requires active canonical equipment')
        if entity.get('category') == 'document': raise ValueError('Choose equipment, not a document record, for an operating event')
        if op['event_type'] not in EVENT_TYPES: raise ValueError('Unsupported event type')
        timestamp(op['occurred_at'])
        if op.get('status', 'recorded') not in ('recorded', 'open', 'closed', 'hypothesis', 'reviewed'): raise ValueError('Unknown event status')
        if op.get('status') == 'reviewed' and op['event_type'] != 'lesson': raise ValueError('Reviewed status applies to lessons only')
        if not isinstance(op.get('details', ''), str) or len(op.get('details', '')) > 12000: raise ValueError('Details must be text up to 12000 characters')
        measurements = op.get('measurements', [])
        if not isinstance(measurements,list) or len(measurements)>20: raise ValueError('Use at most 20 structured readings per record')
        for reading in measurements:
            if not isinstance(reading,dict) or set(reading)-{'quantity','value','unit','condition','instrument'} or not {'quantity','value','unit'}<=set(reading): raise ValueError('Each reading requires quantity, value, unit and optional condition/instrument')
            for key in set(reading)-{'value'}:
                if not isinstance(reading[key],str) or not reading[key].strip() or len(reading[key])>200: raise ValueError('Reading labels must be nonempty text up to 200 characters')
            if isinstance(reading['value'],bool) or not isinstance(reading['value'],(float,int)) or not math.isfinite(reading['value']): raise ValueError('Reading value must be a finite number')
        if op.get('related_event'):
            linked = store.rows('SELECT * FROM operational_events WHERE id=?', (op['related_event'],), db)
            if not linked: raise ValueError('Related event does not exist')
            if entities[linked[0]['equipment']]['canonical_id'] != op['equipment']: raise ValueError('Related event belongs to different equipment')


def write_extra(db, op, version, eid, prov):
    kind = op['op']
    if kind == 'qualify':
        db.execute('INSERT INTO assertion_contexts VALUES(?,?,?,?,?,?)', (uid('ctx'), op['assertion_id'], dumps(op['context']), version, op['reason'], prov))
    elif kind == 'event':
        event_id = uid('evt')
        db.execute('INSERT INTO operational_events VALUES(?,?,?,?,?,?,?,?,?,?,?)', (event_id, eid(op['equipment']), op['event_type'], timestamp(op['occurred_at']).isoformat(), now(), op['summary'], op.get('details', ''), op.get('status', 'recorded'), op.get('related_event') or None, prov, version))
        for reading in op.get('measurements',[]):
            db.execute('INSERT INTO event_measurements VALUES(?,?,?)',(uid('reading'),event_id,dumps(reading)))
    elif kind == 'source_note':
        db.execute('INSERT INTO source_notes VALUES(?,?,?,?)',(uid('index'),op['text'],prov,version))
    else:
        db.execute('INSERT INTO identity_changes VALUES(?,?,?,?,?,?,?)', (uid('change'), kind, op.get('alias_id', op.get('entity', op.get('source'))), op.get('target'), version, op.get('reason', 'Reviewed identity merge'), prov))


def events(store, equipment=None, version=None, model=None):
    if version is not None:
        v = int(version)
        if v < 0 or v > store.version():
            raise ValueError('Unknown model version')
    else:
        v = model['version'] if model is not None else store.version()
    rows = store.rows('SELECT * FROM operational_events WHERE version<=? ORDER BY occurred_at DESC,recorded_at DESC', (v,))
    if not rows:
        return []
    if model is None:
        model = store.model(version)
    ids = {e['id']: e for e in model['entities']}
    result = []
    for row in rows:
        entity = ids[row['equipment']]
        if entity.get('inactive') or (equipment and entity['canonical_id'] != equipment): continue
        row['canonical_equipment'] = entity['canonical_id']
        row['provenance'] = json.loads(row['provenance'])
        row['measurements'] = []
        for reading in store.rows('SELECT body FROM event_measurements WHERE event_id=?',(row['id'],)):
            value = json.loads(reading['body'])
            row['measurements'].append({**value,'normalized_quantity':quantity(value['value'],value['unit'])})
        result.append(row)
    latest = {}
    for row in sorted(result, key=lambda x: (x['version'], x['recorded_at'])):
        if row['related_event'] and row['status'] in ('open', 'closed'):
            latest[row['related_event']] = row['status']
    for row in result:
        row['current_status'] = latest.get(row['id'], row['status'])
    return result


def trace(store, equipment, network='material', direction='upstream', condition='', as_of=None, follow_all=False):
    if network not in NETWORKS or direction not in ('upstream', 'downstream'): raise ValueError('Choose a network and trace direction')
    model = store.model()
    entities = {e['id']: e for e in model['entities'] if not e.get('inactive') and e['canonical_id'] == e['id'] and e.get('category')!='document'}
    if equipment not in entities: raise ValueError('Choose active equipment')
    at = timestamp(as_of) if as_of else datetime.now(timezone.utc)
    cond_query = (condition or '').strip()
    adjacency, excluded, available_conditions = {}, [], set()
    for fact in model['assertions']:
        if fact['retirement'] or not fact['canonical_object']: continue
        ctx = fact.get('context', {})
        if ctx.get('network') != network: continue
        source, target = fact['canonical_subject'], fact['canonical_object']
        if source not in entities or target not in entities: continue
        start, end = (target, source) if direction == 'upstream' else (source, target)
        cond_val = ctx.get('condition', '')
        reason = ''
        if ctx.get('verification') != 'documented' or fact['origin'] != 'explicit':
            reason = 'Connection is not documented'
        elif not follow_all and cond_val and cond_val != cond_query:
            reason = 'Operating condition must be selected explicitly'
        elif follow_all and cond_query and cond_val and cond_query.lower() not in cond_val.lower():
            reason = 'Operating condition does not match filter'
        elif ctx.get('valid_from') and at < timestamp(ctx['valid_from']):
            reason = 'Not valid at requested time'
        elif ctx.get('valid_to') and at >= timestamp(ctx['valid_to']):
            reason = 'No longer valid at requested time'
        adjacency.setdefault(start, []).append((end, fact, reason))
    visited, queue, paths, used = {equipment}, [(equipment, [])], [], []
    while queue:
        node, path = queue.pop(0)
        for end, fact, reason in adjacency.get(node, []):
            c_str = fact.get('context', {}).get('condition', '')
            if c_str:
                available_conditions.add(c_str)
            if reason:
                excluded.append({'assertion_id': fact['id'], 'at': node, 'reason': reason, 'context': fact['context']}); continue
            if fact['id'] not in used: used.append(fact['id'])
            if end in visited: continue
            visited.add(end)
            step = {'from': node, 'to': end, 'assertion_id': fact['id'], 'predicate': fact['predicate'], 'context': fact['context'], 'context_record':fact.get('context_record'), 'evidence': fact['evidence']}
            next_path = path + [step]
            paths.append({'equipment': end, 'label': entities[end]['label'], 'steps': next_path})
            queue.append((end, next_path))
    return {'version': model['version'], 'network': network, 'direction': direction, 'condition': condition, 'follow_all': bool(follow_all),
            'available_conditions': sorted(available_conditions), 'as_of': at.isoformat(), 'equipment': equipment, 'paths': paths, 'excluded': excluded,
            'edges': [a for a in model['assertions'] if a['id'] in used], 'complete': False,
            'notice': 'Documented possible connections only. One discovery path per reachable item; all traversed edges are listed. Unknown links and other networks may exist. This is not live route state or an isolation instruction.'}


def migration_report(store):
    model = store.model()
    active = [a for a in model['assertions'] if not a['retirement']]
    by_id = {e['id']: e for e in model['entities']}
    def item(a):
        return {'assertion_id': a['id'], 'equipment_id':a['canonical_subject'], 'equipment': by_id[a['canonical_subject']]['label'], 'predicate': a['predicate'], 'object_id':a['canonical_object'], 'object':by_id[a['canonical_object']]['label'] if a['canonical_object'] else None, 'value': a['value'], 'unit': a['unit'], 'context': a.get('context', {}), 'evidence': a.get('evidence', [])}
    return {'version': model['version'], 'counts': {'documents': len(store.rows('SELECT id FROM documents')), 'entities': len(model['entities']), 'active_assertions': len(active), 'events': len(events(store, model=model)), 'conflicts': len(model['conflicts'])},
            'missing_context': [item(a) for a in active if not a.get('context')],
            'document_entities': [{'id':e['id'],'label':e['label']} for e in model['entities'] if e.get('category')=='document'],
            'reference_relations': [item(a) for a in active if a['canonical_object'] and a['predicate'] in REFERENCE_RELATIONS],
            'network_review': [item(a) for a in active if a['canonical_object'] and a['predicate'] not in NON_NETWORK_RELATIONS and
                               (not a.get('context') or (a.get('context', {}).get('kind') == 'connection' and a.get('context', {}).get('verification') != 'documented'))],
            'unsupported_units': [item(a) for a in active if isinstance(a['value'], (int, float)) and not isinstance(a['value'], bool) and a['predicate'] not in DIMENSIONLESS_PROPERTIES and quantity(a['value'], a['unit']) is None],
            'dimensionless_properties': [item(a) for a in active if a['predicate'] in DIMENSIONLESS_PROPERTIES and not a['unit']],
            'entities_without_active_facts': [{'id': e['id'], 'label': e['label']} for e in model['entities'] if e['canonical_id'] == e['id'] and not e.get('inactive') and not any(a['canonical_subject'] == e['id'] or a['canonical_object'] == e['id'] for a in active)],
            'conflicts': model['conflicts'],
            'policy': 'These are review candidates, not proven errors. Preserve sources and IDs. Qualify supported facts; retract mistaken aliases; invalidate proven false entities. Never guess dates, units, functional locations, or network direction.'}

import hashlib
import re

def _det_id(prefix, key):
    h = hashlib.sha1(key.encode("utf-8")).hexdigest()[:20]
    return f"{prefix}_{h}"


def enrich_subcomponent_model(model):
    """Pass-through: all subcomponents are persisted canonically in plant.sqlite3 (Pass 17, v1008-v1099)."""
    return model
