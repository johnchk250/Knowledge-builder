"""Deterministic, evidence-preserving qualification of legacy accepted facts.

This migration changes only assertion context. Original assertions, values, units,
evidence and version history remain immutable. Ambiguous inverse/origin relations
are retained outside operational topology instead of being silently reversed.
"""
import argparse
import contextlib
import json
import sqlite3
from collections import Counter
from pathlib import Path

from .ingest import ingest
from .operating_model import REFERENCE_RELATIONS, migration_report
from .patches import commit
from .reviewed_ingestion import stage
from .store import Store, dumps, now


CLASSIFICATION_PROPERTIES = {
    'instance_of',
    'manufacturer',
    'package_vendor',
    'customer_consultant',
    'customer_project',
    'epc_contractor',
    'report_author',
    'report_date',
    'revision',
    'approval_stamp_date',
    'approval_date',
    'fio_stamp_date',
    'drawing_issue_status',
    'document_note',
    'reported_statement',
}

# These predicates describe material movement but point from the conveyor back
# to its origin. They are useful legacy semantics, but are intentionally not
# operational graph edges because graph direction is upstream -> downstream.
INVERSE_MATERIAL_RELATIONS = {'conveys_from'}

# The predicate itself has already been reviewed as subject discharges into
# object. Promoting it to a material connection therefore adds no new direction.
DIRECT_MATERIAL_RELATIONS = {'discharges_to'}


def legacy_context(assertion, entities):
    """Return a conservative operational context for an unqualified assertion."""
    if assertion.get('context'):
        return None
    predicate = assertion['predicate']
    if assertion.get('canonical_object'):
        if predicate in DIRECT_MATERIAL_RELATIONS and assertion.get('origin') == 'explicit':
            return {'kind': 'connection', 'network': 'material', 'verification': 'documented'}
        if predicate in REFERENCE_RELATIONS or predicate in INVERSE_MATERIAL_RELATIONS:
            return {'kind': 'classification'}
        return None

    subject = entities[assertion['canonical_subject']]
    if subject.get('category') == 'document' or predicate in CLASSIFICATION_PROPERTIES:
        return {'kind': 'classification'}
    return {'kind': 'specification'}


def plan(store):
    """Build only context qualifications that are deterministic from accepted semantics."""
    model = store.model()
    entities = {e['id']: e for e in model['entities']}
    operations, deferred = [], []
    counts = Counter()
    for assertion in model['assertions']:
        if assertion['retirement'] or assertion.get('context'):
            continue
        context = legacy_context(assertion, entities)
        if context is None:
            deferred.append({
                'assertion_id': assertion['id'],
                'predicate': assertion['predicate'],
                'subject': assertion['canonical_subject'],
                'object': assertion.get('canonical_object'),
                'reason': 'Entity relation is not safe to orient automatically.',
            })
            continue
        if context.get('kind') == 'connection':
            reason = ('Automated legacy qualification: accepted explicit discharges_to semantics already '
                      'encode upstream subject -> downstream object; promoted to documented material topology.')
            origin = 'explicit'
        elif assertion['predicate'] in INVERSE_MATERIAL_RELATIONS:
            reason = ('Automated legacy qualification: retained the accepted conveys_from relation as descriptive '
                      'classification; it is intentionally excluded from topology because its subject/object '
                      'direction is inverse to operational graph direction.')
            origin = 'inferred'
        elif context['kind'] == 'classification':
            reason = ('Automated legacy qualification: retained accepted identity, document/reference or descriptive '
                      'metadata as classification; no value, unit, date, location or applicability was invented.')
            origin = 'inferred'
        else:
            reason = ('Automated legacy qualification: retained the accepted equipment value as a specification; '
                      'basis, condition, validity and functional location remain unspecified unless already supported.')
            origin = 'inferred'
        operations.append({
            'op': 'qualify',
            'assertion_id': assertion['id'],
            'context': context,
            'reason': reason,
            '_migration_origin': origin,
        })
        counts[context['kind']] += 1
    return {
        'base_version': model['version'],
        'operations': operations,
        'deferred': deferred,
        'counts': dict(counts),
    }


def backup_database(store, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise ValueError(f'Backup already exists: {destination}')
    with contextlib.closing(store.connect()) as source, contextlib.closing(sqlite3.connect(destination)) as target:
        source.backup(target)
    return destination


def _commit_batch(store, batch, batch_number, total_batches):
    source_text = (
        'Automated existing-data operational context migration.\n'
        f'Batch: {batch_number}/{total_batches}\n'
        f'Base plant version: {store.version()}\n'
        f'Assertions qualified: {len(batch)}\n'
        'Scope: context only. Original assertion values, units, evidence, identities and source files are unchanged.\n'
        'Rules: document/reference/descriptive metadata -> classification; equipment values -> specification; '
        'explicit discharges_to -> documented material connection; conveys_from remains descriptive and is not '
        'silently reversed into topology. Unknown basis, dates, conditions, ports and locations remain unknown.\n'
    )
    document = ingest(
        store,
        f'operations-context-migration-{batch_number:02d}-of-{total_batches:02d}.txt',
        source_text.encode('utf-8'),
        revision='operations/1 deterministic migration',
        authority='Automated evidence-preserving migration',
    )['document']
    evidence = store.rows('SELECT * FROM evidence WHERE document_id=? ORDER BY rowid', (document['id'],))
    support = [{'evidence_id': e['id'], 'quote': e['text']} for e in evidence]
    operations = []
    for op in batch:
        origin = op.pop('_migration_origin')
        operations.append({**op, 'origin': origin, 'confidence': 1.0, 'evidence': support})
    envelope = {
        'summary': f'Qualify {len(operations)} legacy assertions for operational use without changing their facts.',
        'operations': operations,
        'intake_assessment': {
            'route': 'mixed',
            'purpose': 'Migrate accepted legacy assertion semantics into the operations-focused context model.',
            'questions': ['How should these already accepted facts participate in operational retrieval and topology?'],
            'gaps': ['Unknown basis, conditions, dates, ports and functional locations remain unspecified.'],
            'reviewed_evidence_ids': [e['id'] for e in evidence],
        },
    }
    staged = stage(store, document['id'], envelope, expected_version=store.version())
    committed = commit(store, staged['proposal_id'])
    return {'document_id': document['id'], 'proposal_id': staged['proposal_id'], **committed}


def apply(store, batch_size=250):
    if not isinstance(batch_size, int) or not 1 <= batch_size <= 500:
        raise ValueError('batch_size must be between 1 and 500')
    migration = plan(store)
    if migration['deferred']:
        raise ValueError(f"{len(migration['deferred'])} relations remain unsafe for automatic migration")
    operations = migration['operations']
    if not operations:
        return {'base_version': migration['base_version'], 'final_version': store.version(), 'batches': [],
                'qualified': 0, 'counts': migration['counts'], 'remaining': migration_report(store)}
    batches = [operations[i:i + batch_size] for i in range(0, len(operations), batch_size)]
    results = []
    for index, batch in enumerate(batches, 1):
        # Copy because provenance preparation removes the private planner field.
        results.append(_commit_batch(store, [dict(op) for op in batch], index, len(batches)))
    return {
        'base_version': migration['base_version'],
        'final_version': store.version(),
        'qualified': len(operations),
        'counts': migration['counts'],
        'batches': results,
        'remaining': migration_report(store),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description='Deterministically qualify accepted legacy CHP facts.')
    parser.add_argument('--root', default='data/plant', help='Plant store directory')
    parser.add_argument('--apply', action='store_true', help='Commit the append-only migration; default is dry-run')
    parser.add_argument('--batch-size', type=int, default=250)
    parser.add_argument('--backup', default='', help='SQLite backup path required with --apply')
    parser.add_argument('--report', default='', help='Optional JSON result path')
    args = parser.parse_args(argv)
    store = Store(Path(args.root))
    result = plan(store)
    if args.apply:
        if not args.backup:
            parser.error('--backup is required with --apply')
        backup_database(store, args.backup)
        result = apply(store, args.batch_size)
        result['backup'] = str(Path(args.backup).resolve())
        result['completed_at'] = now()
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(text + '\n', encoding='utf-8')
    print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
