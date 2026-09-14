"""Record an externally reviewed document analysis through both review queues."""
from . import understanding, usage_intake
from .patches import validate
from .store import dumps, now, uid


def stage(store, document_id, result, visual_ids=(), analysis_dir='', geometry_assessment='', expected_version=None):
    """Accept an analysis envelope; keep geometry outside the canonical patch.

    The caller is responsible for source review. This records that external origin
    honestly; it does not claim the application ran an AI provider or saw images.
    """
    understanding.initialize(store)
    if not isinstance(result, dict) or set(result) - {'summary','operations','intake_assessment'}:
        raise ValueError('Expected summary, operations and intake_assessment. 3D intake is paused.')
    body = {key: result.get(key) for key in ('summary','operations')}
    if not isinstance(body['operations'],list): raise ValueError('Operations must be an array')
    evidence = store.rows('SELECT id FROM evidence WHERE document_id=?',(document_id,))
    if not evidence: raise ValueError('Document not found or has no evidence')
    usage_intake.validate_assessment(result.get('intake_assessment'),[e['id'] for e in evidence],body['operations'])
    version = store.version()
    if expected_version is not None and version != expected_version:
        raise ValueError('Plant changed while preparing the record. Refresh and review again.')
    guidance = understanding.current(store)['revision']
    visual_ids = set(visual_ids)
    known = {e['id'] for e in store.rows('SELECT id FROM evidence WHERE document_id=? AND image IS NOT NULL', (document_id,))}
    if not visual_ids <= known:
        raise ValueError('Visual review IDs must be rendered evidence from this document')
    findings = validate(store, body, document_id, version, visual_ids=visual_ids)
    if findings['errors']:
        raise ValueError('; '.join(findings['errors']))
    run_id, proposal_id = uid('run'), uid('prop')
    manifest = {'provider':'external_review','mode':'EXTERNALLY_REVIEWED','understanding_revision':guidance,
                'vision':bool(visual_ids),'analysis_dir':analysis_dir,'intake_policy':usage_intake.POLICY}
    request = {'document_id':document_id,'analysis_mode':'EXTERNALLY_REVIEWED',
               'images':[{'evidence_id':eid} for eid in sorted(visual_ids)],'analysis_dir':analysis_dir,'prompt_version':usage_intake.POLICY}
    with store.transaction() as db:
        if store.version(db) != version or understanding.current(store, db)['revision'] != guidance:
            raise ValueError('Plant or guidance changed during staging. Review again.')
        db.execute('CREATE TABLE IF NOT EXISTS run_steps(id TEXT PRIMARY KEY,run_id TEXT NOT NULL REFERENCES runs(id),stage TEXT NOT NULL,request TEXT NOT NULL,response TEXT NOT NULL,created TEXT NOT NULL)')
        for action in ('UPDATE','DELETE'):
            db.execute(f"CREATE TRIGGER IF NOT EXISTS immutable_steps_{action} BEFORE {action} ON run_steps BEGIN SELECT RAISE(ABORT,'immutable record'); END")
        db.execute('INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?)',
                   (run_id, document_id, 'complete', version, 'codex_current_session', now(),
                    'Operational intake ready for review', None, dumps(manifest)))
        db.execute('INSERT INTO run_steps VALUES(?,?,?,?,?,?)',
                   (uid('step'), run_id, 'propose', dumps(request), dumps(result), now()))
        db.execute('INSERT INTO proposals VALUES(?,?,?,?,?,?,?,?,?)',
                   (proposal_id, run_id, document_id, version, dumps(body), 'pending', dumps(findings), now(), None))
    return {'proposal_id':proposal_id,'run_id':run_id,'base_version':version,
            'warnings':findings['warnings'],'intake_assessment':result['intake_assessment']}
