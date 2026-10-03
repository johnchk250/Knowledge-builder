# EBA-18A

Planning card at model v628. Package **P12** — EBA-18, UEF-13 and sampling. Primary implementation batch **B36**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p12) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_72888cd70d86451dba02`.
- Existing containment closure: 126 record(s) including root; 44 assertions on root. These are model records, not a count of physical devices.
- Aliases: EBA-18A
- Existing parents: Maitree Coal Handling Plant
- Direct components: EBA-18A Drive assembly, EBA-18A Belt and mechanical assemblies, EBA-18A Belt protection devices, FG-17, QB-3, EAT-3, EBA-18A Discharge chute interface
- Located equipment: QB-3, EAT-3, UEF-13 Local DFDS UBS-05 on EBA-18A

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_52e18b65d3b845fdb786` — GA & LOAD DATA OF BELT CONVEYOR-18 A&B.pdf; available PDF pp. 1–10. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_878e57f585f54e29b031` — 25_METAL DETECTOR.pdf, PDF pp. 16.
- `doc_41860f7c9ac2467bbdb4` — BRG SELECTION & SHELL & DIAPHRAGM THICKNESS CALCULATION FOR CONVEYOR PULLEYS.pdf, PDF pp. 4–5.
- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 3.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 7, 9, 12–13, 17–18, 21–23, 26–29, 39–40, 44–48, 55.
- `doc_957d8f8bd41c4e71be3c` — DRIVE SCHEDULE-.pdf, PDF pp. 2.
- `doc_ea7b9d057938417f822f` — G.A. OF INTERNAL SCRAPPER.pdf, PDF pp. 1.
- `doc_6c1174cd1f294003a5e8` — G.A. OF PRIMARY SCRAPPER.pdf, PDF pp. 1.
- `doc_39a3930034b44154af6b` — G.A. OF SECONDARY SCRAPPER.pdf, PDF pp. 1.
- `doc_52e18b65d3b845fdb786` — GA & LOAD DATA OF BELT CONVEYOR-18 A&B.pdf, PDF pp. 1, 4, 6.
- `doc_a9043e95d82c40f399ec` — GA & MECH LOAD OF TP-13.pdf, PDF pp. 2.
- `doc_558ade05e4644a008b81` — GA OF BELT WEIGHER - Part 1.pdf, PDF pp. 1–7.
- `doc_3898269d389646c1829c` — GA OF BELT WEIGHER - Part 2.pdf, PDF pp. 100–101.
- `doc_64825298f3d243368408` — GA OF BRAKE FOR CHP CONVEYORS.pdf, PDF pp. 5.
- `doc_9258f527621741938b79` — GA OF FLAP GATE.pdf, PDF pp. 1.
- `doc_97e93732778e4618b52b` — GA OF GEAR BOX.pdf, PDF pp. 10.
- `doc_62fdccede7154dc2b8b6` — GA OF GEARED COUPLING.pdf, PDF pp. 3.
- `doc_e09ca845387544f8b9c2` — GA OF IDLERS FOR CHP.pdf, PDF pp. 1.
- `doc_41965812f7d842f3b1ef` — GA OF METAL DETECTOR.pdf, PDF pp. 2, 4, 8, 11–12.
- `doc_7aa49cc0d1c34af7ac06` — GA OF SCOOP TYPE FLUID COUPLING FOR CHP CONVEYORS.pdf, PDF pp. 3, 5, 12, 14.
- `doc_a786031791b9437d9479` — OPERATION & CONTROL PHILOSOPHY OF DUST EXRACTION SYSTEM.pdf, PDF pp. 5.
- `doc_425fb77433564871b40e` — PCS BSS ZSS & BWS-00-EBY-DA-178803-ISG.pdf, PDF pp. 2–4.
- `doc_67a40e7649224ad08ae4` — POWER & BELT TENSION CALC. FOR ALL COAL CONVEYORS EXCEPT BCN-1A&1B.pdf, PDF pp. 112–113, 121.

Existing explicitly applicable reference identities: EBA-18A/18B Power and Belt-Tension Calculation (Rev 03) (`ent_0b9fd890126f4a99975d`), 14ND5 (`ent_296d048c01214d078306`), 14ND1 (`ent_51987f975bc74440b778`), CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), 14DR3 (`ent_6bfc6ac5f1744d6a97dc`), 14ND3 (`ent_9f27545b4c3944169e98`), UEF-13 Coal Sampling System (`ent_cd0c8d6ca3524e98ba13`), CHP HT Conveyor Drive Control Scheme (`ent_dee15248904f4820b982`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| UEE-3 | EBA-18A | No condition recorded; review source | `fact_1434c3d8791c4f9a9d10` |
| EBA-18A | UEF-13 | No condition recorded; review source | `fact_cc8a0c7da213447fb2fb` |
| FG-15 | EBA-18A | Selected downstream conveyor | `fact_e857313292fc4bd5b267` |
| FG-16 | EBA-18A | Selected downstream conveyor | `fact_991e2138b8a541cc8b4b` |
| EBA-18A | FG-17 | No condition recorded; review source | `fact_466816948a474919820d` |
| FG-17 | EBA-19A | Gate REV | `fact_63a06c622bce4408855b` |
| FG-17 | EBA-19B | Gate FWD | `fact_dcc7c9484f844d608435` |
| EBA-18A | EAU-2 Primary Sampler-1 | Sample cut only | `fact_258bc6ba977c4fe8ab9d` |
| FG-15 | EBA-18A | Outlet A selected | `fact_7663770bdcdb434fb5dc` |
| FG-16 | EBA-18A | Outlet A selected | `fact_96e03f5dd4a240aaabbf` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_e2041006d2074b81b9e8` (EBA-18A Belt and mechanical assemblies Flat return rollers): GA flat-return row states 4 but names EBA-6A/6B inside the 18A/B drawing. No per-18 count is inferred from this row; see dedicated idler schedule.
- `fact_e340007d98db498caea0` (EBA-18A Belt and mechanical assemblies Skirt and deck): Seal-plate thickness appears as 31.5 THK. Do not normalize to 3.15 mm or assert an installed 31.5 mm plate; fabrication revision needed.
- `fact_158fb8dd2ad14750a628` (EBA-18A Belt protection devices PCS): Individual switch addresses, cable tags and commissioned loop settings need field records.
- `fact_fcaf9759b8964f1f9bb6` (EBA-18A Belt protection devices BSS): Individual switch addresses, cable tags and commissioned loop settings need field records.
- `fact_f20bfce05f1c40b6a604` (EBA-18A Belt protection devices ZSS): Individual switch addresses, cable tags and commissioned loop settings need field records.
- `fact_165d07b108c6409f9166` (EBA-18A Drive assembly Scoop coupling PST-570): Pump GA flow is 150 L/min; P&I normal circulation row for 570/660 is 140 L/min. The 75°C design maximum, 85°C inlet alarm and >110°C outlet trip have different bases; they are not interchangeable settings.
- `fact_81fe30b5d34549afbf2c` (EBA-18A Drive assembly Scoop coupling PST-570): 500 PST sectional BOM on sheet6 is not a 570-specific bearing/impeller selection. 570 internals and installed maintenance intervals need the matching vendor sectional/O&M record.
- `fact_7205467227aa403f8f0a` (EBA-18A Drive assembly Gearbox B3-500): Gearbox internal gear/bearing selections and overhaul intervals are not resolved by the external GA. Two installed units plus one project spare is a supply total, not three per conveyor.
- `fact_65521ec00c324fa2bd41` (EBA-18A Drive assembly Low-speed geared coupling RG-12): GA supplied in pilot-bore state; installed shaft bores, alignment and final coupling selection require installation records. Schedule totals cover several conveyors and spares.
- `fact_a2e88d1798ef444f94a4` (EBA-18A Drive assembly Thruster brake): Conveyor GA specifies EBTF-600/G. Brake sheet5 labels EBTM-600/G and EAC-18A/B, whereas canonical tags are EBA-18A/B. 600 mm and 500 kW/1488 rpm align; installed model/nameplate remains unresolved.
- `fact_7f4659c30bf0430e8ad7` (EBA-18A Belt and mechanical assemblies Head pulley Keyless locking assembly): Do not use adjacent catalogue torque rows as the installed tightening procedure. Confirm exact supplied size/manual before maintenance.
- `fact_4dc62b8a3e4543d89322` (EBA-18A Belt and mechanical assemblies Carrying idlers): Conveyor GA gives 435 carrying sets per conveyor; dedicated idler schedule gives 431+431 for 18A/B. Final installed quantity needs reconciliation.
- `fact_a2731fc25e8740a69568` (EBA-18A Belt and mechanical assemblies Nonmagnetic idlers): GA states 4 per conveyor, dedicated schedule gives 2+2 for the 18A/B pair. Preserve both; do not treat project pair total as a per-machine quantity.
- `fact_59fa7b62c2f043de9faa` (QB-3): Detector GA design speed 2.6 m/s differs from conveyor18 GA 2.7 m/s. Compliance review also requests small ferrous/nonferrous pieces. Field sensitivity tests/final vendor approval are required.
- `fact_c0254aaef74243a6b227` (QB-3): DCS IO table p12 maps ON T25/26, fault T22/23/24 and metal T27/28; wiring p11 labels relays differently. No definitive field terminal mapping is inferred.
- `fact_cd0c062ac77545a893a7` (QB-3): Support height is explicitly determined at site. Sensitivity, serial numbers, field cable lengths and final IP protection of hooter remain unresolved.
- `fact_1dce4d8f92b944fdba97` (EAT-3): Drawing group totals of8 units cover several conveyor pairs, not8 per18 conveyor. Installed calibration results, load-cell serials and weighed-idler alignment require records.
- `fact_f6e82ab1c6de4a0298ac` (EBA-18A Drive assembly Scoop coupling PST-570 Scoop actuator): CBS permissive says both not operated; trip wording also says CBS not operated. Polarity remains unresolved. Vendor DPS gives alarm only; general control-write-up differential-pressure wording needs action-target reconciliation.
- `fact_408f6bc3ea334de78f97` (FG-17): Gate control text p12 gives approximately 2 min anti-jam reversal; p13 gives conveyor-off T1=10 s/return T2=5 s and feeding-conveyor-off T1=4 h/return T2=120 s. The modes and conflicting requirements are retained without a commissioned timer selection.
- `fact_1bee3ad4506f45f0974d` (EBA-18A Drive assembly Gearbox B3-500): Drive schedule thermal rating905 kW differs from gearbox GA633 kW at50°C. Nominal28.4 versus exact29.2 is a documented distinction, not itself a conflict. Verify thermal selection/ambient derating and installed nameplate.
- `fact_c912ed58b2484790a3ea` (EBA-18A Drive assembly): Drive schedule uses EAC18A/18B rather than EBA18A/18B; electrical tolerance ±6% and frequency+3%/-5% differ from conveyor GA±10% and±5%. Component sizes align; installed motor record needed.
- `fact_b4167ffedbb24096984d` (EBA-18A Belt and mechanical assemblies Skirt and deck): Calculation input skirt length10 m differs from GA total18 m; confirm design revision and the skirting-length basis used in resistance calculation.
- `fact_2b848ad066674c7ba3cd` (EBA-18A Belt and mechanical assemblies Deflector pulley group): Calculation inputs p113 give one deflector with243 mm external diameter; GA gives two219 mm deflector rollers. Quantity/revision and bare-versus-external-diameter basis require reconciliation.
- `fact_dd0d0dadba1f43e5a9e6` (EBA-18A): Calculation profile472.184 m differs from GA471.943 m; calculated motor-shaft power392 kW differs from coupling consumed-power basis382 kW. Keep source-qualified calculation/selection values.
- `fact_eb9be349092b46e49f13` (EBA-18A Belt protection devices): Supplier package pp5–25 contains group panels/auxiliary families without a verified18A/B panel or address schedule. Do not attach a specific panel number, individual switch address or cable tag without conveyor-specific wiring/commissioning records.
- `fact_baee03962a4f489eae89` (EBA-18A Drive assembly Thruster brake): Coasting table selects EBTM600/G and gives440 maximum torque and160 applied torque; drive schedule givesEBTF600/G and495 kg-m rated torque. Rated and assumed applied torque have different meanings; model/rating disagreement still needs final brake selection and field test record.
- `fact_6e34ed037ce745ffba1b` (EBA-18A Belt and mechanical assemblies): Calculation p113 lists drive-bearing diameter280mm, non-drive tail/take-up/bend160mm and snub140mm. Later selection p4/5 uses different selected shaft diameters at bearings (drive260mm, take-up220mm, tail/snub180mm). Final shaft/BOM revision and bearing-fit record are needed; catalogue bearing model is design selection only.
