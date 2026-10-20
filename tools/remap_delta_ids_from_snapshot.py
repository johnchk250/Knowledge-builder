"""Repair stale assertion/entity IDs in a returned delta using its authoring snapshot.

A delta returned by the top model may have been authored against a re-applied
working copy of the same model version. Re-applying the accepted proposals
regenerates random assertion IDs, so `retire` references point at facts that do
not exist in the canonical DB although the facts themselves are identical.
Pass 15's two stale entity IDs are the same phenomenon for identities.

The snapshot (the sqlite file the author saw) allows a strictly grounded repair:

  * a stale entity ID must not resolve in the live model, must resolve in the
    snapshot, its snapshot label must resolve to exactly one live entity, and
    that live entity must carry the identical label;
  * a stale assertion ID must not resolve in the live model, must resolve in the
    snapshot, and exactly one LIVE, NON-RETIRED assertion must match it on
    subject / predicate / value / object_entity / unit / evidence (entity IDs in
    the snapshot signature are resolved through the entity map);
  * every stale reference must resolve; anything ambiguous is refused;
  * duplicate `assert` operations that repeat an active canonical fact are
    reported (not removed), because the delta is otherwise applied as returned.

Usage:
    python tools/remap_delta_ids_from_snapshot.py <delta.json> <authoring.sqlite3> <out.json>

A repair report is written next to the output as <out>.repair.json.
"""
import argparse
import collections
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chp.store import Store


def load_delta(path):
    delta = json.loads(Path(path).read_text(encoding='utf-8'))
    if delta.get('schema_version') != 1 or not isinstance(delta.get('proposals'), list):
        raise SystemExit('Unsupported delta file: expected schema_version 1 and a proposals array')
    return delta


def signature(row, entity_map):
    subject = entity_map.get(row['subject'], row['subject'])
    obj = row['object_entity']
    obj = entity_map.get(obj, obj) if obj else None
    return (subject, row['predicate'], row['value'], obj, row['unit'])


def evidence_value(text):
    try:
        return json.loads(text or '[]')
    except ValueError:
        return text


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('delta', help='path to the returned delta JSON')
    parser.add_argument('snapshot', help='path to the sqlite DB the delta author saw')
    parser.add_argument('out', help='path to write the repaired delta JSON')
    parser.add_argument('--live', default=str(ROOT / 'data/plant'),
                        help='data directory of the canonical model (default: data/plant)')
    args = parser.parse_args()

    delta = load_delta(args.delta)
    store = Store(Path(args.live))
    if store.version() != delta['base_version']:
        raise SystemExit('Delta base_version %s does not match live version %s'
                         % (delta['base_version'], store.version()))
    live_entities = {r['id']: r for r in store.rows('SELECT id, label FROM entities')}
    live_assertions = [r for r in store.rows('SELECT * FROM assertions')]
    retired = {r['assertion_id'] for r in store.rows('SELECT assertion_id FROM retirements')}

    snapshot = sqlite3.connect(Path(args.snapshot).resolve().as_uri() + '?mode=ro', uri=True)
    snapshot.row_factory = sqlite3.Row
    snap_version = snapshot.execute("SELECT value FROM meta WHERE key='version'").fetchone()
    if not snap_version or int(snap_version[0]) != delta['base_version']:
        raise SystemExit('Snapshot version %s does not match delta base_version %s'
                         % (snap_version[0] if snap_version else None, delta['base_version']))
    snapshot_retired = {r[0] for r in snapshot.execute('SELECT assertion_id FROM retirements')}

    operations = [(pi, oi, op) for pi, p in enumerate(delta['proposals'])
                  for oi, op in enumerate(p.get('operations') or [])]

    # --- entities: resolve every stale reference by exact label -------------
    entity_map = {}
    entity_changes = []
    stale_entities = sorted({op[f] for _, _, op in operations for f in ('subject', 'object_entity')
                             if isinstance(op.get(f), str) and op[f] not in live_entities})
    for stale in stale_entities:
        row = snapshot.execute('SELECT id, label FROM entities WHERE id=?', (stale,)).fetchone()
        if not row:
            raise SystemExit('Stale entity %s is in neither the live model nor the snapshot' % stale)
        matches = [r['id'] for r in live_entities.values() if r['label'] == row['label']]
        if len(matches) != 1:
            raise SystemExit('Entity %s (%r): expected exactly one live label match, found %d'
                             % (stale, row['label'], len(matches)))
        entity_map[stale] = matches[0]
        for pi, oi, op in operations:
            for field in ('subject', 'object_entity'):
                if op.get(field) == stale:
                    op[field] = matches[0]
                    entity_changes.append({'proposal': pi + 1, 'operation': oi + 1, 'field': field,
                                           'from': stale, 'to': matches[0], 'label': row['label']})

    # --- assertions: resolve every stale retire ID by exact content ---------
    live_by_signature = collections.defaultdict(list)
    for row in live_assertions:
        if row['id'] in retired:
            continue
        live_by_signature[signature(row, entity_map)].append(row)

    assertion_map = {}
    assertion_changes = []
    live_ids = {r['id'] for r in live_assertions}
    stale_ids = sorted({op['assertion_id'] for _, _, op in operations
                        if op['op'] == 'retire' and op['assertion_id'] not in live_ids})
    for stale in stale_ids:
        snap = snapshot.execute('SELECT * FROM assertions WHERE id=?', (stale,)).fetchone()
        if not snap:
            raise SystemExit('Retired assertion %s is in neither the live model nor the snapshot' % stale)
        if stale in snapshot_retired:
            raise SystemExit('Retired assertion %s is already retired in the snapshot' % stale)
        candidates = [r for r in live_by_signature.get(signature(snap, entity_map), [])
                      if evidence_value(r['evidence']) == evidence_value(snap['evidence'])]
        if len(candidates) != 1:
            raise SystemExit('Assertion %s: expected exactly one active live content match, found %d'
                             % (stale, len(candidates)))
        if candidates[0]['id'] in assertion_map.values():
            raise SystemExit('Assertion %s resolves to an ID already used by another stale ID' % stale)
        assertion_map[stale] = candidates[0]['id']
        for pi, oi, op in operations:
            if op['op'] == 'retire' and op['assertion_id'] == stale:
                assertion_changes.append({'proposal': pi + 1, 'operation': oi + 1,
                                          'from': stale, 'to': candidates[0]['id'],
                                          'record': {k: snap[k] for k in
                                                     ('subject', 'predicate', 'value', 'object_entity')}})
                op['assertion_id'] = candidates[0]['id']

    # --- post-conditions and duplicate reporting ----------------------------
    live_entity_ids = set(live_entities)
    for pi, oi, op in operations:
        for field in ('subject', 'object_entity'):
            if isinstance(op.get(field), str) and op[field] not in live_entity_ids:
                raise SystemExit('Post-check: proposal %d operation %d has unresolved entity %s'
                                 % (pi + 1, oi + 1, op[field]))
        if op['op'] != 'retire' and op.get('assertion_id'):
            raise SystemExit('Unsupported operation %s with assertion_id in proposal %d operation %d'
                             % (op['op'], pi + 1, oi + 1))
        if op['op'] == 'retire' and op['assertion_id'] not in live_ids:
            raise SystemExit('Post-check: proposal %d operation %d has unresolved assertion %s'
                             % (pi + 1, oi + 1, op['assertion_id']))
        if op['op'] == 'retire' and op['assertion_id'] in retired:
            raise SystemExit('Post-check: proposal %d operation %d retires already-retired assertion %s'
                             % (pi + 1, oi + 1, op['assertion_id']))

    duplicate_asserts = []
    for pi, oi, op in operations:
        if op['op'] != 'assert':
            continue
        key = (op['subject'], op['predicate'], op.get('value'), op.get('object_entity'), op.get('unit'))
        existing = [r['id'] for r in live_by_signature.get(key, [])]
        if existing:
            duplicate_asserts.append({'proposal': pi + 1, 'operation': oi + 1,
                                      'existing_assertion_ids': existing})

    Path(args.out).write_text(json.dumps(delta, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    report = {
        'delta': str(args.delta),
        'snapshot': str(args.snapshot),
        'out': str(args.out),
        'live_version': store.version(),
        'entity_map': entity_map,
        'assertion_map': assertion_map,
        'entity_changes': entity_changes,
        'assertion_changes': assertion_changes,
        'duplicate_asserts': duplicate_asserts,
    }
    Path(args.out + '.repair.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'entities': len(entity_map), 'assertions': len(assertion_map),
                      'entity_refs': len(entity_changes), 'retire_refs': len(assertion_changes),
                      'duplicate_asserts': len(duplicate_asserts)}))


if __name__ == '__main__':
    main()
