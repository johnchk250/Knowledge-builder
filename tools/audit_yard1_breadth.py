"""Read-only current Yard1 semantic/boundary review, not a historical migration audit."""
import argparse
import json
from pathlib import Path
from audit_yard1_pilot import audit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('snapshot')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    snap = json.loads(Path(args.snapshot).read_text(encoding='utf8'))
    model = snap['model']
    # No mutations in B15/B16. Reuse only the pilot's current semantic checks;
    # comparing a snapshot with itself does not establish historical preservation.
    semantic = audit(model, model, snap['evidence'])
    labels = {e['canonical_id']: e['label'] for e in model['entities']}
    ids = {v: k for k, v in labels.items()}
    facts = [a for a in model['assertions'] if not a.get('retirement') and not a.get('suppressed')]
    edges = {(labels[a['canonical_subject']], labels[a['canonical_object']])
             for a in facts if a['predicate'] == 'material_flow_to'}
    checks = semantic['checks'][2:]
    chain = ['EAC-7', 'EAD-1', 'EAE-1', 'EAF-1', 'EBA-8', 'FG-10']
    for a, b in zip(chain, chain[1:]):
        assert (a, b) in edges, (a, b)
    assert {b for a, b in edges if a == 'FG-10'} == {'EBA-15A', 'EBA-15B'}
    checks.append('Yard1 exact coal chain and both FG10 downstream alternatives')
    inlet = [a for a in facts if a['predicate'] == 'material_flow_to'
             and a.get('canonical_object') == ids['EAC-7']]
    assert any(a['created_version'] >= 653 for a in inlet), 'B13 inlet missing'
    checks.append('B13 source-reviewed TP6 inlet retained')
    evidence = {e['id']: e for e in snap['evidence']}
    owned = {ids['Coal Yard 1']}
    while True:
        more = {a['canonical_subject'] for a in facts if a['predicate'] == 'part_of'
                and a.get('canonical_object') in owned} - owned
        if not more:
            break
        owned |= more
    claims = [a for a in facts if a['canonical_subject'] in owned]
    for a in claims:
        assert a['evidence']
        assert all(ref['evidence_id'] in evidence for ref in a['evidence'])
    checks.append('All current Yard1 claims retain resolvable evidence references')
    report = dict(ok=True, version=model['version'], mode='current_semantics_only',
                  canonical_changes=0, historical_preservation_claimed=False,
                  yard_records=len(owned), current_yard_claims=len(claims), checks=checks)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2)+'\n', encoding='utf8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
