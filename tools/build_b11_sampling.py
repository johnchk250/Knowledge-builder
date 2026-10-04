"""Source-reviewed sampling1 breadth packages; never applies changes itself."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scope', choices=['ga', 'control'])
    ap.add_argument('--baseline', required=True)
    args = ap.parse_args()
    m = json.loads((ROOT / args.baseline).read_text(encoding='utf8'))
    labels = {e['label']: e['canonical_id'] for e in m['entities']}
    system, house = labels['UEF-3 Coal Sampling System'], labels['UEF-3']
    ga = args.scope == 'ga'
    doc = 'doc_404c8747ba8047ab8f12' if ga else 'doc_4f2cd96c3b1e413ea4b5'
    evs = json.loads((ROOT / ('output/plant-enrichment/B11/review/evidence.json' if ga else 'output/plant-enrichment/B11/review/control-evidence.json')).read_text(encoding='utf8'))
    ev = {e['page']: e['id'] for e in evs}
    ops, nodes = [], []
    basis = '175072 Rev1 sampling GA, approved07-Jan-2019; design, not field verification.' if ga else '175001 control write-up Rev04,26-Mar-2020,AOC06-Apr-2020; design, not live state.'

    def proof(page, region=None):
        if not ga:
            return dict(origin='explicit', confidence=.98, evidence=[dict(evidence_id=ev[n], quote='', region=[.16,.21,.88,.94 if n != 21 else .76]) for n in dict.fromkeys([page,19,20,21])])
        return dict(origin='explicit', confidence=.98, evidence=[dict(evidence_id=ev[page], quote='', **({'region': region} if region else {}))])

    def fact(s, p, value, page=1, region=None, obj=False, net=None, condition=None):
        ctx = dict(kind='classification' if p == 'instance_of' else 'specification', basis=basis)
        if net:
            ctx.update(kind='connection', network=net, verification='documented', condition=condition)
        ops.append(dict(op='assert', subject=s, predicate=p, **{('object_entity' if obj else 'value'): value}, context=ctx, **proof(page, region)))

    def new(key, name, owner, page, region=None, typ='functional_assembly'):
        assert name not in labels
        id = 'tmp_b11_' + key
        ops.append(dict(op='entity', id=id, label=name, **proof(page, region)))
        fact(id, 'instance_of', typ, page, region)
        fact(id, 'part_of', owner, page, region, True)
        fact(id, 'located_at', house, page, region, True)
        nodes.append(id)
        return id

    def unit(name):
        return labels['EAU-1 ' + name]

    if ga:
        # Existing EAU-1 components already belong to this system: no parallel identity.
        fact(system, 'located_at', house, 1, [.07,.10,.69,.57], True)
        for a in m['assertions']:
            if a['canonical_subject'] == system and a['predicate'] == 'part_of' and a['canonical_object'] == 'ent_47917398ad6c4e0aac58' and not a['retirement']:
                ops.append(dict(op='retire', assertion_id=a['id'], reason='175072 locates the sampling system at UEF3; retain existing immediate UEF3 owner, remove redundant plant-level owner.', **proof(1, [.07,.10,.69,.57])))
        rows = [
            ('Primary Sampler-1',8,'geared brake drive','15kW geared brake motor; approximate output44rpm. GA differs from existing control20 motor30kW; neither is claimed field-confirmed.',[.77,.32,.97,.54]),
            ('Primary Sampler-2',8,'geared brake drive','15kW geared brake motor; approximate output44rpm. GA differs from existing control20 motor30kW; neither is claimed field-confirmed.',[.77,.32,.97,.54]),
            ('Reversible Belt Feeder',3,'reversible geared drive','2.2kW geared motor without brake;1440rpm motor,approximately10rpm output;415V.',[.78,.36,.96,.56]),
            ('Hammer Crusher',4,'drive motor','18.5kW,approximately1440rpm,415V motor; V-belt drive. Existing control20 says45kW; unresolved source difference.',[.70,.03,.96,.31]),
            ('Secondary Sampler',6,'geared brake drive','0.37kW,1440rpm motor,approximately15rpm output;415V geared motor with brake. Existing control21 says2.2kW; unresolved.',[.64,.34,.96,.61]),
            ('Rotary Sample Collector',5,'geared brake drive','0.37kW,approximately1.1rpm output;415V geared brake motor. Existing control21 says2.2kW; unresolved.',[.69,.05,.96,.32]),
            ('Reject Screw Conveyor',7,'geared drive','2.2kW geared motor without brake;approximately29rpm output,415V. Existing control21 says7.5kW; unresolved.',[.03,.75,.26,.97]),
            ('Reject Slide Gate',1,'linear electric actuator','System drive schedule specifies0.25kW linear actuator. Screw GA p7 lists0.25/0.55kW alternatives; control21 says1.1kW. Final rating unresolved.',[.035,.60,.26,.815]),
        ]
        for i,(name,page,suffix,description,region) in enumerate(rows):
            owner=unit(name)
            id=new('drive'+str(i),'EAU-1 '+name+' '+suffix,owner,page,region, 'electric_motor' if name=='Hammer Crusher' else 'functional_assembly')
            fact(id,'assembly_arrangement',description,page,region)
            fact(id,'mechanically_drives',owner,page,region,True,'mechanical','GA drive of this sample-handling unit; source rating disagreements remain qualified.')
        groups = [
            ('Primary Sampler-1',8,'cutter hood and support assembly','Swing-arm cutter300mm opening across2000mm EAC3A belt; hood,discharge,skirt/frame,5-roll support and mechanical backstop. Two proximity switches shown per primary sampler.',[.04,.035,.98,.56]),
            ('Primary Sampler-2',8,'cutter hood and support assembly','Swing-arm cutter300mm opening across2000mm EAC3B belt; hood,discharge,skirt/frame,5-roll support and mechanical backstop. Two proximity switches shown per primary sampler.',[.04,.035,.98,.56]),
            ('Reversible Belt Feeder',3,'belt pulley take-up and enclosure assembly','500mm reversible belt,approx8780mm pulley centres,9.5m/min;5100kg/h design capacity. Head/tail pulleys,screw take-up300mm,external/internal cleaners,covered skirt and inlet flow-control plates. Proximity feedback shown.',[.035,.04,.97,.57]),
            ('Hammer Crusher',4,'hammer mill and guarded belt transmission','Jeffrey MME hammer mill with breaker plate; motor,V-belts,pulleys and guard.5100kg/h;100mm maximum feed,95% minus8mesh and100% minus4mesh approximate product; proximity switch shown.',[.03,.03,.97,.34]),
            ('Secondary Sampler',6,'rotary cutter and outlet housing','45mm cutter opening; enclosed rotary plate/cutter with separate sample and reject outlets and proximity feedback. No continuous full-flow sample collection assumed.',[.05,.045,.96,.61]),
            ('Rotary Sample Collector',5,'four-station bottle bank','Four40L collection containers,rotary frame/cover and shaft; two proximity switches. Containers are collected manually under existing control requirement.',[.04,.04,.96,.66]),
            ('Reject Screw Conveyor',7,'screw trough and two-outlet assembly','Approx7245mm trough,230mm diameter/pitch,29rpm; covered trough with inspection access,two outlets and one slide gate. Equipment page7 rates3000kg/h while system page1 rates5100kg/h; capacity discrepancy retained.',[.03,.03,.78,.97]),
        ]
        for i,(name,page,suffix,desc,region) in enumerate(groups):
            id=new('body'+str(i),'EAU-1 '+name+' '+suffix,unit(name),page,region)
            fact(id,'assembly_arrangement',desc,page,region)
        for name,desc in [('Primary Sampler-1','Samples EAC3A only;3400TPH main conveyor basis,2000mm belt,300mm cutter opening.'),('Primary Sampler-2','Samples EAC3B only;3400TPH main conveyor basis,2000mm belt,300mm cutter opening.'),('Reversible Belt Feeder','5100kg/h,500mm belt,9.5m/min,8780mm approximate centres; forward sample preparation or reverse bias collection.'),('Hammer Crusher','5100kg/h sample hammer mill;100mm maximum feed;95% minus8mesh and100% minus4mesh approximate product.'),('Secondary Sampler','45mm cutter opening; approximately15rpm selected output.'),('Rotary Sample Collector','Four40L containers; approximately1.1rpm output.'),('Reject Screw Conveyor','System GA5100kg/h versus equipment GA3000kg/h remains unresolved; approx7245mm trough.')]:
            fact(unit(name),'assembly_arrangement',desc,1,[.81,.225,.975,.79])
        connections=[
            ('Primary Sampler-1','Reversible Belt Feeder','primary1 sample chute','Sample cut from EAC3A only.'),
            ('Primary Sampler-2','Reversible Belt Feeder','primary2 sample chute','Sample cut from EAC3B only.'),
            ('Reversible Belt Feeder','Hammer Crusher','forward feeder discharge chute','Normal forward sampling; bias reverse is a separate mode.'),
            ('Reversible Belt Feeder','Bias Sample Bin','reverse bias discharge chute','Bias mode only: reversed feeder; downstream preparation units stopped.'),
            ('Hammer Crusher','Secondary Sampler','crushed sample chute','Normal preparation branch.'),
            ('Secondary Sampler','Rotary Sample Collector','final sample chute','Selected sample portion only; manual final collection.'),
            ('Secondary Sampler','Reject Screw Conveyor','reject inlet chute','Rejected sample portion only.'),
        ]
        for i,(src,dst,name,condition) in enumerate(connections):
            id=new('chute'+str(i),'EAU-1 '+name,system,1,[.09,.11,.31,.46],'chute_interface')
            fact(unit(src),'material_flow_to',id,1,[.09,.11,.31,.46],True,'material',condition)
            fact(id,'material_flow_to',unit(dst),1,[.09,.11,.31,.46],True,'material',condition)
        # Both return chutes are shown on the GA. State-to-lane mapping comes from control p20.
        for lane,region in [('A',[.15,.33,.20,.46]),('B',[.21,.33,.26,.46])]:
            id=new('return'+lane,'EAU-1 reject return chute to EAC-4'+lane,unit('Reject Screw Conveyor'),1,region,'chute_interface')
            fact(id,'material_flow_to',labels['EAC-4'+lane],1,region,True,'material','Selected reject return only; slide-gate condition separately sourced from control20.')
        fact(system,'document_note','GA drive ratings differ from later control motor schedule for primary samplers,crusher,secondary sampler,collector,screw and slide gate. GA p7 also differs from system p1 for screw capacity. Existing ratings retained; no field selection inferred.',1,[.035,.60,.26,.815])
        gaps=['All eight principal system/equipment GA pages visually reviewed at maintainable assembly level; replies pp9-11 read. No internals/BOM fasteners expanded.','GA p10 rejects feeder BSS and uses proximity zero-speed; later control20 calls for both BSS and ZSS. Preserve both requirements; final configuration unresolved.','GA p11 confirms one selector slide gate despite requested two. Existing single canonical gate retained. Common DFDS and drainage/hoist service remains at UEF3, no unsupported sampler-specific nozzle or utility consumer invented.']
    else:
        id=new('controls','EAU-1 PLC protection and local control group',system,19)
        fact(id,'assembly_arrangement','Dedicated sampling PLC; CHP DCS start/stop and CSU/cutter status; local equipment pushbuttons. Primary cutter parking/stuck protection trips its preceding conveyor; feeder VVVF,ZSS/BSS; crusher ZSS; secondary/collector proximity and slide-gate end limits. Numeric timers and detailed clauses deferred.',19)
        fact(id,'document_note','Control20/21 requirements and motor schedule differ from175072 GA. GA replyp10 says feeder BSS not required; control20 specifies BSS. Control21 return labels EAC3A/3B and2B conflict with explicit system path on control20 and GA to EAC4A/B; no return to upstream3 belts added.',20)
        for lane,state in [('A','closed'),('B','open')]:
            fact(unit('Reject Slide Gate'),'material_flow_to',labels['EAU-1 reject return chute to EAC-4'+lane],20,obj=True,net='material',condition=f'Slide gate {state}: reject to EAC4{lane} per explicit CSU1 operational paragraphp20 and GA. Control21 endpoint labels conflict; no live interlock or state inferred.')
        fact(system,'document_note','Reject return modeled to EAC4A with gate closed and EAC4B with gate open, following control20 and corroborating175072 GA. Control21 EAC3/2B labels remain unresolved; detailed interlock association is not promoted.',20)
        for name,page,desc in [('Primary Sampler-1',20,'PLC parking/limit feedback and brake; cutter stuck/fall protection for its EAC3A belt.'),('Primary Sampler-2',20,'PLC parking/limit feedback and brake; cutter stuck/fall protection for its EAC3B belt.'),('Reversible Belt Feeder',20,'VVVF,zero-speed and belt-sway requirements; BSS disputed by earlier GA replyp10.'),('Hammer Crusher',20,'Zero-speed protection; sample crusher only.'),('Secondary Sampler',21,'Proximity/PLC intermittent sampling.'),('Rotary Sample Collector',21,'Proximity/PLC positioning and brake motor.'),('Reject Slide Gate',21,'Two end-limit switches; source endpoint label disagreement retained.')]:
            fact(id,'controls',unit(name),page,obj=True,net='control',condition=desc)
        gaps=['Control19-21 read for sampling1 only; whole evidence inventory reconciles previous accepted control review. Other pages unchanged.','Motor/BSS disagreements and control21 return/interlock labels retained; detailed timers/settings deferred. Bias and sample paths already accepted are retained.']
    out=ROOT/'output/plant-enrichment/B11'/args.scope
    out.mkdir(parents=True,exist_ok=True)
    assert not (out/'accepted/commit-log.json').exists()
    (out/'baseline-model.json').write_text(json.dumps(m),encoding='utf8')
    pkg=dict(document_id=doc,baseline_version=m['version'],baseline_model=str((out/'baseline-model.json').relative_to(ROOT)),expected_new_components=len(nodes),visual_ids=[e['id'] for e in evs],body=dict(summary='B11 sampling1 '+args.scope+' major assemblies and qualified sample/bias/reject paths',operations=ops,intake_assessment=dict(route='mixed',purpose='Tier1 sampling1; preserve source disagreements and existing identities',questions=['Which major assemblies and conditional routes belong to sampling1?'],reviewed_evidence_ids=[e['id'] for e in evs],gaps=gaps)))
    (out/'package.json').write_text(json.dumps(pkg,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(scope=args.scope,components=len(nodes),operations=len(ops),baseline=m['version'])))


if __name__ == '__main__':
    main()

