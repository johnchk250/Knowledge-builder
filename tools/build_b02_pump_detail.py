"""Build, but do not commit, the reviewed 175093 pump-internal source package."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.implement_b00_corrections import save, support

BASE=ROOT/'output/plant-enrichment/B02'
DOC='doc_b5188c19e5b942cfa976'
PAGES={2:'ev_593f764437c7464fba4c',4:'ev_1fffe4ac90fa4d75bfb3',5:'ev_946ffc19e5fe434c942c',
       6:'ev_e2ec44123b7b4ad8a762',8:'ev_26b1a56da4aa4acabe90',9:'ev_7d3b09d2f27448b7bf27'}
PUMPS=[(1,'A','ent_975edb9acc07451cbc62'),(1,'B','ent_8a35251f220d4c9287d2'),
       (2,'A','ent_afdfc43f0f1148d0b555'),(2,'B','ent_eca52aa5ec3d4d3fa153')]
HOUSES={1:'ent_bdf8e7e7f7f8485b80fe',2:'ent_36135b45a07c4d03bf06'}

def main():
    model=json.loads((BASE/'receiver-detail/accepted/model.json').read_text(encoding='utf8'))
    assert model['version']==624
    ops=[]
    for n,lane,pump in PUMPS:
        ds,ga,bom=(2,4,5) if n==1 else (6,8,9)
        stages,power,dsrpm,garpm,nominal,longqty=(14,3,2870,2867,2949,11) if n==1 else (16,4,2910,2863,2954,13)
        tag=f'DFDSP-{n}{lane}'
        basis=(f'175093 Rev4 cover dated 5-Dec-2019, approved 30-Dec-2019; '
               f'DFDS-{n}A/{n}B datasheet PDFp{ds} Rev02 dated 25-Sep-2019 and matched '
               f'Movitec VCF6/{stages}B GA/section PDFpp{ga}/{bom}. Two pumps per pair; '
               'one component assembly per individual canonical pump. Vendor design, not installed nameplate/field inspection.')
        def fact(subject,predicate,value,page,region,unit=None,relation=False,origin='explicit',kind='specification',extra=None):
            context={'kind':kind,'basis':basis+f' Applicable original PDFp{page}.'}
            if extra:context.update(extra)
            op={'op':'assert','subject':subject,'predicate':predicate,
                'object_entity' if relation else 'value':value,'context':context,**support(PAGES[page],region)}
            op['origin']=origin
            if unit:op['unit']=unit
            ops.append(op)
        def node(key,label,cls,qty,region,material=None):
            temp=f'tmp_dfds{n}{lane.lower()}_{key}'
            ops.append({'op':'entity','id':temp,'label':f'{tag} {label}',**support(PAGES[bom],region)})
            fact(temp,'instance_of',cls,bom,region,kind='classification')
            fact(temp,'part_of',pump,bom,region,relation=True)
            fact(temp,'located_at',HOUSES[n],bom,region,relation=True,origin='inferred')
            if qty is not None:fact(temp,'quantity',qty,bom,region,unit='Nos')
            if material:fact(temp,'component_material',material,bom,region)
            return temp
        electrical=[.071,.77,.95,.935]
        motor=node('motor','Drive motor','electric_motor',1,[.644,.311,.93,.332])
        for pred,value,unit in [('motor_rated_power',power,'kW'),('motor_voltage',415,'V'),
                                ('motor_supply_frequency',50,'Hz'),('motor_pole_count',2,None),
                                ('motor_rated_speed',dsrpm,'rpm')]:
            fact(motor,pred,value,ds,electrical,unit=unit)
        fact(motor,'manufacturer','Laxmi Hydraulics Pvt. Ltd., Chincholi Solapur',ds,electrical)
        fact(motor,'ingress_protection','IP55',ds,electrical)
        fact(motor,'insulation_class','F; temperature rise limited to Class B',ds,electrical)
        fact(motor,'operating_requirement','IE3 air-cooled, 2-pole, 3-phase AC design; 415 V ±10%, 50 Hz ±5%, ambient 50 °C. Supply feeder, installed starter and nameplate configuration are not established by this vendor package.',ds,electrical)
        fact(motor,'motor_rated_speed',garpm,ga,[.419,.095,.581,.15],unit='rpm')
        fact(motor,'source_discrepancy',f'Datasheet PDFp{ds} states motor full-load speed {dsrpm} rpm at rated voltage/frequency; matched GA PDFp{ga} prints {garpm} rpm. Pump nominal/curve basis {nominal} rpm is a separate hydraulic design condition. No final installed motor-speed selection is inferred. GA also prints Make: KSB; datasheet explicitly names Laxmi Hydraulics for the electrical motor.',ga,[.419,.095,.581,.15])
        coupling=node('coupling','Rigid coupling','coupling',1,[.644,.293,.93,.315],'Aluminium coupling-shell halves (BOM862)')
        fact(coupling,'equipment_role','One rigid coupling assembly: BOM862 lists two coupling shells/halves. Quantity1 assembly is inferred from the sectional shaft connection; the reported BOM quantity2 is halves, not two complete couplings.',bom,[.644,.293,.93,.315])
        # The assembly count is a derivation, unlike the raw BOM half count.
        next(o for o in reversed(ops) if o.get('subject')==coupling and o.get('predicate')=='quantity')['origin']='inferred'
        guard=node('guard','Coupling guard group','mechanical_component',2,[.644,.33,.93,.35],'1.4301')
        fact(guard,'equipment_role','BOM681: two coupling guards per pump; guard removal or an isolation procedure is not established.',bom,[.644,.33,.93,.35])
        shaft=node('shaft','Pump shaft','mechanical_component',1,[.644,.62,.93,.641],'1.4057 (section BOM210)')
        fact(shaft,'source_discrepancy','Datasheet material row prints shaft SS413; sectional BOM210 prints 1.4057. Retain the literal source material bases; no unverified grade equivalence is imposed.',ds,[.071,.575,.95,.634])
        impellers=node('impellers','Closed impeller group','mechanical_component',stages,[.644,.601,.93,.622],'1.4301 (section BOM230); SS304 in datasheet')
        fact(impellers,'equipment_role',f'BOM230 reports {stages} impellers per pump, matching the datasheet {stages}-stage design. Closed impellers, 90 mm diameter and six vanes are source design values; no wear measurement or operating speed is inferred.',ds,[.071,.633,.95,.755])
        seal=node('seal','Mechanical seal','mechanical_component',1,[.644,.492,.93,.513])
        fact(seal,'equipment_role','Section BOM433: one mechanical seal; sectional note describes tungsten carbide versus carbon. Small printed seal model is not transcribed. Seal interval, flush circuit and completed maintenance are not established.',bom,[.408,.23,.93,.28])
        sleeves=node('bearings','Bearing sleeve group','bearing',2,[.644,.403,.93,.423],'Tungsten carbide (BOM529)')
        fact(sleeves,'operating_requirement','Datasheet specifies self-lubricated tungsten-carbide plain bearings. No separate oil circuit, grease interval or commissioned dry-run protection is inferred from this construction statement.',ds,[.071,.52,.95,.56])
        stool=node('stool','Motor stool','mechanical_component',1,[.644,.583,.93,.604],'IS210 Gr FG260 (BOM341)')
        shroud=node('shroud','Pump shroud','mechanical_component',1,[.644,.746,.93,.765],'AISI304 (BOM10-6)')
        casing=node('casings','Stage casing group','mechanical_component',None,[.644,.654,.93,.727],'1.4301')
        fact(casing,'equipment_role',f'Section BOM108.01: {longqty} stage casings; 108.02: two stage casings with ceramic bearing; 108.04: one bottom stage casing; 108.05: one upper stage casing. These are source-counted construction rows; do not sum them into a different hydraulic stage count. Datasheet states {stages} stages.',bom,[.644,.654,.93,.727])
        spacers=node('spacers','Long spacer sleeve group','mechanical_component',longqty,[.644,.456,.93,.476],'1.4305 (BOM525.03)')
        fact(spacers,'equipment_role',f'BOM525.03 long spacer sleeve quantity {longqty}; seal-side, shaft-end and short spacer rows remain distinct, with no invented field tags.',bom,[.644,.421,.93,.494])
        for src,dst in [(motor,coupling),(coupling,shaft),(shaft,impellers)]:
            fact(src,'mechanically_drives',dst,bom,[.125,.1,.431,.81],relation=True,kind='connection',
                 extra={'network':'mechanical','verification':'documented','condition':'Vendor rigid-coupled pump design; installed status not established.'})
        fact(pump,'rated_rotational_speed',nominal,ds,[.071,.315,.95,.349],unit='rpm')
        fact(pump,'maintenance_requirement','Source vendor design includes removable coupling guards, mechanical seal, bearing sleeves and stage/shroud construction. Painting and inspection/testing are per approved schedule/QAP; this source does not supply a completed test, replacement interval, isolation completeness or installed spare-part approval.',ds,[.071,.633,.95,.755])
    evidence=json.loads((BASE/'review/pumps/evidence.json').read_text(encoding='utf8'))
    assert len(ops)<=500,len(ops)
    pkg={'document_id':DOC,'baseline_version':624,'baseline_model':'output/plant-enrichment/B02/receiver-detail/accepted/model.json',
         'expected_new_components':44,'visual_ids':list(PAGES.values()),'body':{
          'summary':'B02: independently scoped DFDS1/2 pump drive chains and maintainable vendor internals with qualified motor speeds',
          'operations':ops,'intake_assessment':{'route':'mixed',
             'purpose':'Use separately matched 14/16-stage pump originals for existing canonical A/B pumps; no duplicate common pumps or installed motor assumptions.',
             'questions':['Which maintainable internals and motor/coupling drive chain apply to each numbered pump?',
                          'Which differing motor-speed, material and quantity bases must remain inspectable?'],
             'reviewed_evidence_ids':[e['id'] for e in evidence],
             'gaps':['All nine original pages visually inventoried. Cover, both datasheets, curves, GAs and readable enlarged sectional BOMs reviewed independently.',
                     'Curve operating intersection points are calculated design conditions, not promoted to rated or observed duty.',
                     'Datasheet/GA motor speed and supplier labels differ; installed final nameplate/source selection is absent.',
                     'BOM casing-row total differs from hydraulic stage count; keep raw construction rows and stated stage count separate.',
                     'Small seal model and spare-part approval unresolved; no replacement interval, electrical feeder, completed test or complete isolation procedure.']}}}
    out=BASE/'pump-detail';out.mkdir(exist_ok=True);save(out/'package.json',pkg)
    print(json.dumps({'operations':len(ops),'new_components':44,'baseline':624}))

if __name__=='__main__':main()
