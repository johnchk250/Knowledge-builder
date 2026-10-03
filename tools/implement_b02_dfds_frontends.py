"""One-time reviewed DFDS station front ends from v620; rehearse before apply."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chp.store import Store
from chp.reviewed_ingestion import stage
from chp.patches import validate, commit
from tools.implement_b00_corrections import save, support

BASE = ROOT / 'output/plant-enrichment/B02/frontends'
DOC = 'doc_bca09d68af9b43e3b633'
STATIONS = [
    dict(n=1, system='ent_2024dfa4a4084a86b0b5', house='ent_bdf8e7e7f7f8485b80fe',
         tank='ent_568564ff3bd948438f86', pumps=['ent_975edb9acc07451cbc62', 'ent_8a35251f220d4c9287d2'],
         compressors=['ent_081c34835a684544a6d0', 'ent_2fc625b1e93743ae9e7f'],
         dps='ent_f29313786c2242e89aed', eid='ev_08ec0122d044468d8975',
         region=[.03,.20,.37,.46], receiver_capacity=2.0, air_nb=80),
    dict(n=2, system='ent_b2f48e8d116f484882a1', house='ent_36135b45a07c4d03bf06',
         tank='ent_1aceca34e2644238a03e', pumps=['ent_afdfc43f0f1148d0b555', 'ent_eca52aa5ec3d4d3fa153'],
         compressors=['ent_1936e05712944165aeb9', 'ent_b5dfed25a0c84bb1a91a'],
         dps='ent_c3e2e10247594533af74', eid='ev_d705803b38ce46ccb5fa',
         region=[.63,.04,.985,.32], receiver_capacity=1.7, air_nb=100),
]


def packages(snap):
    result=[]
    for station in STATIONS:
        n=station['n']; eid=station['eid']; region=station['region']; ops=[]
        proof=support(eid,region)
        basis=f'Original175089 Rev1 PDF p{n}, approved14-Dec-2018: visually traced station arrows and legend. Design arrangement, not live valve state or complete isolation.'
        def fact(subject,predicate,value,relation=False,kind='specification',extra=None):
            context={'kind':kind if kind in ('classification','connection') else 'specification','basis':basis}
            for key,item in (extra or {}).items():
                if key in ('network','verification','condition','from_port','to_port','basis'):
                    context[key]=item
                else:
                    context['basis']+=' '+key+': '+str(item)+'.'
            op={'op':'assert','subject':subject,'predicate':predicate,
                'object_entity' if relation else 'value':value,
                'context':context,**proof}
            ops.append(op)
        def node(key,label,cls,owner,role=None):
            temp=f'tmp_s{n}_{key}'
            ops.append({'op':'entity','id':temp,'label':f'DFDS-{n} {label}',**proof})
            fact(temp,'instance_of',cls,kind='classification')
            fact(temp,'part_of',owner,True,kind='assembly')
            fact(temp,'located_at',station['house'],True,kind='location')
            if role:fact(temp,'equipment_role',role)
            return temp
        def link(a,b,medium,detail):
            fact(a,'utility_supply_to',b,True,kind='connection',extra={
                'network':'utility','verification':'documented','medium':medium,
                'mode':'source-documented possible flow path; duty/standby symbols are design illustration',
                'basis':basis+' '+detail})
        if n==1:
            for key,definition in [('non_return_valve','One-way non-return/check valve identified by the source legend; not a positive isolation boundary.'),
                                   ('ball_valve','Ball valve identified by the source legend and individual BV tag.')]:
                assert not any(o['key']==key for o in snap['model']['ontology'])
                ops.append({'op':'define','key':key,'kind':'entity_type','definition':definition,
                            'cardinality':'many','value_type':'string',**support(eid,[.435,.59,.634,.85])})
        water=node('water','Common water supply train','functional_assembly',station['system'],
                   f'Tank withdrawal through GAV01 and DUP01 splits to existing DFDSP-{n}A/B, rejoins at PointD, passes GLV01 and enters32NB water main. Return branch has GAV06/PRV01 and parallel GLV02 bypass to20NB tank-return line. Pump identities/ownership remain the existing shared system.')
        air=node('air','Common compressed-air supply train','functional_assembly',station['system'],
                 f'Existing DFDSC-{n}A/B discharge through BV01/BV02 to one common receiver, then BV03 to the{station["air_nb"]}NB air main. Moisture separator is inbuilt in compressor per source note9; no standalone dryer is drawn in this station region. Treatment/vendor detail remains further B02 review.')
        ops[-1]['evidence'].append({'evidence_id':eid,'quote':'','region':[.04,.78,.325,.97] if n==1 else [.34,.675,.596,.97]})
        gav1=node('gav01','GAV-01 common suction gate valve','gate_valve',water)
        dup=node('dup01','DUP-01 common suction duplex filter','duplex_filter',water,
                 'One common suction duplex filter precedes the split to both pumps. DUP01 and DPS01 are distinct filter and differential-pressure switch tags; the existing DPS record is reused.')
        gava=node('gav02','GAV-02 pump-A suction gate valve','gate_valve',water)
        gavb=node('gav04','GAV-04 pump-B suction gate valve','gate_valve',water)
        nrva=node('nrv01','NRV-01 pump-A discharge check valve','non_return_valve',water)
        nrvb=node('nrv02','NRV-02 pump-B discharge check valve','non_return_valve',water)
        outa=node('gav03','GAV-03 pump-A discharge gate valve','gate_valve',water)
        outb=node('gav05','GAV-05 pump-B discharge gate valve','gate_valve',water)
        pointd=node('pointd','Common water discharge manifold Point D','utility_header',water,
                    'PointD is the explicitly marked joined pump-discharge junction before GLV01 and the tank-return branch, not a separate pump or storage vessel.')
        glv1=node('glv01','GLV-01 common water outlet globe valve','globe_valve',water)
        wh=node('watermain','Common water main at station outlet','utility_header',water,
                '32NB(W) station outlet toward local DFDS applications. Detailed downstream branches/FAS/PRU applicability and local isolation remain B02 and consuming batches.')
        gav6=node('gav06','GAV-06 tank-return relief branch gate valve','gate_valve',water)
        prv=node('prv01','PRV-01 water relief-to-tank valve','pressure_relief_valve',water,
                 'Source legend defines PRV as pressure relief valve; return follows GAV06 toPRV01. No relief setting or commissioned pressure is stated in this drawing.')
        glv2=node('glv02','GLV-02 tank-return bypass globe valve','globe_valve',water,
                  'Parallel bypass around the GAV06/PRV01 relief branch joins the same20NB tank-return line. Source symbol depicts partially closed globe valve; no current opening fraction is known.')
        rec=node('return','20NB recirculation return to common tank','utility_header',water)
        bv1=node('bv01','BV-01 compressor-A discharge ball valve','ball_valve',air)
        bv2=node('bv02','BV-02 compressor-B discharge ball valve','ball_valve',air)
        receiver=node('receiver','Common air receiver','air_receiver',air,
                      'Common receiver accepts both compressor branches; PG, receiver safety relief and ADT drain are shown. Receiver accessory decomposition/ratings/vendor applicability remain B02; no inspection certification is inferred.')
        bv3=node('bv03','BV-03 common receiver outlet ball valve','ball_valve',air)
        ah=node('airmain','Common air main at receiver outlet','utility_header',air,
                f'{station["air_nb"]}NB(A) station outlet toward local DFDS applications. It is separate from32NB(W) main; crossing air/water lines are not cross-connections.')
        for obj,value in [(wh,32),(rec,20),(ah,station['air_nb'])]:
            fact(obj,'nominal_diameter',value,extra={'unit_basis':'NB annotation is nominal bore, not measured outside diameter'})
            ops[-1]['unit']='mm'
        fact(receiver,'volume_capacity',station['receiver_capacity'],extra={'rating_basis':f'CAP-{station["receiver_capacity"]:.1f}CUM source design annotation, not current stored air volume'})
        ops[-1]['unit']='m3'
        for obj in [gavb,outb,nrvb,station['pumps'][1]]:
            fact(obj,'operating_requirement','B pump branch is shown with closed/hatched gate-valve and pump symbols. It remains a documented possible standby connection; illustration does not establish current valve position, which pump is running, complete isolation or executable changeover logic.')
        fact(station['dps'],'monitors_equipment',dup,True,kind='connection',extra={'network':'control','verification':'documented','basis':basis+' DPS01 is drawn across the DUP01 filter; no differential-pressure setpoint or commissioned polarity added.'})
        fact(station['dps'],'located_at',station['house'],True,kind='location')
        tank_basis='Tank1 existing commonSWS/DFDS identity reused.' if n==1 else 'P&ID labels parentTank2; B01 accepted DFDS/LSDS/SWS compartment reused for service-specific withdrawal and return; noSPDS/potable cross-connection.'
        for a,b,detail in [(station['tank'],gav1,tank_basis),(gav1,dup,'common suction'),(dup,gava,'filter outlet split A'),(dup,gavb,'filter outlet split B'),
                           (gava,station['pumps'][0],'A pump suction'),(gavb,station['pumps'][1],'B pump suction'),
                           (station['pumps'][0],nrva,'A pump discharge'),(station['pumps'][1],nrvb,'B pump discharge'),
                           (nrva,outa,'A branch check then isolation'),(nrvb,outb,'B branch check then isolation'),
                           (outa,pointd,'A joins PointD'),(outb,pointd,'B joins PointD'),(pointd,glv1,'joined discharge to station outlet'),(glv1,wh,'32NB(W) outgoing main'),
                           (pointd,gav6,'water return branch from joined discharge'),(gav6,prv,'gate before pressure relief'),(prv,rec,'relief return line'),
                           (pointd,glv2,'parallel return bypass'),(glv2,rec,'bypass joins20NBreturn'),(rec,station['tank'],tank_basis+' Explicit arrows return towaterstorage tank.')]:
            link(a,b,'water',detail)
        for a,b,detail in [(station['compressors'][0],bv1,'compressorA outlet'),(station['compressors'][1],bv2,'compressorB outlet'),
                           (bv1,receiver,'A branch tocommon receiver'),(bv2,receiver,'B branch tocommon receiver'),(receiver,bv3,'common receiver outlet'),(bv3,ah,'air outlet main')]:
            link(a,b,'compressed air',detail)
        result.append({'document_id':DOC,'visual_ids':[eid], 'body':{
            'summary':f'B02: source-traced DFDS System{n} common water/air station front ends',
            'operations':ops,'intake_assessment':{
                'route':'mixed','purpose':'Implement source-supported common production front ends while reusing canonical pumps/compressors/tanks and retaining source-revision duties.',
                'questions':['Which physical common filter/valve/receiver paths are drawn?','Do air and water paths remain separate?','Does standby illustration differ from live isolation?'],
                'reviewed_evidence_ids':[e['id'] for e in snap['evidence'] if e['document_id']==DOC],
                'gaps':['Both original sheets/title/revision/approval/legends/notes and application regions visually inventoried; station regions enlarged and traced. Dense per-application lists/BOM and local FAS/PRU detailed extraction remain furtherB02/consuming batches.',
                        'Tank2 compartment identification is acceptedB01 source bridge, not an extra subdivision deduced from this schematic. Tank capacity/motor power refer toGAs/vendor sheets. No commissioning/live state, relief setpoint, installed certificate or complete isolation asserted.',
                        'Common motor/receiver safety-drain-gauge accessories, vendor treatment/maintenance and source-exact standby/pressure logic remain furtherB02 work.']}}})
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');args=p.parse_args()
    snap=json.loads((ROOT/'output/plant-enrichment/B01/accepted-v620.json').read_text(encoding='utf8'))
    pkgs=packages(snap);plant=ROOT/'data/plant';out=BASE/('accepted' if args.apply else 'rehearsal');out.mkdir(parents=True,exist_ok=True)
    assert not (out/'commit-log.json').exists(),'One-time builder; inspect partial state and resume verification, never replay.'
    with sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row;db.execute('BEGIN');before=Store.__new__(Store).model(db=db)
        assert before==snap['model'] and before['version']==620,'Live state changed; re-review required.'
        assert not db.execute("SELECT id FROM proposals WHERE status='pending'").fetchall()
        if not args.apply:
            backup=BASE/'backup-v620';backup.mkdir(exist_ok=True)
            for dest in [out/'plant.sqlite3',backup/'plant.sqlite3']:
                with sqlite3.connect(dest) as dst:db.backup(dst)
            doc=next(d for d in snap['documents'] if d['id']==DOC)
            assert hashlib.sha256((plant/'originals'/doc['sha256']).read_bytes()).hexdigest()==doc['sha256']
            paths={Path('originals')/doc['sha256']}|{Path('renders')/e['image'] for e in snap['evidence'] if e['document_id']==DOC and e['image']}
            for rel in paths:
                dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(plant/rel,dest)
            save(backup/'manifest.json',{'version':620,'scope':'Consistent full SQLite backup plus immutable reviewed DFDS original/render files.','copied_files':sorted(str(p) for p in paths)})
    if args.apply:
        assert pkgs==json.loads((BASE/'rehearsal/packages.json').read_text(encoding='utf8'))
        assert json.loads((BASE/'rehearsal/result.json').read_text(encoding='utf8'))['ok']
    save(out/'packages.json',pkgs);store=Store(plant if args.apply else out);logs=[]
    for i,pkg in enumerate(pkgs):
        body=pkg['body'];v=620+i
        report=validate(store,{k:body[k] for k in ['summary','operations']},DOC,v,visual_ids=pkg['visual_ids'])
        save(out/f'validation-v{v}.json',report);assert not report['errors'],report
        staged=stage(store,DOC,body,visual_ids=pkg['visual_ids'],analysis_dir=str(out),expected_version=v)
        accepted=commit(store,staged['proposal_id']);logs.append({'proposal_id':staged['proposal_id'],**accepted});save(out/'commit-log.json',logs)
    after=store.model();save(out/'model.json',after);verify(before,after,logs,out)


def verify(before,after,logs,out):
    assert after['version']==622
    facts={a['id']:a for a in after['assertions']}
    assert all(a==facts[a['id']] for a in before['assertions'])
    aliases={a['id']:a for a in after['aliases']};assert all(a==aliases[a['id']] for a in before['aliases'])
    assert after['merges']==before['merges'] and after['conflicts']==before['conflicts']
    nodes=[e for e in after['entities'] if e['created_version']>620]
    assert len(nodes)==44 and len({e['label'] for e in nodes})==44
    added=[a for a in after['assertions'] if a['created_version']>620]
    edges=[a for a in added if a['context'].get('network')=='utility']
    assert len(edges)==52
    owners={a['canonical_subject']:a['canonical_object'] for a in added if a['predicate']=='part_of'}
    assert all(e['id'] in owners for e in nodes)
    labels={e['label']:e['id'] for e in nodes}
    for st in STATIONS:
        n=st['n'];prefix=f'DFDS-{n} '
        assert owners[labels[prefix+'Common water supply train']]==st['system']
        assert owners[labels[prefix+'Common compressed-air supply train']]==st['system']
        adj={}
        for a in edges:adj.setdefault(a['canonical_subject'],set()).add(a['canonical_object'])
        def reaches(start,end):
            seen=set();queue=[start]
            while queue:
                node=queue.pop()
                if node==end:return True
                if node in seen:continue
                seen.add(node);queue.extend(adj.get(node,set())-seen)
            return False
        for pump in st['pumps']:assert reaches(st['tank'],pump) and reaches(pump,labels[prefix+'Common water main at station outlet'])
        for comp in st['compressors']:assert reaches(comp,labels[prefix+'Common air main at receiver outlet'])
        assert not reaches(st['compressors'][0],labels[prefix+'Common water main at station outlet'])
        assert not reaches(st['tank'],labels[prefix+'Common air main at receiver outlet'])
        assert reaches(labels[prefix+'Common water discharge manifold Point D'],st['tank'])
    save(out/'result.json',{'ok':True,'version':622,'proposals':[x['proposal_id'] for x in logs],
                           'new_entities':nodes,'added_claims':added,'utility_edges':52,'preserved_assertions':len(before['assertions']),
                           'checks':['44 source-identified owned/located components','separate water/air paths','both pump/compressor branches reach own common headers','water recirculation returns to own tank','all prior facts/aliases/merges/four conflicts unchanged','same-source packages guarded620/621']})
    print(json.dumps({'ok':True,'version':622,'mode':out.name,'proposals':[x['proposal_id'] for x in logs]}))


if __name__=='__main__':main()
