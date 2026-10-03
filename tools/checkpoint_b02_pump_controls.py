"""Checkpoint the accepted v627 controls and corrected viewport evidence."""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'output/plant-enrichment/B02'

def read(path):return json.loads(path.read_text(encoding='utf8'))
def save(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

def main():
    snapshot=read(BASE/'accepted-v627.json')
    assert snapshot['model']['version']==627 and snapshot['integrity']==['ok'] and not snapshot['foreign_key_errors']
    manifest=read(BASE/'browser-full-manifest-v627.json')
    log=read(BASE/'browser-checks-v627.json')
    expected={f['id'] for p in manifest['roots'] for f in p['facts']}
    assert len(expected)==32
    for view in ['desktop','wide']:
        assert {c['fact'] for c in log['checks'] if c['viewport']==view}==expected
    assert len([c for c in log['checks'] if c['viewport']=='narrow'])==8
    assert len({(c['pump'],c['sensor']) for c in log['signalScenes'] if c['viewport']=='wide'})==8
    assert all(c['image']['complete'] and c['image']['width']>0 and c['source_return'] for c in log['checks'])
    assert all(c['viewport_size']=={'width':1280,'height':900} for c in log['checks'] if c['viewport']=='wide')
    for c in log['checks']:
        if c['viewport']=='desktop':c['viewport']='default_panel'
    for c in log['signalScenes']:
        if c['viewport']=='desktop':c['viewport']='default_panel'
    log['viewport_note']='Initial desktop label denoted the default browser panel (470px screenshot), not a wide layout. Corrected to default_panel. All32 claims repeated at explicit1280x900;8 narrow checks at requested390x844.'
    save(BASE/'browser-checks-v627.json',log)
    old=read(BASE/'browser-checks-v626.json')
    assert len({c['fact'] for c in old['checks'] if c['viewport']=='desktop'})==164
    assert len([c for c in old['checks'] if c['viewport']=='wide'])==16
    for c in old['checks']:
        if c['viewport']=='desktop':c['viewport']='default_panel'
    old['viewport_note']='Original164 exhaustive checks ran in the default browser panel, not an explicitly wide viewport.16 narrow checks pass.16 additional1280x900 journeys across all four pumps verified the preserved v626 maintenance claims on modelv627.'
    save(BASE/'browser-checks-v626.json',old)
    description=('v627 controls verified:32 claims on12 existing records passed original-page/crop/source-return checks at explicit1280x900 desktop width and in the default app panel;8 narrow journeys passed. All8 same-system PS/DPS-to-pump signal links are drawn.46 Node tests, independent control semantics, integrity/FK, preservation and both pilot audits pass.')
    next_action=('B02: common pump-control milestone is accepted and verified atv627. Review175103 compressor PID/controller originals pp4-8/11-16 against model applicability and existing qualified identities; then trace175089 common headers to TP1/TP13 local originals. Preserve missing final180055 motor source, tagged level/MGV mapping gap, PS polarity and filter trip/annunciation disagreements. Do not replay accepted packages.')
    progress=read(BASE/'progress.json')
    assert progress['latest_version']==627
    verification={'data_version':627,'snapshot':'accepted-v627.json','integrity':'ok','foreign_key_errors':[],
        'preservation':'All16828 prior assertions and prior aliases/merges/four qualified conflicts unchanged; no new entities.',
        'independent_audit':'pump-controls/accepted/semantic-audit.json','node_tests':'46/46',
        'pilot_audits':['silo-audit-v627.json','crusher-audit-v627.json'],'browser':description,
        'browser_artifact':'browser-checks-v627.json'}
    progress.update(next_action=next_action,verification_pending_version=None,verification=verification,data_verification=verification)
    save(BASE/'progress.json',progress)
    phase_path=ROOT/'docs/plant-handoff/phase-progress.json';phase=read(phase_path)
    phase.update(latest_verified_version=627,next_action=next_action,updated_date='2026-10-03')
    phase['last_completed_work']={'scope':description,'version':627,'checkpoint':'output/plant-enrichment/B02/checkpoint.md'}
    phase['last_accepted_work']['visual_gate']='passed at explicit desktop and narrow widths'
    for row in phase['run_history']:
        if row.get('version')==626 and 'Actual browser verification' in row.get('milestone',''):
            row['milestone']=row['milestone'].replace('at desktop','at default browser width')
    phase['run_history'].append({'date':'2026-10-03','batch':'B02','version':627,'milestone':description,'verification':'passed; B02 remains in_progress'})
    save(phase_path,phase)
    batches_path=ROOT/'docs/plant-handoff/batches.json';batches=read(batches_path)
    next(b for b in batches['batches'] if b['id']=='B02').update(next_action=next_action,latest_version=627)
    save(batches_path,batches)
    sources=read(BASE/'sources.json');review=read(BASE/'pump-controls/source-review.json')
    sources.append({'document_id':review['document_id'],'sha256':review['sha256'],'drawing':review['drawing'],
        'filename':'OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf','approval':review['title_status'],
        'disposition':'used','deep_reviewed_pages':[1,2,3,4,18,19,20,32],
        'evidence_inventory':review['inventory'],'accepted_version':627,'proposal_id':'prop_b94fcde5d1cb45d99a07',
        'source_package':'pump-controls/accepted/package.json','verification':description,
        'open_available_work':['Local FAS/conveyor/selector application pages remain with downstream consumer packages.',
            'Exact level-switch/inlet-valve KKS and Tank2 compartment applicability require separate SW/PW/runoff reconciliation; no tagged level-control edge added.',
            '175265 filter trip vs separately accepted179162 annunciation, PS low-pressure action vs schedule High label, and H/general wording vs not-LOW start condition remain inspectable qualifications. Approved final cause-and-effect/PLC/commissioning evidence needed.']})
    save(BASE/'sources.json',sources)
    queue=read(BASE/'source-queue.json')
    for row in queue:
        if row['document_id']==review['document_id']:
            row.update(status='common_pump_controls_accepted_verified_v627_local_work_remains',
                next_action='Common pump controls verified627; exact tagged LS/MGV mapping remains a cross-source gap. Local TP1/TP13 application regions remain for exact consumer interface review.')
    save(BASE/'source-queue.json',queue)
    findings=read(BASE/'review/control/findings.json')
    findings.update(original_visual_review_pages=[1,2,3,4,18,19,20,32],
        comparison_originals={'document_id':'doc_4f2cd96c3b1e413ea4b5','pages':[30,53,54]},
        disposition='common pump controls accepted and verified627; source differences retained',
        accepted_proposal='prop_b94fcde5d1cb45d99a07',next=next_action)
    findings['findings'].extend(['All36 original individual pump permissive/trip claims preserved;32 new claims include8 explicit PS/DPS signal links.',
        '179162 p30 independently reviewed: automatic standby start,500mm minimum level,60s low-pressure trip delay and suction-DP annunciation. These remain separate accepted bases, not copied into175265 logic.',
        '179162 p53 retains literal High severity on PS rows; p54 retains0.4kg/cm2 setpoint below0.7-7kg/cm2 range. No corrected commissioned setting or contact polarity invented.'])
    save(BASE/'review/control/findings.json',findings)
    with (BASE/'coverage.csv').open(newline='',encoding='utf8') as f:rows=list(csv.DictReader(f))
    for row in rows:
        if row['dimension']=='control':row.update(status='common_pump_control_verified_v627_local_and_tagged_level_work_remains',evidence_or_next='pump-controls/accepted;browser-checks-v627.json;sources.json source disagreements;exact local application/control mapping remains')
        if row['dimension']=='provenance_visual':row.update(status='accepted_milestones_verified_through_v627',evidence_or_next='browser-checks-v626.json:164 default-panel/16 narrow/16 wide;browser-checks-v627.json:32 wide/32 default-panel/8 narrow')
        if row['dimension']=='maintenance_access':row.update(evidence_or_next='filter-detail/accepted;pump-detail/accepted;pump-maintenance/accepted;installed records and compressor detail remain')
    with (BASE/'coverage.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    for path in [BASE/'checkpoint.md',ROOT/'docs/plant-handoff/FIVE_PHASE_PLAN.md']:
        lines=path.read_text(encoding='utf8').splitlines()
        for i,line in enumerate(lines):
            if line.startswith('**Next action:**'):lines[i]='**Next action:** '+next_action
            elif line.startswith('Next action:'):lines[i]='Next action: '+next_action
            elif 'Actual browser verification at v626:' in line:lines[i]=line.replace('at desktop','at default browser width')
        if path.name=='checkpoint.md':lines[2]='Status: **in_progress**. Baseline v620; latest accepted and fully verified model **v627**. Compressor internals/control and exact downstream common-header connections remain.'
        path.write_text('\n'.join(lines)+'\n\n### B02 verified control milestone - v627\n\n'+description+'\n\nViewport correction: the earlier v626 exhaustive164 checks used the default app panel.16 mobile checks and16 additional explicit1280x900 checks across all four pumps pass; wide checks were performed on v627 with all v626 facts preserved.\n',encoding='utf8')
    with (BASE/'verification.md').open('a',encoding='utf8') as f:
        f.write('\n## v627 pump-control acceptance\n\n'+description+'\n\nAll prior16828 assertions, aliases, merges and four exact conflicts are preserved. Full source-scoped restorable backup and rehearsal: pump-controls/backup-v626 and pump-controls/rehearsal. Accepted proposal prop_b94fcde5d1cb45d99a07. Source review and reconciliation include independently inspected175265 pages1-4,18-20,32 and179162 pages30,53,54. No new numeric setpoint or duplicate sensor.\n\n'+old['viewport_note']+'\n')
    print(description)

if __name__=='__main__':main()
