"""Evidence-linked candidate detail capture; never creates CAD or plant facts."""
import argparse
import json
import math
from pathlib import Path
from . import spatial

KINDS=('identity','view','dimension','component','constraint','interface','route','material','tolerance','manufacturing','revision')
GUIDE='''
Every source block must also return reconstruction_assessment, separately from operations and geometry_suggestions.
Capture ALL relevant detail for future CAD, not only overall envelope dimensions. Inspect schedule rows, sections, detail views, notes and referenced drawings. Cover equipment identity/revision; components/counts; diameters, wall/plate thicknesses, shaft steps, bores, keys, grooves, holes, bolt circles; axes/datums/units/view orientation; assembly offsets, coaxiality, symmetry, mounting and mating interfaces; pipe centreline segments, elbows and elevations when explicit; material/lagging/coatings; tolerances/fits and manufacturing notes. P&ID connectivity is not a physical route. Missing views or manufacturer details are gaps. Never estimate a dimension from page pixels or assume a standard manufacturer's geometry.
Schema: {schema:1,scope:"block|document",applicability:"relevant|not_applicable|uncertain",summary:"reason and reconstructable scope",reviewed_evidence_ids:["supplied evidence IDs"],records:[{id:"unique record ID",kind:"identity|view|dimension|component|constraint|interface|route|material|tolerance|manufacturing|revision",subject:"equipment ID/tag and component path",feature:"precise engineering meaning",value:123,unit:"mm or null for nonnumeric details",basis:"explicit|derived|interpreted",evidence:[{evidence_id:"...",quote:"exact source text",region:optional [0,0,1,1]}],derivation:null,notes:"qualifiers, datum, drawing symbol/row, applicability and uncertainty"}],gaps:[{subject:"equipment/component",detail:"missing/ambiguous information or unchecked category",impact:"what cannot be modeled or verified",required_source:"specific view/detail/drawing/measurement",blocking:true}],conflicts:["competing values, revisions or view interpretations and evidence IDs"]}.
Values may be strings, finite numbers, booleans or arrays. Keep source units; record any conversion or calculated value as derived with derivation:{formula:"explicit calculation",inputs:["record IDs"]}. Explicit/interpreted records use derivation:null. Interpretations must never be asserted as explicit plant facts. Cite immutable supplied evidence for every record, including input sources for calculations. Regions require an actually supplied/reviewed image; when only text is available, cite text and record missing visual inspection. Record source view orientation and coordinate convention; never claim a shared plant frame from drawing layout.
reviewed_evidence_ids covers exactly the supplied block (or every document evidence item for a final document dossier). Reconcile with accepted knowledge using its provenance; record conflicts instead of overwriting. This output is candidate evidence for later review, not approved geometry or proof of completeness. Use not_applicable only with a reason and no records; still assess text-only datasheets, BOMs, manuals and revision notes. Partial coverage must remain a gap. Do not silently truncate records: split source scope if the response budget is insufficient. The five-proxy-suggestion limit does not limit these records.
'''


def validate(store, assessment, document_id, visual_ids=(), expected_ids=None):
    errors=[]
    if not isinstance(assessment,dict):return ['Reconstruction assessment missing; future CAD detail capture is incomplete.']
    required={'schema','scope','applicability','summary','reviewed_evidence_ids','records','gaps','conflicts'}
    if set(assessment)!=required:return ['Invalid reconstruction assessment fields.']
    if assessment['schema']!=1 or assessment['scope'] not in ('block','document') or assessment['applicability'] not in ('relevant','not_applicable','uncertain'):
        errors.append('Invalid reconstruction schema, scope or applicability.')
    if not isinstance(assessment['summary'],str) or not assessment['summary'].strip():errors.append('Explain reconstruction applicability and scope.')
    known={e['id'] for e in store.rows('SELECT id FROM evidence WHERE document_id=?',(document_id,))}
    reviewed=assessment['reviewed_evidence_ids']
    if not isinstance(reviewed,list) or any(not isinstance(e,str) for e in reviewed):return errors+['Invalid reviewed evidence IDs.']
    expected=known if assessment['scope']=='document' else set(expected_ids or reviewed)
    if set(reviewed)!=expected or len(reviewed)!=len(set(reviewed)) or not set(reviewed)<=known:errors.append('Reconstruction evidence coverage is incomplete or unrelated.')
    records=assessment['records']
    if not isinstance(records,list) or len(records)>2000:return errors+['Use at most 2000 detail records; split larger source scopes without dropping details.']
    ids=set()
    def safe(value):
        return value is None or isinstance(value,(str,bool)) or (type(value) in (int,float) and math.isfinite(value)) or (isinstance(value,list) and all(safe(v) for v in value))
    for record in records:
        if not isinstance(record,dict) or set(record)!={'id','kind','subject','feature','value','unit','basis','evidence','derivation','notes'}:
            errors.append('Invalid reconstruction record fields.');continue
        rid=record['id']
        if not isinstance(rid,str) or not rid or rid in ids:errors.append('Detail record IDs must be nonempty and unique.')
        else:ids.add(rid)
        if record['kind'] not in KINDS or record['basis'] not in ('explicit','derived','interpreted'):errors.append('Invalid detail kind or basis.')
        if any(not isinstance(record[k],str) or not record[k].strip() for k in ('subject','feature')) or not isinstance(record['notes'],str):errors.append('Detail subject, feature and notes are required.')
        if not safe(record['value']) or record['value'] is None or not (record['unit'] is None or isinstance(record['unit'],str)):errors.append('Use finite detail values and explicit units, or record a gap.')
        if record['kind'] in ('dimension','tolerance') and type(record['value']) in (int,float) and (not isinstance(record['unit'],str) or not record['unit'].strip()):errors.append('Numeric dimensions and tolerances require units.')
        errors.extend(spatial.evidence_errors(store,record['evidence'],set(visual_ids),document_id))
        if isinstance(record['evidence'],list) and any(isinstance(r,dict) and r.get('evidence_id') not in reviewed for r in record['evidence']):errors.append('Detail cites evidence not listed as reviewed.')
        d=record['derivation']
        if record['basis']=='derived':
            if not isinstance(d,dict) or set(d)!={'formula','inputs'} or not isinstance(d.get('formula'),str) or not d['formula'].strip() or not isinstance(d.get('inputs'),list) or not d['inputs'] or any(not isinstance(i,str) for i in d['inputs']):errors.append('Derived values require a formula and input record IDs.')
        elif d is not None:errors.append('Only derived records may contain a derivation.')
    for record in records:
        if isinstance(record,dict) and isinstance(record.get('derivation'),dict):
            inputs=record['derivation'].get('inputs')
            if isinstance(inputs,list) and all(isinstance(i,str) for i in inputs) and (not set(inputs)<=ids or record.get('id') in inputs):errors.append('Calculation input is missing or self-referential.')
    if not isinstance(assessment['gaps'],list):errors.append('Gaps must be an array.')
    else:
        for gap in assessment['gaps']:
            if not isinstance(gap,dict) or set(gap)!={'subject','detail','impact','required_source','blocking'} or any(not isinstance(gap[k],str) or not gap[k].strip() for k in ('subject','detail','impact','required_source')) or type(gap['blocking']) is not bool:errors.append('Gaps must identify the detail, impact, required source and blocking flag.')
    if not isinstance(assessment['conflicts'],list) or any(not isinstance(c,str) for c in assessment['conflicts']):errors.append('Conflicts must be an array of explanations.')
    if assessment['applicability']=='not_applicable' and records:errors.append('Not-applicable assessment cannot contain reconstruction records.')
    if assessment['applicability']!='not_applicable' and not records and not assessment['gaps']:errors.append('Relevant/uncertain sources need detail records or explicit gaps.')
    return list(dict.fromkeys(errors))


def audit(store, assessment, document_id, visual_ids=(), expected_ids=None):
    errors=validate(store,assessment,document_id,visual_ids,expected_ids)
    return {'status':'invalid_or_missing' if errors else 'candidate_pending_review','errors':errors,
            'notice':'Structural/source validation does not verify drawing interpretation or approve CAD.'}


def main():
    parser=argparse.ArgumentParser(description='Export recorded reconstruction candidates and their validation status.')
    parser.add_argument('--data',required=True);parser.add_argument('--document-id',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args()
    from .store import Store
    store=Store(args.data)
    rows=store.rows("SELECT s.run_id,s.response,p.id proposal_id,p.status knowledge_status FROM run_steps s JOIN runs r ON r.id=s.run_id LEFT JOIN proposals p ON p.run_id=r.id WHERE r.document_id=? AND s.stage='propose' ORDER BY s.created,s.rowid",(args.document_id,))
    candidates=[]
    for row in rows:
        response=json.loads(row.pop('response'))
        candidates.append({**row,'assessment':response.get('reconstruction_assessment'),'validation':response.get('reconstruction_validation',{'status':'not_assessed_legacy'})})
    Path(args.output).write_text(json.dumps({'document_id':args.document_id,'candidates':candidates,'note':'Keep runs separate; reconcile revisions and block-level records before modeling.'},indent=2,ensure_ascii=False),encoding='utf-8')


if __name__=='__main__':main()
