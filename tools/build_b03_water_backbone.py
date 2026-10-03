"""Build reviewed Pass-A water networks; never replay an accepted package."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/plant-enrichment/B03/water-175091'
DOC = 'doc_e17edf6897d746fabe12'

def main():
    model = json.loads((ROOT/'output/plant-enrichment/B03/accepted-v631.json').read_text(encoding='utf8'))['model']
    assert model['version'] == 631
    entities = {e['id']: e for e in model['entities']}
    def canonical(e): return entities[e]['canonical_id']
    def label(name):
        matches = {e['canonical_id'] for e in entities.values() if e['label'] == name}
        assert len(matches) == 1, (name, matches)
        return matches.pop()
    evs = json.loads((ROOT/f'output/plant-enrichment/B03/review/{DOC}-evidence.json').read_text(encoding='utf8'))
    page_ids = {13:'ev_dda36d1f97fe4d4cba8b',14:'ev_da322de8e7ca4a9bac11',15:'ev_a179ac4ae9454cedb364'}
    ops=[]
    def proof(page, region):
        return dict(origin='explicit', confidence=.97, evidence=[dict(evidence_id=page_ids[page],quote='',region=region)])
    def fact(s,p,v,page,r,obj=False,condition=None):
        context=dict(kind='classification' if p=='instance_of' else 'specification',basis=f'175091 Rev3 embedded original PDF p{page} in approved control philosophy175319 Rev5. Design arrangement; source-specific pump naming and ratings retained.')
        if p=='utility_supply_to': context.update(kind='connection',network='utility',verification='documented',condition=condition)
        ops.append(dict(op='assert',subject=s,predicate=p,**{('object_entity' if obj else 'value'):v},context=context,**proof(page,r)))
    def edge(s,t,page,r,condition):fact(s,'utility_supply_to',t,page,r,True,condition)
    specs=[
        ('SW1',13,'ent_3cbea88a25d5426b882b','ent_bdf8e7e7f7f8485b80fe','ent_568564ff3bd948438f86',['ent_58b7e7c3998e4d98b5d7','ent_2c87676b95944bf9b134'],[.055,.23,.35,.45],['UEF-1','UEE-1','UEF-3','UEF-4','UEF-5','UEF-6','UEF-7'],[.54,.57,.79,.86]),
        ('SW2',14,'ent_b613a544197645ebbcda','ent_36135b45a07c4d03bf06','ent_dbe58a4eb9a74ed6b0c4',['ent_bef111efde0840029c77','ent_105687fe8f1b449ea92b'],[.63,.14,.90,.32],['UEE-2','UEE-3','UEF-13','UEF-12','UEF-11','UEF-10','UEF-9','UEF-8'],[.14,.57,.34,.82]),
        ('PW',15,'ent_205d8809dce044069d51','ent_36135b45a07c4d03bf06','ent_dbe58a4eb9a74ed6b0c4',['ent_a408ea3a3ca04f2899b6','ent_6380321730824a9a8be8'],[.55,.50,.78,.69],['UEF-1','UEE-1','UEF-3','UEF-4','UEF-5','UEF-6','UEF-7','UEE-2','UEE-3','UEF-13','UEF-12','UEF-11','UEF-10','UEF-9','UEF-8'],[.79,.35,.94,.725]),
    ]
    for key,page,system,house,tank,pumps,r,consumers,table in specs:
        system,house,tank=map(canonical,[system,house,tank])
        filt,header='tmp_b03_'+key+'_filter','tmp_b03_'+key+'_header'
        for id,name,typ in [(filt,f'{key} Common DUP-01 duplex suction filter','duplex_filter'),(header,f'{key} Common distribution header','utility_header')]:
            ops.append(dict(op='entity',id=id,label=name,**proof(page,r)))
            fact(id,'instance_of',typ,page,r)
            fact(id,'part_of',system,page,r,True)
            if id==filt:fact(id,'located_at',house,page,r,True)
        edge(tank,filt,page,r,'Dedicated system takeoff from the common RCC tank outline; no connection between service and potable compartments implied.')
        for pump in pumps:
            edge(filt,canonical(pump),page,r,'Filtered suction branch. Two-pump one-working/one-standby design; no present duty selection asserted.')
            edge(canonical(pump),header,page,r,'Non-return/isolation discharge branch to common distribution outlet D. Recirculation is distinct from consumer supply.')
        for consumer in consumers:
            edge(header,label(consumer),page,table,('Potable-water roof-storage/tap' if key=='PW' else 'Service-water hose/tap')+' application boundary in source consumption schedule. Local branches and physical routing remain source-specific; no coal-flow relationship.')
        fact(header,'assembly_arrangement',('Potable storage and tap distribution serves the listed CHP buildings; schedule PWP-1A/B and control PWP-2A/B are already reconciled by identical KKS. ' if key=='PW' else 'Service-water distribution serves the listed CHP buildings and connecting galleries. ')+'Individual hose boxes, taps, valves, pipe supports and detailed recirculation components are deferred to Pass B; source schedule is not simultaneous consumption.',page,table)
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'accepted/commit-log.json').exists()
    (OUT/'baseline-model.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf8')
    package=dict(document_id=DOC,baseline_version=631,baseline_model='output/plant-enrichment/B03/water-175091/baseline-model.json',expected_new_components=6,visual_ids=list(page_ids.values()),body=dict(summary='B03 Tier1: three independent SW1/SW2/PW tank-filter-pump-header networks and thirty CHP building consumer boundaries',operations=ops,intake_assessment=dict(route='mixed',purpose='Trace common water sources to main CHP consumers',questions=['Which common pumps and headers serve each CHP building?'],reviewed_evidence_ids=[e['id'] for e in evs],gaps=['Document evidence inventoried and text reviewed for scope: control pp1-10 retains prior B01 qualifications; DFDS pp11-12 reuses B02; SPDS p16 reuses separate175255; makeup/runoff p17 belongs B04; LHP p18 is outside CHP consumer detail. Only pp13-15 original drawings are the visual basis of this package.','175091 is present as embedded drawings in this source; previous standalone-title search was not evidence that the drawing was unavailable.','Pass B: detailed AP/SC/SV mappings, control tables, recirculation assemblies, hose boxes, roof tanks, all gallery branches, LHP interfaces and source-rating reconciliation. Existing claims retained.'])))
    (OUT/'package.json').write_text(json.dumps(package,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(components=6,operations=len(ops),consumers=sum(len(s[7]) for s in specs))))

if __name__=='__main__':main()
