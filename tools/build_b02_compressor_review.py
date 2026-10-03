"""Record bounded compressor source reconciliation without inventing installed models."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'output/plant-enrichment/B02'
DOC = 'doc_d91e9eef8a40479687cd'


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf8')


def main():
    s = json.loads((BASE/'accepted-v627.json').read_text(encoding='utf8'))
    m = s['model']
    assert m['version'] == 627
    d = next(d for d in s['documents'] if d['id'] == DOC)
    assert hashlib.sha256((ROOT/'data/plant/originals'/d['sha256']).read_bytes()).hexdigest() == d['sha256']
    evs = [e for e in s['evidence'] if e['document_id'] == DOC]
    pages = {}
    for e in evs:
        pages.setdefault(e['page'], e['id'])
    ops = []

    def add(subject, predicate, value, supports):
        ops.append({'op':'assert', 'subject':subject, 'predicate':predicate, 'value':value,
            'origin':'inferred', 'confidence':.97,
            'context':{'kind':'specification', 'basis':'175103 Rev2, FIO16-Oct-2019. Source reconciliation of vendor design sheets, not installed model assignment or commissioned settings. System association follows the separately accepted capacity comparison only.'},
            'evidence':[{'evidence_id':pages[p], 'region':r} for p,r in supports]})

    full = [.035,.08,.975,.96]
    tds = [.12,.10,.79,.91]
    for system, model, ds, pid, wiring, control, compressors in [
        ('ent_2024dfa4a4084a86b0b5','ZT160',3,5,6,27,['ent_081c34835a684544a6d0','ent_2fc625b1e93743ae9e7f']),
        ('ent_b2f48e8d116f484882a1','ZT132',10,12,14,18,['ent_1936e05712944165aeb9','ent_b5dfed25a0c84bb1a91a'])]:
        add(system, 'design_applicability',
            f'Available vendor {model} P&ID PDFp{pid} identifies inlet filter100, throttle103, LP screw104, HP screw111, inter/aftercooling, water separators109/117 and drains124/127; oil sump130, pump131, cooler132, filter133 and breathing system169; motor150, coupling151, fan motors153 and cubicle160. These are model-specific design callouts, not installed tags. No reviewed sheet maps this model to an individual DFDSC A/B tag; capacity correspondence alone does not authorize cloning these parts under numbered compressors.',
            [(pid,full),(ds,tds)])
        add(system, 'source_discrepancy',
            f'{model} datasheet PDFp{ds} row3.1 says single stage with male/female rotor. P&ID PDFp{pid} shows separate LP104 and HP111 screw elements with intercooling; control description PDFp{control} also describes LP then HP compression. Preserve the conflicting design descriptions. Neither an installed single-stage arrangement nor a resolved final two-stage selection is established.',
            [(ds,[.12,.395,.79,.462]),(pid,[.05,.32,.79,.57]),(control,[.12,.21,.92,.54])])
        cooling = ('ZT132 P&ID p12 legend additionally calls116a/116b water-cooled inter/aftercoolers, while its body uses108a/b and116a/b. ' if model=='ZT132' else 'ZT160 P&ID p5 legend calls108 intercooler and116 aftercooler. ')
        add(system, 'source_discrepancy',
            f'{model} datasheet and GA identify air cooling; the control description PDFp{control} names air-cooled oil/inter/aftercoolers and fans153a/b but also describes a cooling-water flow switch and shutoff valve with5-10min closure delay. '+cooling+'Keep this inconsistency unresolved. A cooling-water supply edge or installed water valve is not established by the generic paragraph.',
            [(control,[.12,.75,.92,.94]),(pid,[.80,.085,.97,.69]),(ds,[.12,.13,.79,.215])])
        add(system, 'source_discrepancy',
            f'{model} datasheet PDFp{ds} row4.8 specifies DOL starting. Service wiring PDFpp{wiring}/{wiring+1} identifies K21 line, K22 star and K23 delta contactors and a Y-D drive-motor starter; its DOL labels separately apply to fan motors. The main-motor kW box in the wiring is blank. Do not silently choose an installed starter or populate its rating. Final motor manufacturer and bearing/winding RTDs remain referred to missing180055-ISG0 by review p36.',
            [(wiring,[.045,.055,.90,.85]),(ds,[.12,.48,.79,.63]),(36,[.12,.35,.94,.49])])
        table = 34 if model=='ZT160' else 25
        add(system, 'source_discrepancy',
            f'{model} control interface table PDFp{table} calls S2-prime remote Load/Unload command (customer DCS to compressor LCP). Service wiring PDFp{wiring} legend calls S2-prime remote emergency-stop button and PDFp{wiring+1} draws it in the remote emergency-stop circuit. These functions are not interchangeable. No commissioned S2-prime loop, terminal mapping or executable control edge is created; obtain the approved final interface/loop drawings.',
            [(table,[.12,.26,.92,.58]),(wiring,[.045,.44,.205,.59]),(wiring+1,[.795,.045,.89,.29])])
        add(system, 'operating_requirement',
            f'Vendor control attachment for {model} is identified by its reference list PDFp{table}, not by attachment order: '+('1671700A02/A03 (PDFpp26-34).' if model=='ZT160' else '1671700A07/A08 (PDFpp17-25).')+' It describes Elektronikon local/remote control, unloaded starting, a minimum25s load delay for oil-pressure build-up, programmed unloading before normal stop, immediate emergency stop, and a stated20s minimum restart period after trip/reset. These are source design descriptions, not verified field settings. The separate numeric protection/service table needs reconciliation against P&ID tags before any per-instrument settings are assigned.',
            [(table,[.12,.62,.78,.74]),(control+3,[.12,.25,.92,.56]),(control+5,[.12,.23,.92,.66])])
        for compressor in compressors:
            add(compressor, 'design_applicability',
                '175103 supplies model-specific ZT160/ZT132 GA, P&ID and service wiring but no reviewed individual DFDSC tag/nameplate mapping. Existing system-level capacity comparisons remain qualified. Hold per-instance internals, final motor/starter selection and protection settings until approved model-to-tag evidence and referenced final motor document180055-ISG0 are available. The corpus search found no180055 source; its mention in review p36 is a reference, not the missing motor data.',
                [(36,[.12,.35,.94,.49]),(ds,[.12,.10,.79,.30])])
    out=BASE/'compressor-review'
    save(out/'baseline-model.json',m)
    deep={3,4,5,6,7,8,10,11,12,13,14,15,16,18,19,20,21,22,23,24,25,27,30,32,34,35,36}
    # Repeated control pages28/29/31/33 retain the prior text-review disposition.
    used={e['evidence_id'] for o in ops for e in o['evidence']}
    inventory=[{'evidence_id':e['id'],'page':e['page'],
        'review':'original visually reviewed for bounded reconciliation' if e['page'] in deep else 'prior document-wide visual inventory/text review; no new detailed visual acceptance',
        'disposition':'used' if e['id'] in used else 'corroborating' if e['page'] in deep else 'deferred-with-reason',
        'reason':'Model/part/starter/control applicability and conflicting source bases; pin-by-pin circuit acceptance and calibrated settings are outside this package.'} for e in evs]
    save(out/'source-review.json',{'document_id':DOC,'sha256':d['sha256'],'deep_pages':sorted(deep),'inventory':inventory,
        'findings':['Reference lists reverse naive attachment ordering: pp17-25 cite ZT132 A07/A08; pp26-34 cite ZT160 A02/A03.',
        'Both main-motor wiring legends show star/delta while TDS says DOL. Fan DOL is distinct.',
        'S2-prime load/unload table versus remote emergency-stop wiring is unresolved.',
        'ZT132 TDS4210kg differs from GA3700kg standard configuration; no mass selected.',
        'P&ID Y2 is generic/model-qualified; optional full-feature dryer details do not prove installed dryer.',
        'Protection-table numerical values and service counters are available source work, not commissioned values. Tag/function discrepancies require separate reconciliation.'],
        'open_work':['Model-reference internals can be developed separately after reviewing exact legends; do not make physical per-instance parts from capacity correspondence.',
                     'Finish control table/P&ID comparison: air-filter high versus low-vacuum wording, KSH49 oil versus oil-pump wording, S2-prime interface and check-valve114 text versus safety-valve114 diagram.',
                     'Missing180055 motor record and numbered model mapping remain evidence gaps; downstream headers are independent available work.']})
    save(out/'package.json',{'document_id':DOC,'baseline_version':627,
        'baseline_model':'output/plant-enrichment/B02/compressor-review/baseline-model.json','expected_new_components':0,
        'visual_ids':[pages[p] for p in sorted(deep)],'body':{
            'summary':'B02: reconcile compressor model applicability, staging, cooling, starter and S2-prime source conflicts without invented installed hardware',
            'operations':ops,'intake_assessment':{'route':'mixed','purpose':'Expose vendor-source limits on the two existing DFDS systems and four canonical compressors.',
            'questions':['Which compressor details are model references rather than confirmed numbered-unit parts?','Which source contradictions prevent final starter/control assignment?'],
            'reviewed_evidence_ids':[e['id'] for e in evs],
            'gaps':['Document-wide inventory is retained; source-review.json separates deep visual review from deferred detailed circuit work.',
                    'No per-instance model mapping, missing180055 final motor record, and staging/cooling/starter/S2-prime contradictions remain explicit.',
                    'No numeric protection setting, new physical entity, utility/electrical/control edge, or maintenance interval is accepted by this bounded reconciliation.']}}})
    print(json.dumps({'baseline':627,'assertions':len(ops),'new_entities':0}))


if __name__=='__main__':main()
