"""Build the separately reviewed remaining pump BOM groups at exact v625."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.build_b02_pump_detail import BASE, DOC, PAGES, PUMPS, HOUSES
from tools.implement_b00_corrections import save, support


def main():
    model = json.loads((BASE/'pump-detail/accepted/model.json').read_text(encoding='utf8'))
    assert model['version'] == 625
    ops = []
    review = []
    for n, lane, pump in PUMPS:
        page = 5 if n == 1 else 9
        ring_count = 14 if n == 1 else 16
        basis = (f'175093 Rev4 approved 30-Dec-2019; individually matched DFDS-{n}{lane} '
                 f'VCF6/{ring_count}B sectional BOM, original PDFp{page}. '
                 'Vendor design, not an installed spare-parts survey or completed maintenance record.')

        def fact(subject, predicate, value, region, unit=None, relation=False, origin='explicit'):
            op = {'op':'assert', 'subject':subject, 'predicate':predicate,
                  'object_entity' if relation else 'value':value, 'origin':origin,
                  'context':{'kind':'classification' if predicate=='instance_of' else 'specification',
                             'basis':basis}, **support(PAGES[page], region)}
            if unit:
                op['unit'] = unit
            ops.append(op)

        def node(key, label, cls, region, quantity, material, role):
            label = f'DFDSP-{n}{lane} {label}'
            assert not any(e['label']==label for e in model['entities']), label
            temp = f'tmp_dfds{n}{lane.lower()}_maintenance_{key}'
            ops.append({'op':'entity','id':temp,'label':label,**support(PAGES[page],region)})
            fact(temp,'instance_of',cls,region)
            fact(temp,'part_of',pump,region,relation=True)
            fact(temp,'located_at',HOUSES[n],region,relation=True,origin='inferred')
            if quantity is not None:
                fact(temp,'quantity',quantity,region,unit='Nos')
            fact(temp,'component_material',material,region)
            fact(temp,'equipment_role',role,region)
            review.append({'pump':pump,'label':label,'page':page,'region':region,
                           'quantity':quantity,'material':material,'source_statement':role})

        node('vent','Vent plug','plug_group',[.644,.258,.93,.278],1,'1.4301 (BOM903.01)',
             'BOM903.01: one vent plug per pump. No drain or automatic vent function, field tag or isolation procedure is inferred.')
        node('screwed','Screwed plug group','plug_group',[.644,.199,.93,.22],2,'1.4301 (BOM903.02)',
             'BOM903.02: two screwed plugs per pump. The drawing does not establish a drain destination or maintenance interval.')
        node('cover','Pump cover','mechanical_component',[.644,.636,.93,.658],1,'1.4301 (BOM160)',
             'BOM160: one cover per pump, distinct from the stage casing and external shroud.')
        node('rings','O-ring group','mechanical_component',[.644,.511,.93,.584],None,'EPDM WRC (BOM412.01–412.04)',
             f'Four separately counted BOM rows: 412.01 quantity2; 412.02 quantity1; 412.03 quantity{ring_count}; 412.04 quantity1. Counts are per pump and remain row-qualified. No aggregate spare kit, interchangeability, replacement interval or installed condition is inferred.')
        node('short','Short spacer sleeve group','mechanical_component',[.644,.475,.93,.494],2,'1.4305 (BOM525.01)',
             'BOM525.01: two short spacer sleeves; distinct from accepted long spacer sleeves and the shaft-end and seal-side sleeves.')
        node('shaftend','Shaft-end spacer sleeve','mechanical_component',[.644,.438,.93,.458],1,'1.4305 (BOM525.04)',
             'BOM525.04: one shaft-end spacer sleeve, distinct from short, long and seal-side rows.')
        node('sealside','Seal-side spacer sleeve','mechanical_component',[.644,.42,.93,.44],1,'1.4305 (BOM525.05)',
             'BOM525.05: one seal-side spacer sleeve, distinct from the mechanical seal and other spacer rows.')

    evidence = json.loads((BASE/'review/pumps/evidence.json').read_text(encoding='utf8'))
    pkg = {'document_id':DOC,'baseline_version':625,
           'baseline_model':'output/plant-enrichment/B02/pump-detail/accepted/model.json',
           'expected_new_components':28,'visual_ids':list(PAGES.values()),'body':{
               'summary':'B02: remaining DFDS pump cover, plugs, qualified O-ring and spacer BOM groups',
               'operations':ops,'intake_assessment':{'route':'mixed',
                   'purpose':'Complete distinct maintainable vendor groups on the four existing pumps without duplicating accepted core internals.',
                   'questions':['Which remaining BOM rows apply to each canonical pump?',
                                'Which quantities must remain row-qualified rather than aggregated into a spare kit?'],
                   'reviewed_evidence_ids':[e['id'] for e in evidence],
                   'gaps':['All nine original pages were previously inventoried. Matched sectional originals pp5/9 and readable BOM enlargements were independently reviewed again for this scope.',
                           'Cover160, plugs903.01/903.02, rings412.01–412.04 and spacers525.01/.04/.05 are distinct rows; 525.05 is the seal-side row.',
                           'O-ring row412.03 differs between 14-stage and16-stage pumps. No aggregate spare-kit quantity or interchangeability is asserted.',
                           'Fasteners, pin, circlip and generic safety-device row remain construction detail; an unspecified safety-device function is not promoted to an operational safeguard.',
                           'No installed condition, replacement interval, completed work, drain route or full isolation procedure is supplied.']}}}
    out = BASE/'pump-maintenance';out.mkdir(exist_ok=True)
    save(out/'source-review.json',{'baseline':625,'source':DOC,'reviewed_groups':review})
    save(out/'package.json',pkg)
    print(json.dumps({'baseline':625,'operations':len(ops),'components':28}))


if __name__ == '__main__':
    main()
