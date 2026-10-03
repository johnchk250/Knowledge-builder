# Coal blending silo implementation

Implemented 20 September 2026 against the v510 handoff baseline. Accepted model is **v527**, after 17 reviewed ingestion batches. Open the **Blending** area in Plant explorer to enter the house directly.

## What is now navigable

The house view follows two vertical process assemblies, with shared/local services beside them:

| Incoming conveyors | Vessel | Extractor | Feeder | Selector | Outlets |
|---|---|---|---|---|---|
| EBA-6B and EBA-16A | EBB-1 | EBE-CES-1 | KF-3 | FG-13 | Selected EBA-17A or EBA-17B |
| EBA-6A and EBA-16B | EBB-2 | EBE-CES-2 | KF-4 | FG-14 | Selected EBA-17A or EBA-17B |

Arrows retain their individual evidence and operating conditions. Simultaneous operation and a current blending ratio are not asserted. Scene placement is an illustrative arrangement; cited elevations and drawing views carry the engineering location information.

- **Each vessel:** shell/liner, level and temperature instrumentation, access, emergency bypass chute and rod gate, direct-mounted vent filter.
- **Each extractor:** pressure cone/four support arms, reclaim platform, rotating blade, adjusting sleeve, tubular chute/outlet, slew bearing/external gear/guard, labyrinth seal, automatic lubrication, two drive assemblies, common VFD and local controls. Each drive opens to motor, coupling, gearbox and pinion. The VFD supplies two 55 kW motors, with individual overload protection. Remote, Local and Maintenance references appear separately.
- **KF-3/4:** motor, delay-filled fluid coupling, gearbox, low-speed coupling, thruster brake, belt/pulleys/idlers, screw take-up, scrapers, skirt/hood, PCS/BSS/ZSS. One pair of PCS and one pair of BSS are preserved as source quantities; two individual devices is explicitly derived. These feeders are not assigned the main conveyors' scoop-coupling/oil-cooler assembly.
- **FG-13/14:** Type 4 casing/doors, flap/shaft, arm, bearings/seals, actuator, motor, manual handwheel, travel/thrust limits.
- **Local DFDS:** ten applications grouped by incoming discharge, feeder discharge and EBA-17 receiving location; FAS, PRU, air/water branches, headers and nozzle groups. Application schedule totals sum to 60 nozzles. Panels and shared System 2 supply remain distinguishable from the local applications.
- **Ventilation:** individual silo vent filters, fans/motors, exhaust ducts, pulse valves, sequential timers, pressure/DP instruments and source-specific control sequence.
- **House services:** service/drinking-water pipework and tank, SP-7A/B drainage pumps, maintenance openings, lifting hooks/hoists and source-stated elevations.

Selecting a component opens its values and source qualifications. Each accepted assertion has its own evidence support; source buttons open the cited page/region and original document. Optional flow animation illustrates documented directions only. It is not plant control or telemetry.

## Accepted data and corrections

228 new descriptive component identities; 1,253 new assertions; 13 older assertions retired with history retained. Active assertions increased from 10,721 to 11,961. No new documents or replacement page renders were imported. There are zero formal model conflicts; this does **not** mean the drawing disagreements below are resolved.

New documented network assertions: 89 utility, 42 control, 40 mechanical, 6 internal material and 4 electrical. Existing top-level material routes were reused.

Corrections include:

- Vendor RE-1/RE-2 records now serve as design references, so the house does not depict four physical extractors. Their numbered applicability is qualified, not a field-verified nameplate merge.
- Six DFDS summaries had read KF-3/4 running-with-load as feeder position. Those summaries were retired and replaced with the actual inputs at their applications. Ambiguous Boolean grouping remains unresolved.
- Two vent-filter summaries had borrowed conditions from the preceding bunker section or overstated silo-dependent stopping. The silo-specific continuous-ventilation sequence is retained instead.
- Coal-flow legend GK/PC is drinking/service water; the older hoist/ventilation interpretation was retired.

## Sources reviewed for this implementation

Original PDFs, extracted text and enlarged drawing regions were inspected locally. The batch files enumerate the exact supporting pages and regions. This is targeted equipment enrichment, not a claim to have re-extracted the whole corpus.

| Document | Used for |
|---|---|
| `doc_4f2cd96c3b1e413ea4b5`, 179162 Rev04 | Coal-flow p55; purpose p5; feeder protection p29; path tables pp40,45,48 |
| `doc_ef73ffa11a1748979909`, 175115 | Extractor design/mechanism pp4–6; mode-specific controls pp6–8; review qualifications |
| `doc_40baa8f059a0427f9567`, 175116 | Extractor GA/BOM/details, liner, bearing, access and review context |
| `doc_17dab58f999c4939bbc7`, 175040 | House GA, vessel/supports, floor location, hoists and technical review replies |
| `doc_396739a89bde48f28f61`, 175031 | Actual GA title/table for KF-3/4, despite misleading imported filename |
| `doc_9258f527621741938b79`, 175065 | Sheet 4 Type 4 flap-gate arrangement and BOM |
| `doc_bca09d68af9b43e3b633`, 175089 | System 2 P&ID sheet 2, ten UEE-2 applications and nozzle schedule |
| `doc_e87ceea2e93c40d7ad8b`, 175298 | Local DFDS/water piping, floor applications, headers and tank |
| `doc_294aacf286d246769e32`, 175265 | Local DFDS philosophy pp21–23 |
| `doc_84156b4bfaae4e6184fe`, 175100 | Direct silo vent-filter schematic, sheet 3 |
| `doc_a786031791b9437d9479`, 175280 | Silo-specific DE control section pp15–16 |
| `doc_0453a0a014424f1cae06`, 175259 | SP-7 pump schedule, local pit and runoff discharge route |

## Outstanding source qualifications

Keep these visible when extending or using the model; do not select an arbitrary winner:

1. FG-14 FWD/REV destination versus running-permissive wording differs across control paths 2, 3 and 4. Two physical outlet branches are supported; commissioned directional logic is not settled.
2. DFDS P&ID panel allocation differs from the philosophy. AP-02/06 list multiple load inputs without an explicit Boolean expression. PS-02 versus PS-02A/B wiring assignment is unresolved.
3. KF-3/4 GA dimensions, take-up and wrap differ from the calculation case. GA motor supply is 3.3 kV; general feeder controls refer to LT conditions. Brake model and coupling brake-drum diameter require reconciliation.
4. VFD siting differs between philosophy/GA and house review reply (MCC near DS-2). Do not turn a schematic position into an as-built room assignment.
5. Potable-water capacity is 300 L in piping, but one GA view says 250 L. UGA-2 pump/compressor-house identity conflicts with an existing dozer-shed label; no merge was performed.
6. Vent-filter control text mixes BU and BS tags and contains a conveyor-feedback note on power restoration. DP thresholds, precise trip timers and final fan-motor selection are not commissioned facts.
7. Lubrication destinations are established. Pump model, lubricant/dose/cycle and a complete hydraulic dust-seal circuit remain unverified. Do not invent an extractor scoop coupling, oil radiator or hydraulic seal circuit.
8. Vendor hopper inputs, design coal temperature and minimum-bed/anti-consolidation notes retain their source basis. They are not commissioned alarm/trip settings or an approved maintenance procedure. Exact device tags, field settings, fire/inerting/CO provisions and field condition need additional applicable records.

## Reproducibility and continuation

- `tools/enrich_silo_pilot.py`: guarded v510-only rehearsal/apply script. **Do not replay on v527.** Accepted per-document proposals and commit log are in `output/silo-pilot/accepted/`.
- `output/silo-pilot/backup-v510.sqlite3`: consistent pre-implementation database backup. Original documents/renders remain in the live data folder; this SQLite file alone is not a full workspace backup.
- `output/silo-pilot/snapshot.json`: source/model inventory baseline; review text, full-page renders and crops under `output/silo-pilot/review/`.
- `tools/audit_silo_pilot.cjs`: semantic audit of the accepted export, covering inlet crossovers, identity boundaries, drives/power, modes, outlets, protection counts, DFDS counts and individual evidence.
- Node projection/scene tests cover the new house boundary logic, exact motor endpoints and mode separation alongside earlier pilots. Integrity verification passed all 266 originals, 5,196 evidence blocks and 527 versions.

Actual browser checks passed for house → extractor → drive → motor → original source crop/full page, the feeder assembly entry, DFDS AP-02's four-nozzle source-linked value, Auto/Manual and Remote/Maintenance reference switching, and the extractor power layer. The two motors remain endpoints of the common VFD, with their drive assemblies used as the extractor-level visual anchors. Desktop inspection used 1440 × 1000; the temporary viewport was then reset and narrow-panel zoom/detail navigation checked. The final browser error/warning check was empty. All 30 projection/scene tests and the v527 semantic audit passed after the final layout changes.

Handoff packages B30/B31 are implemented with the above source qualifications. B14/B29 upstream expansion and crusher-house expansion remain separate work. Preserve the frozen v510 inventory as the historical design baseline; inspect v527 or later before planning a follow-up. Do not duplicate the components or silently overwrite the unresolved source cases.
