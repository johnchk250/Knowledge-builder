"""Independent check of the B02 header-link acceptance (v629/v630) against the live read-only model."""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chp.store import Store

OUT = ROOT / 'output/plant-enrichment/B02'
CHAINS = {
    'DFDS-1 air pump-house chain': ('ent_081c34835a684544a6d0', 'ent_21a02d1f40f04686a18a'),   # compressor 1A -> UEF-1 air main
    'DFDS-1 water pump chain': ('ent_975edb9acc07451cbc62', 'ent_3e6f0c75149b49cdbce2'),     # pump 1A -> UEF-1 water main
    'DFDS-2 air chain to TP13': ('ent_1936e05712944165aeb9', 'ent_676c063beff246908ca0'),     # compressor 2A -> UEF-13 inlet
    'DFDS-2 water chain to TP13': ('ent_afdfc43f0f1148d0b555', 'ent_676c063beff246908ca0'),   # pump 2A -> UEF-13 inlet
}
NEG = {
    'air must not reach UEF-1 water main': ('ent_081c34835a684544a6d0', 'ent_3e6f0c75149b49cdbce2'),
    'DFDS-1 pump must not reach DFDS-2 inlet': ('ent_975edb9acc07451cbc62', 'ent_676c063beff246908ca0'),
    'DFDS-2 compressor must not reach UEF-1 air main': ('ent_1936e05712944165aeb9', 'ent_21a02d1f40f04686a18a'),
}


def main():
    with sqlite3.connect((ROOT / 'data/plant/plant.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('BEGIN')
        m = Store.__new__(Store).model(db=db)
        integ = db.execute('PRAGMA integrity_check').fetchall()
        fk = db.execute('PRAGMA foreign_key_check').fetchall()
    base = json.loads((OUT / 'accepted-v628.json').read_text(encoding='utf8'))['model']
    facts = {a['id']: a for a in m['assertions']}
    assert all(facts[a['id']] == a for a in base['assertions'] if a['id'] in facts) and \
        all(a['id'] in facts for a in base['assertions']), 'prior assertion changed or vanished'
    assert m['merges'] == base['merges'] and m['conflicts'] == base['conflicts']
    als = {a['id']: a for a in m['aliases']}
    assert all(als[a['id']] == a for a in base['aliases'])
    adj = {}
    for a in m['assertions']:
        if a['predicate'] == 'utility_supply_to' and not a.get('retirement') and a.get('canonical_object'):
            adj.setdefault(a['canonical_subject'], set()).add(a['canonical_object'])

    def reaches(s, t):
        seen, q = set(), [s]
        while q:
            n = q.pop()
            if n == t:
                return True
            if n in seen:
                continue
            seen.add(n)
            q.extend(adj.get(n, set()) - seen)
        return False
    res = {'version': m['version'], 'integrity': [tuple(r) for r in integ], 'fk_errors': len(fk), 'positive': {}, 'negative': {}}
    for k, (s, t) in CHAINS.items():
        res['positive'][k] = reaches(s, t)
    for k, (s, t) in NEG.items():
        res['negative'][k] = not reaches(s, t)
    added = [a for a in m['assertions'] if a['created_version'] > 628]
    res['added'] = [(a['created_version'], a['predicate'], a['canonical_subject'], a.get('canonical_object')) for a in added]
    res['no_new_entities'] = not [e for e in m['entities'] if e['created_version'] > 628]
    print(json.dumps(res, indent=1))
    assert res['integrity'] == [('ok',)] and not fk and all(res['positive'].values()) and all(res['negative'].values()) and res['no_new_entities']
    (OUT / f'headers-verification-v{m["version"]}.json').write_text(json.dumps(res, indent=2), encoding='utf8')


if __name__ == '__main__':
    main()
