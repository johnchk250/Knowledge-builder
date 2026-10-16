"""Source-reviewed Yard3 Tier1 area and conveyor packages. Never replay acceptance."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = {'area': 'doc_4f2cd96c3b1e413ea4b5', 'eleven': 'doc_9d6657d14f3a4c829469',
        'twelve': 'doc_0adf08e6189847b88503'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scope', choices=DOCS)
    ap.add_argument('--baseline', required=True)
    args = ap.parse_args()
    model = json.loads((ROOT/args.baseline).read_text(encoding='utf8'))
    snap = json.loads((ROOT/'output/plant-enrichment/B14/accepted-v661.json').read_text(encoding='utf8'))
    labels = {e['label']: e['canonical_id'] for e in model['entities']}
    active = [a for a in model['assertions'] if not a['retirement'] and not a['suppressed']]
    doc = DOCS[args.scope]
    evs = [e for e in snap['evidence'] if e['document_id'] == doc]
    ev = {e['page']: e['id'] for e in evs}
    area = args.scope == 'area'; eleven = args.scope == 'eleven'
    basis = ('Coal flow175001 Rev8 p55; descriptive Yard3 grouping, not a field tag.' if area else
             ('175021 Rev2 approved29-Oct-2018' if eleven else '175022 Rev2 approved26-Nov-2018')+' conveyor GA; design, not field verification.')
    default_page = 55 if area else 5
    region = [.25,.48,.82,.58] if area else [.777,.045,.96,.815]
    ops, nodes = [], []

    def proof(p, r):
        return dict(origin='explicit', confidence=.98, evidence=[dict(evidence_id=ev[p],quote='',region=r)])

    def fact(s,p,v,page=default_page,r=region,obj=False,net=None,condition=None):
        ctx = dict(kind='classification' if p=='instance_of' else 'specification',basis=basis)
        if net: ctx.update(kind='connection',network=net,verification='documented',condition=condition)
        ops.append(dict(op='assert',subject=s,predicate=p,**{('object_entity' if obj else 'value'):v},context=ctx,**proof(page,r)))

    def new(key,label,typ,owner):
        assert label not in labels,label
        id='tmp_b20_'+args.scope+'_'+key
        ops.append(dict(op='entity',id=id,label=label,**proof(default_page,region)))
        fact(id,'instance_of',typ);fact(id,'part_of',owner,obj=True);nodes.append(id)
        return id

    def retire(a,why,page=default_page,r=region):
        ops.append(dict(op='retire',assertion_id=a['id'],reason=why,**proof(page,r)))

    if area:
        yard=new('yard','Coal Yard 3','functional_area',labels['Coal Stockpile Yard'])
        fact(yard,'equipment_role','Stack, store and reclaim through EAC11, EAD3, EAE3, EAF3 and EBA12; existing numbered identities reused.')
        fact(yard,'location_description','EAE3/UEB3 branch between TP4 stacking inlet and TP9 reclaim outlet; UAX3 drive house and UAX7 tail house.')
        for label in ['EAC-11','EAD-3','EAE-3','EAF-3','EBA-12','UEB-3','UAX-3','UAX-7']:
            id=labels[label]
            for a in active:
                if a['canonical_subject']==id and a['predicate']=='part_of':retire(a,'Replace aggregate ownership with descriptive Yard3 membership; original identities and physical route retained.')
            fact(id,'part_of',yard,obj=True)
        for label in ['UEF-4','UEF-9']:fact(yard,'associated_with',labels[label],obj=True)
        for label,desc in [('UAX-3','Drive/head end house of EAC11; a place, not a coal destination.'),('UAX-7','Tail/take-up end house of EBA12.'),('UEB-3','Cover shed over EAE3 stockpile; source geometry is design context, not surveyed coordinates.')]:fact(labels[label],'location_description',desc)
        gaps=['Control evidence inventory screened for scope; original coal-flowp55 reviewed. Other control pages excluded from new claims, not exhaustively rereviewed. Continuous EAC-8B-to-EAC-11 fixed-tripper diversion at UEF-4 and EBA-12-to-FG-8 outlet at UEF-9 preserved. Machine assemblies B21 and local utilities B22.']
    else:
        tag='EAC-11' if eleven else 'EBA-12';owner=labels[tag]
        head=labels['UAX-3' if eleven else 'UEF-9'];tail=labels['UEF-4' if eleven else 'UAX-7']
        specs=[
            ('motor','main drive motor','electric_motor',f'BHEL {680 if eleven else 270}kW,1488rpm,3.3kV three-phase motor. Voltage is not a traced feeder connection.'),
            ('fluid','scoop fluid coupling','fluid_coupling','Premium '+('PST-660' if eleven else 'PST-530')+' scoop coupling.'),
            ('gear','main gearbox','gearbox','Bevel-helical '+('B3-560,20.9:1' if eleven else 'B3-355,23.2:1 (schedule prints23.2:1; existing23.21 retained as minor rounding qualification)')+'.'),
            ('low','low-speed coupling','coupling','GBM geared '+('RG-12' if eleven else 'RG-10')+' coupling.'),
            ('brake','service thruster brake','thruster_drum_brake','Elektromag '+('EBTM500 DS/I' if eleven else 'EBTM500')+' schedule selection; detailed setting/calculation reconciliation deferred.'),
            ('head','head drive pulley','pulley',('1000mm' if eleven else '800mm')+' diameter drive pulley;12mm diamond-groove lagging. Detailed dimension reconciliation remains separate.'),
            ('belt','conveyor belting','conveyor_belt',('2000mm ST1000 with rip protection, FR8/6mm covers,1850m endless length.' if eleven else '1400mm N/N HD1250/4,FR5/2mm covers,1820m endless length.')),
            ('tail','tail and snub pulley group','functional_assembly',('800mm tail and bend pulleys,630mm snub,219mm deflector/hold-down rollers.' if eleven else '630mm tail/snubbing arrangement;219mm deflector/hold-down rollers.')),
            ('takeup','horizontal gravity take-up assembly','take_up_assembly',('Head-end HGTU at UAX3;3300mm trolley travel,17000kg design counterweight,800mm take-up pulley.' if eleven else 'Tail-end HGTU at UAX7;23000mm trolley travel,21000kg design counterweight,630mm take-up pulley.')),
            ('idlers','idler and belt-support assembly','functional_assembly','Carrying,transition,self-aligning and return idler groups with deck/guard support; row-level BOM deferred.'),
            ('cleaners','head and tail belt-cleaner group','functional_assembly','Spring-loaded primary/secondary external scraper at discharge and internal V-plough near tail. Schedule quantity1 wording retained; individual cleaner row reconciliation deferred.'),
            ('protection','PCS BSS and ZSS protection group','functional_assembly',f'BSS {18 if eleven else 17} pairs on both sides at50m; PCS schedule quantity{30 if eleven else 31} on both sides at30m does not explicitly state pairs; one tail ZSS. No individual PCS count or settings inferred.'),
        ]
        if not eleven:specs.append(('weigher','load-cell belt weigher','belt_weigher','One1400mm load-cell weigher near discharge gallery. Original GA175022p5 schedule prints accuracy (+/-)25% at20–120% load (apparent missing decimal/typo versus2% on peer GA175020 and0.25% in earlier summary); discrepancy explicitly qualified.'))
        parts={}
        for key,name,typ,desc in specs:
            id=new(key,tag+' '+name,typ,owner);parts[key]=id;fact(id,'assembly_arrangement',desc)
            if key in ['motor','fluid','gear','low','brake','head','weigher']:fact(id,'located_at',head,1,[.07,.32,.49,.69],True)
            if key=='tail':fact(id,'located_at',tail,4,[.66,.12,.93,.59],True)
            if key=='takeup':fact(id,'located_at',labels['UAX-3' if eleven else 'UAX-7'],5,[.055,.065,.57,.43],True)
        for a,b in zip(['motor','fluid','gear','low','head'],['fluid','gear','low','head','belt']):fact(parts[a],'mechanically_drives',parts[b],obj=True,net='mechanical',condition='Documented head drive arrangement.')
        if not eleven:fact(parts['weigher'],'monitors_equipment',owner,obj=True)
        for a in active:
            if a['canonical_subject']!=owner:continue
            if not eleven and a['predicate']=='document_note' and '0.25%' in str(a['value']):
                retire(a,'Original weigher schedule prints(+/-)25% (qualified against2% on peer GA175020 and prior0.25% transcription); PCS count-unit remains qualified.');fact(owner,'document_note','Protection and weigher detail now on own assemblies. GA175022p5 prints17BSS pairs,PCS quantity31 without explicit pair-unit,tailZSS1 and load-cell weigher accuracy(+/-)25% at20–120% load (qualified against peer2% and prior0.25% transcription).')
        if eleven:fact(owner,'document_note','GA11 detailed schedule says UEF4-toUAX3; sheet1 copied UAX1/UEF6 notes do not override its numbered key plan. Head pulley table/detail face wording and existing coasting-calculation1400mm width versus GA2000mm remain review qualifications.')
        gaps=['All five GA sheets visually reviewed and appended review replies read. Headline ratings and exact material routes reused. Vendor internals,PCS count-unit,brake settings and detailed civil/access/BOM deferred.']
    out=ROOT/'output/plant-enrichment/B20'/args.scope;out.mkdir(parents=True,exist_ok=True)
    assert not (out/'accepted/commit-log.json').exists()
    (out/'baseline-model.json').write_text(json.dumps(model),encoding='utf8')
    pkg=dict(document_id=doc,baseline_version=model['version'],baseline_model=(out/'baseline-model.json').relative_to(ROOT).as_posix(),expected_new_components=len(nodes),visual_ids=[e['id'] for e in evs if (e['page']==55 if area else e['page']<=5)],body=dict(summary='B20 Yard3 Tier1 '+args.scope,operations=ops,intake_assessment=dict(route='mixed',purpose='Major Yard3 conveyor assemblies and source-specific place structure',questions=['Which major assemblies and exact places are supported?'],reviewed_evidence_ids=[e['id'] for e in evs],gaps=gaps)))
    (out/'package.json').write_text(json.dumps(pkg,indent=2)+'
',encoding='utf8')
    print(dict(scope=args.scope,components=len(nodes),operations=len(ops),baseline=model['version']))


if __name__=='__main__':main()
