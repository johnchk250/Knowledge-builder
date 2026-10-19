"""Repair stale entity IDs in a returned delta before it is applied.

A delta returned by the top model may reference entity IDs that do not exist in
the canonical plant model, because the entity was re-created (or the model was
rolled back and re-applied) after the delta was authored. The reference can
still be resolved unambiguously when exactly one live entity carries the
identical canonical label that the delta itself quotes in its context/basis.

This tool performs ONLY that kind of repair. It is deliberately strict:

  * the stale ID must not resolve in the live model (it is stale, not merged);
  * the replacement ID must resolve in the live model;
  * the replacement entity's canonical label must equal the expected label
    exactly (no fuzzy, prefix or substring matching);
  * the expected label must appear verbatim in the affected operation's
    context/basis text, so the repair is grounded in the delta's own wording;
  * every other entity reference in the delta is left untouched.

Usage:
    python tools/remap_delta_entity_ids.py <delta.json> <mapping.json> <out.json>

The mapping file is a JSON object of the form:

    {
      "stale_id": {
        "id": "<replacement id>",
        "label": "<exact expected canonical label>"
      }
    }

A remap report is written next to the output file as <out>.remap.json.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chp.store import Store


def iter_refs(ops):
    """Yield (index, op, field) for every entity reference in a proposal."""
    for i, op in enumerate(ops):
        if not isinstance(op, dict):
            continue
        for field in ('subject', 'object_entity'):
            if isinstance(op.get(field), str):
                yield i, op, field


def op_text(op):
    parts = []
    for key in ('basis', 'reason'):
        value = op.get(key)
        if isinstance(value, str):
            parts.append(value)
    ctx = op.get('context')
    if isinstance(ctx, dict):
        for value in ctx.values():
            if isinstance(value, str):
                parts.append(value)
    return '\n'.join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('delta', help='path to the delta JSON to repair')
    parser.add_argument('mapping', help='path to the stale-id -> canonical-id mapping JSON')
    parser.add_argument('out', help='path to write the repaired delta JSON')
    args = parser.parse_args()

    delta_path = Path(args.delta)
    mapping_path = Path(args.mapping)
    delta = json.loads(delta_path.read_text(encoding='utf-8'))
    mapping = json.loads(mapping_path.read_text(encoding='utf-8'))

    store = Store(ROOT / 'data/plant')
    model = store.model()
    entities = {e['id']: e for e in model['entities']}

    for stale, rule in mapping.items():
        if stale in entities:
            raise SystemExit('Refusing to remap %s: it resolves in the live model' % stale)
        target = rule['id']
        if target not in entities:
            raise SystemExit('Refusing to remap %s: replacement %s does not resolve' % (stale, target))
        actual = entities[target]['label']
        if actual != rule['label']:
            raise SystemExit('Refusing to remap %s: %s is labelled %r, expected %r'
                             % (stale, target, actual, rule['label']))

    report = {'delta': str(delta_path), 'mapping': str(mapping_path), 'changes': []}
    counts = {stale: 0 for stale in mapping}
    for pi, proposal in enumerate(delta.get('proposals') or []):
        ops = proposal.get('operations') or []
        for i, op, field in iter_refs(ops):
            value = op[field]
            if value not in mapping:
                continue
            rule = mapping[value]
            if rule['label'] not in op_text(op):
                raise SystemExit(
                    'Refusing to remap %s in proposal %d operation %d: the expected label %r '
                    'does not appear in the operation context/basis'
                    % (value, pi + 1, i + 1, rule['label']))
            op[field] = rule['id']
            counts[value] += 1
            report['changes'].append({
                'proposal': pi + 1,
                'document': proposal.get('document'),
                'operation': i + 1,
                'field': field,
                'from': value,
                'to': rule['id'],
                'label': rule['label'],
            })

    for stale, count in counts.items():
        if count == 0:
            raise SystemExit('Mapping entry %s was never used; the delta does not contain it' % stale)

    Path(args.out).write_text(json.dumps(delta, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    report['out'] = str(args.out)
    Path(args.out + '.remap.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'remapped': sum(counts.values()), 'by_stale_id': counts}))


if __name__ == '__main__':
    main()
