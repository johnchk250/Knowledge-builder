"""Conservative, inspectable bridge from accepted assertions to spatial drafts.

No text-number guessing, routing inference, or writes to the knowledge graph.
Rules describe the represented envelope, not every component of an assembly.
"""
import math
import re
import json
from collections import defaultdict
from .store import dumps

NONPHYSICAL = re.compile(r'drawing|document|report|manual|specification|procedure|review_sheet|quality_assurance|email|schedule|organization|company|person|observation|event')
UNITS = {'m': 1, 'metre': 1, 'meter': 1, 'mm': .001, 'cm': .01, 'ft': .3048, 'in': .0254}
# Predicate mappings are deliberately exact. Belt loop length is NOT conveyor length.
RULES = {
    'overall_length': (('size.x',), None, 'Overall bounding length'),
    'overall_height': (('size.y',), None, 'Overall bounding height'),
    'overall_width': (('size.z',), None, 'Overall bounding width'),
    'profile_length': (('size.x',), 'conveyor', 'Conveyor profile length; straight proxy does not reconstruct its bends or inclines'),
    'belt_width': (('size.z',), 'conveyor', 'Belt working width; proxy excludes the unknown outer structure envelope'),
    'pulley_diameter': (('size.y', 'size.z'), 'pulley', 'Pulley barrel diameter; shaft and hub extents are not represented'),
    'face_width': (('size.x',), 'pulley', 'Pulley barrel face width; shaft and hub extents are not represented'),
    'stockpile_length': (('size.x',), 'stockpile', 'Stockpile design envelope length'),
    'stockpile_width': (('size.z',), 'stockpile', 'Stockpile design envelope width'),
    'max_stockpile_height': (('size.y',), 'stockpile', 'Maximum design envelope height, not a measured current coal level'),
}


def shape_for(types):
    name = ' '.join(types).lower()
    for word, shape in [('pulley', 'pulley'), ('idler', 'pulley'), ('stockpile', 'stockpile'),
                        ('conveyor', 'conveyor'), ('belt_feeder', 'conveyor'), ('motor', 'motor'),
                        ('gearbox', 'gearbox'), ('sensor', 'sensor'), ('detector', 'sensor'),
                        ('analyser', 'sensor'), ('monitor', 'sensor'), ('hopper', 'hopper'),
                        ('chute', 'hopper'), ('tank', 'cylinder'), ('hydraulic_cylinder', 'cylinder'),
                        ('house', 'building'), ('cabin', 'building'), ('pump', 'pump'), ('fan', 'fan'), ('valve', 'valve'), ('gate', 'gate'),
                        ('filter', 'filter'), ('house', 'building'), ('cabin', 'building'),
                        ('stacker', 'stacker'), ('reclaimer', 'stacker'), ('ship_unloader', 'unloader')]:
        if word in name:
            return shape
    return 'box'


def catalog(store, model=None):
    from .spatial import evidence_errors
    model = model or store.model()
    facts = defaultdict(list)
    for a in model['assertions']:
        if not a['retirement']:
            facts[a['canonical_subject']].append(a)
    result = []
    for entity in model['entities']:
        if entity['id'] != entity['canonical_id']:
            continue
        active = facts[entity['id']]
        types = sorted({a['value'] for a in active if a['predicate'] == 'instance_of' and isinstance(a['value'], str)})
        physical = len(types) == 1 and not any(NONPHYSICAL.search(t) for t in types)
        shape = shape_for(types)
        candidates = defaultdict(list)
        issues = []
        dimensions = []
        for a in active:
            pred = a['predicate']
            if not any(word in pred for word in ('length', 'width', 'height', 'diameter', 'elevation', 'coordinate')):
                continue
            dimensions.append({k: a[k] for k in ('id', 'predicate', 'value', 'unit', 'evidence', 'origin')})
            rule = RULES.get(pred)
            if not rule or (rule[1] and rule[1] != shape):
                issues.append(f'{pred}: retained in knowledge; no unambiguous envelope mapping.')
                continue
            keys, _, meaning = rule
            factor = UNITS.get((a['unit'] or '').strip().lower())
            value = a['value']
            valid = (a['origin'] == 'explicit' and type(value) in (int, float)
                     and factor is not None and math.isfinite(value) and 0 < value * factor <= 100000)
            refs = a['evidence']
            if valid:
                valid = not evidence_errors(store, refs)
            for key in keys:
                candidates[key].append((a, round(value * factor, 12) if valid else None, meaning))
        params = {}
        sources = {}
        for key, group in candidates.items():
            values = [row[1] for row in group]
            if any(v is None for v in values) or any(not math.isclose(v, values[0], rel_tol=1e-9, abs_tol=1e-9) for v in values):
                issues.append(f'{key}: competing, inferred, invalid or unsupported-unit assertions; no dimension applied.')
                continue
            refs = list({dumps(ref): ref for a, _, _ in group for ref in a['evidence']}.values())
            if len(refs) > 10:
                issues.append(f'{key}: more than 10 source references; review explicitly.')
                continue
            ids = [a['id'] for a, _, _ in group]
            note = 'Accepted knowledge: ' + '; '.join(sorted({meaning for _, _, meaning in group})) + '. Assertions: ' + ', '.join(ids)
            if len(note) > 1200:
                issues.append(f'{key}: source history needs explicit review.')
                continue
            params[key] = {'value': values[0], 'basis': 'document', 'note': note, 'evidence': refs}
            sources[key] = ids
        result.append({'entity_id': entity['id'], 'label': entity['label'], 'types': types, 'shape': shape,
                       'eligible': physical, 'exclusion': '' if physical else 'Document/nonphysical record, unclassified identity or conflicting classifications',
                       'parameters': params if physical else {}, 'assertions': sources if physical else {},
                       'dimensions': dimensions, 'issues': sorted(set(issues))})
    return {'model_version': model['version'], 'equipment': result,
            'eligible_count': sum(e['eligible'] for e in result),
            'excluded_count': sum(not e['eligible'] for e in result),
            'supported_parameters': sum(len(e['parameters']) for e in result if e['eligible'])}


def build(store, entity_ids=None, use_knowledge=True):
    from . import spatial
    if type(use_knowledge) is not bool:
        raise ValueError('use_knowledge must be true or false')
    old = spatial.current(store)
    model = store.model()
    inventory = catalog(store, model)
    available = {e['entity_id']: e for e in inventory['equipment']}
    if entity_ids is not None and (not isinstance(entity_ids, list) or any(not isinstance(e, str) or e not in available for e in entity_ids)):
        raise ValueError('Choose current canonical equipment identities')
    selected = set(entity_ids) if entity_ids is not None else {e['entity_id'] for e in inventory['equipment'] if e['eligible']}
    scene = json.loads(dumps(old['scene']))
    byid = {i['entity_id']: i for i in scene}
    if any(eid not in available for eid in byid):
        raise ValueError('A represented entity was merged. Reassign or remove its representation in Edit scene JSON before building.')
    if len(set(byid) | selected) > spatial.MAX_ITEMS:
        raise ValueError(f'Select a smaller scope: maximum {spatial.MAX_ITEMS} representations per saved scene.')
    entities = {e['id']: e for e in model['entities']}
    changes, issues, added = [], [], []
    for eid in sorted(selected, key=lambda x: (available[x]['shape'], available[x]['label'])):
        info = available[eid]
        if eid not in byid:
            item = spatial.template(entities[eid], len(scene), model)
            scene.append(item)
            byid[eid] = item
            added.append(item)
        item = byid[eid]
        issues.extend({'entity_id': eid, 'label': info['label'], 'message': message} for message in info['issues'])
        if not use_knowledge:
            continue
        for key, previous in item['parameters'].items():
            if previous['basis'] == 'document' and previous['note'].startswith('Accepted knowledge:') and key not in info['parameters']:
                issues.append({'entity_id': eid, 'label': info['label'], 'message': f'{key}: saved knowledge dimension no longer has an unambiguous active mapping; preserved for explicit review.'})
        for key, param in info['parameters'].items():
            previous = item['parameters'][key]
            if item['shape'] != info['shape'] or item['shape'] == 'mesh':
                issues.append({'entity_id': eid, 'label': info['label'], 'message': f'{key}: existing shape preserved; apply dimensions explicitly.'})
            elif previous['basis'] == 'schematic':
                changes.append({'entity_id': eid, 'label': info['label'], 'parameter': key, 'previous': previous, 'proposed': param})
                item['parameters'][key] = param
            elif previous != param:
                issues.append({'entity_id': eid, 'label': info['label'], 'message': f'{key}: saved reviewed value preserved; compare with current knowledge before replacing.'})
    # Pack only NEW objects after existing extents. Never overwrite reviewed placement.
    # Sizes may span millimetres to hundreds of metres, so fixed grid cells overlap.
    added_ids = {i['entity_id'] for i in added}
    existing = [i for i in scene if i['entity_id'] not in added_ids]
    z = max((max(v[2] for v in spatial.world_mesh(store, i)) for i in existing), default=-6) + 6
    columns = max(1, math.ceil(math.sqrt(len(added))))
    x, row_depth = 0, 0
    for n, item in enumerate(added):
        sx, sy, sz = [item['parameters']['size.' + a]['value'] for a in 'xyz']
        if n and n % columns == 0:
            x = 0; z += row_depth + 6; row_depth = 0
        for axis, value in zip('xyz', (x + sx / 2, sy / 2, z + sz / 2)):
            item['parameters']['position.' + axis] = spatial.parameter(value, 'Schematic size-aware catalog placement, not a surveyed plant coordinate.')
        x += sx + 6
        row_depth = max(row_depth, sz)
    errors = spatial.validate_scene(store, scene)
    if errors:
        raise ValueError('; '.join(errors))
    if sum(len(spatial.world_mesh(store, i)) // 3 for i in scene) > spatial.MAX_TRIANGLES:
        raise ValueError('Scene triangle budget exceeded. Build a smaller scope or simplify imported meshes.')
    if store.version() != model['version'] or spatial.current(store)['revision'] != old['revision']:
        raise ValueError('Plant or spatial model changed during build. Build again.')
    return {**old, 'model_version': model['version'], 'scene': scene, 'changes': changes, 'issues': issues,
            'build_summary': {'added': len(added), 'total': len(scene), 'supported_parameters_applied': len(changes),
                              'excluded_records': inventory['excluded_count'], 'selected': len(selected)}}
