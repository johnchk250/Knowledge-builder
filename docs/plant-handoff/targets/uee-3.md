# UEE-3

Planning card at model v628. Package **P11** — Crusher house and EBA-17. Primary implementation batch **B32**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p11) and [family contract](../ASSEMBLY_CONTRACTS.md#crusher) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_f3a25812c42246d3b167`.
- Existing containment closure: 416 record(s) including root; 14 assertions on root. These are model records, not a count of physical devices.
- Aliases: UEE-3
- Existing parents: Maitree Coal Handling Plant
- Direct components: Crusher House Passenger and Goods Elevator, Crusher House Warning Hooter (Hooter-14), KF-1, KF-2, DE-1, DE-2, EBC-1, EBD-5, FG-15A, FG-15, EBC-2, EBD-6, FG-15B, FG-16, UEE-3 Maintenance access and lifting, Crusher House DE System DE-1 and DE-2, UEE-3 Local DFDS, UEE-3 Service and drinking water, UEE-3 Drainage sump and pumps
- Located equipment: FG-15A, EBD-5, EBC-1, KF-1, FG-15B, EBD-6, EBC-2, KF-2, FG-15, FG-16, Crusher House Passenger and Goods Elevator, DFDSS-2 PS-09, EBA-17A, EBA-17B, EBA-18A Belt and mechanical assemblies Tail bend and take-up pulley group Tail pulley, EBA-18B Belt and mechanical assemblies Tail bend and take-up pulley group Tail pulley

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **crusher** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_9c169bf7536b4ebca236` — COAL FLOW DIAGRAM.pdf, PDF pp. 1.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 5, 14–17, 29, 39–40, 44–45, 47–48, 53, 55.
- `doc_d4f7140726b240f7b479` — DESIGN BASIS REPORT OF DE SYSTEM.pdf, PDF pp. 2.
- `doc_c30c2201121e44798c9d` — DESIGN MEMORANDUM OF ELEVATOR FOR CHP.pdf, PDF pp. 4.
- `doc_3b65e744297d4a028320` — DUCTING LAYOUT FOR DE SYSTEM AT CRH.pdf, PDF pp. 3.
- `doc_2426398655e74c2fb4df` — G.A & Details of HooterSiren.pdf, PDF pp. 2.
- `doc_d4f87b906a964bd58c17` — G.A. OF VIBRATION ISOLATION SYSTEM FOR CRUSHERS.pdf, PDF pp. 1.
- `doc_52e18b65d3b845fdb786` — GA & LOAD DATA OF BELT CONVEYOR-18 A&B.pdf, PDF pp. 6.
- `doc_3aed51331d5243ab85ab` — GA & LOAD DATA OF BELT FEEDER 1 & 2 AT CRH.pdf, PDF pp. 1.
- `doc_e082675ac82d4ad280d2` — GA & MECH LOAD OF CRUSHER HOUSE.pdf, PDF pp. 1, 6–7.
- `doc_7263469a9d61411dbe04` — GA OF BAGFILTER FOR DE SYSTEM.pdf, PDF pp. 4.
- `doc_ae2f48499fd7429fad60` — GA OF CENTRIFUGAL FANS FOR DE SYSTEM.pdf, PDF pp. 2.
- `doc_f608e15aedbf4f368692` — GA OF CRUSHER (RING GRANULATOR).pdf, PDF pp. 1.
- `doc_4079754720fe4b6891c1` — GA OF ELEVATOR AT CRH.pdf, PDF pp. 1, 10.
- `doc_9258f527621741938b79` — GA OF FLAP GATE.pdf, PDF pp. 1, 5.
- `doc_799aadaacc6e481e8595` — GA OF ROTARY AIR LOCK VALVE FOR DE SYSTEM.pdf, PDF pp. 1–2.
- `doc_624bd9eb971746e293a8` — GA OF SCOOP TYPE COUPLING FOR CRUSHER.pdf, PDF pp. 1–2, 12.
- `doc_4581250ffd114bacba82` — GA OF VIBRATING GRIZZLY FEEDER (INCLUDING TECH. DATA SHEET).pdf, PDF pp. 1–2, 4.
- `doc_294aacf286d246769e32` — OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf, PDF pp. 29–31.
- `doc_a786031791b9437d9479` — OPERATION & CONTROL PHILOSOPHY OF DUST EXRACTION SYSTEM.pdf, PDF pp. 3, 5–11.
- `doc_bca09d68af9b43e3b633` — P & ID FOR DFDS SYSTEM.pdf, PDF pp. 2.
- `doc_0453a0a014424f1cae06` — P & ID FOR SUMP PUMP & STOCK YARD RUNOFF WATER PUMP SYSTEM.pdf, PDF pp. 1.
- `doc_ba5c790519f14234851a` — POWER & BELT TENSION CALC. FOR BELT FEEDER.pdf, PDF pp. 2–4.
- `doc_a58b0c516ef3413db6c0` — Piping Layout for DFDS, SW & PW System at UEE-3.pdf, PDF pp. 1, 3.
- `doc_84156b4bfaae4e6184fe` — SCHEMATIC DIAGRAM FOR DE SYSTEM.pdf, PDF pp. 1.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| UEE-3 | EBA-18A | No condition recorded; review source | `fact_1434c3d8791c4f9a9d10` |
| UEE-3 | EBA-18B | No condition recorded; review source | `fact_0915444e034f4429ad82` |
| FG-13 | EBA-17A | Selected downstream conveyor; direction assignments require reconciliation | `fact_00c009d0811146d5aa3d` |
| FG-13 | EBA-17B | Selected downstream conveyor; direction assignments require reconciliation | `fact_897f4ca4bd1f46618fd5` |
| FG-14 | EBA-17A | Selected downstream conveyor; direction assignments require reconciliation | `fact_bf5ce0d9e64f4a06b22f` |
| FG-14 | EBA-17B | Selected downstream conveyor; direction assignments require reconciliation | `fact_b7ceb21f175b42a58c2c` |
| EBA-17A | FG-15A | No condition recorded; review source | `fact_ce8aac2be5764dff9fb7` |
| FG-15A | EBD-5 | Gate FWD: screening/crushing selected | `fact_1589c991a1314911beb5` |
| FG-15A | KF-1 | Gate REV: crusher-house bypass selected | `fact_82427b68ba4546faaca3` |
| EBA-17B | FG-15B | No condition recorded; review source | `fact_45f25673f8994451a1db` |
| FG-15B | EBD-6 | Gate FWD: screening/crushing selected | `fact_2b2588f496ba46aba1eb` |
| FG-15B | KF-2 | Gate REV: crusher-house bypass selected | `fact_55446b60756a45c98a38` |
| EBD-5 | EBC-1 | Oversize +20 mm | `fact_1051da9400424381a4b2` |
| EBD-5 | KF-1 | Undersize -20 mm bypasses crusher | `fact_07bd560f56b540d6ac57` |
| EBC-1 | KF-1 | Crushed coal | `fact_a029f39e96704c91b110` |
| KF-1 | FG-15 | No condition recorded; review source | `fact_ecc1a9baa7f44d708f75` |
| FG-15 | EBA-18A | Selected downstream conveyor | `fact_e857313292fc4bd5b267` |
| FG-15 | EBA-18B | Selected downstream conveyor | `fact_002aad30c9a042659814` |
| EBD-6 | EBC-2 | Oversize +20 mm | `fact_6636bddad0e347958fa1` |
| EBD-6 | KF-2 | Undersize -20 mm bypasses crusher | `fact_8672afd6b8a544d0b9ba` |
| EBC-2 | KF-2 | Crushed coal | `fact_aa4644756f8e4c7f92af` |
| KF-2 | FG-16 | No condition recorded; review source | `fact_4ac417b174eb4dbfa8bb` |
| FG-16 | EBA-18A | Selected downstream conveyor | `fact_991e2138b8a541cc8b4b` |
| FG-16 | EBA-18B | Selected downstream conveyor | `fact_4949d0092a634883b68c` |
| EBA-17A | FG-15A | Incoming coal | `fact_664e6554e9e14299995b` |
| FG-15A | EBD-5 | Screening route | `fact_7bea5f832caa4ffbbe99` |
| FG-15A | KF-1 | Direct bypass selected | `fact_50af8df79ca14bb1aba6` |
| EBD-5 | EBC-1 | Screen oversize | `fact_70dc680f38cd43a8a902` |
| EBD-5 | KF-1 | Screen undersize | `fact_185f2921d4be4133b00d` |
| EBC-1 | KF-1 | Crushed product | `fact_6580c004ead24307a7c5` |
| KF-1 | FG-15 | Feeder discharge | `fact_f1e32aba07c045ffa515` |
| FG-15 | EBA-18A | Outlet A selected | `fact_7663770bdcdb434fb5dc` |
| FG-15 | EBA-18B | Outlet B selected | `fact_46256d353bfa49879862` |
| EBA-17B | FG-15B | Incoming coal | `fact_1b73fb919150403b93f9` |
| FG-15B | EBD-6 | Screening route | `fact_1fdf5f4b2e4247029fb4` |
| FG-15B | KF-2 | Direct bypass selected | `fact_5bc3716e836d4244a5c5` |
| EBD-6 | EBC-2 | Screen oversize | `fact_bbf422a7662845a8aaa0` |
| EBD-6 | KF-2 | Screen undersize | `fact_b58d818e433c4adab6e1` |
| EBC-2 | KF-2 | Crushed product | `fact_c583169502984e2e975b` |
| KF-2 | FG-16 | Feeder discharge | `fact_15916508c03747f7a549` |
| FG-16 | EBA-18A | Outlet A selected | `fact_96e03f5dd4a240aaabbf` |
| FG-16 | EBA-18B | Outlet B selected | `fact_7d5a00ef5cfb45aebe8b` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_f2fac0660cd74d0d88b9` (EBD-5): Control narrative p5 calls the crusher-house pair EBD-1/2, but flow p55 identifies EBD-5/6; primary EBD-1–4 are different assets. No identity merge or alias is established.
- `fact_8598a306091b46e8be70` (EBD-6): Control narrative p5 calls the crusher-house pair EBD-1/2, but flow p55 identifies EBD-5/6; primary EBD-1–4 are different assets. No identity merge or alias is established.
- `fact_15e7c2e63628408c977a` (EBC-1): Two machines are one LH and one RH; reviewed machine GA alone does not map handedness to EBC-1 versus EBC-2. Shaft/bearing selection remains design data.
- `fact_728403f7b74b4c0f800f` (EBC-1 Hydraulic opening system Power pack): Hydraulic motor rating, pump duty, oil grade/volume, valve circuit and commissioned pressure are not established by the reviewed crusher GA.
- `fact_9643e61b5638479c8896` (EBC-1 Protection and monitoring Rotor bearing RTDs): GA bearing alarm/trip80/90 degC differs from crusher control p16/17 rotor-bearing scoop permission <=70 and disengagement >80 degC. Motor bearing limits are separate. Do not choose a commissioned setting from these documents.
- `fact_89ac829932224a2ba0b2` (EBC-1 Drive assembly Scoop coupling PST-1150 Scoop actuator Motor): GA detailed box and actuator datasheet give0.1/0.25kW; a separate GA notes line says0.37kW. Speed labels for8/4second engagement also differ from datasheet685/1380rpm. Final actuator selection/timing needs reconciliation.
- `fact_889dccd55168484a82d2` (EBC-1 Drive assembly Scoop coupling PST-1150): P&I TS1/TS2 alarm/trip>85/>110degC coexists with GA maximum operating oil75degC and review request to restrict maximum75degC. These are different reported limits, not verified commissioned settings. P&I nominal flow405L/min differs from GA pump415L/min.
- `fact_4e20ab618fa1435a8afb` (EBC-1 Drive assembly Scoop coupling PST-1150): Local terminal/relay drawings are retained in source sheets5–11; field cable/MCC assignment and commissioned cause/effect are not established by the GA/P&I.
- `fact_f4d3486119264cc7ba16` (EBD-5): GA design capacity1375t/h; selection/calculation headings state1370t/h. Preserve the difference pending reconciliation.
- `fact_02f3d1f600c8413086f0` (EBD-5 Springs and supports): Spring supports isolate mechanical vibration; no separate vibration trip instrument is established by this GA. Exciter bearing/lubricant details need applicable vendor maintenance data.
- `fact_60eae6c577fd4c109b41` (EBC-2): Two machines are one LH and one RH; reviewed machine GA alone does not map handedness to EBC-1 versus EBC-2. Shaft/bearing selection remains design data.
- `fact_0a9558e5656847009d2c` (EBC-2 Hydraulic opening system Power pack): Hydraulic motor rating, pump duty, oil grade/volume, valve circuit and commissioned pressure are not established by the reviewed crusher GA.
- `fact_ed66404907964a2e9611` (EBC-2 Protection and monitoring Rotor bearing RTDs): GA bearing alarm/trip80/90 degC differs from crusher control p16/17 rotor-bearing scoop permission <=70 and disengagement >80 degC. Motor bearing limits are separate. Do not choose a commissioned setting from these documents.
- `fact_28973e0ec6c9455c9876` (EBC-2 Drive assembly Scoop coupling PST-1150 Scoop actuator Motor): GA detailed box and actuator datasheet give0.1/0.25kW; a separate GA notes line says0.37kW. Speed labels for8/4second engagement also differ from datasheet685/1380rpm. Final actuator selection/timing needs reconciliation.
- `fact_3330c70d7e474c96a901` (EBC-2 Drive assembly Scoop coupling PST-1150): P&I TS1/TS2 alarm/trip>85/>110degC coexists with GA maximum operating oil75degC and review request to restrict maximum75degC. These are different reported limits, not verified commissioned settings. P&I nominal flow405L/min differs from GA pump415L/min.
- `fact_dd79f488c0244525baeb` (EBC-2 Drive assembly Scoop coupling PST-1150): Local terminal/relay drawings are retained in source sheets5–11; field cable/MCC assignment and commissioned cause/effect are not established by the GA/P&I.
- `fact_3db5980ddb284ee0947c` (EBD-6): GA design capacity1375t/h; selection/calculation headings state1370t/h. Preserve the difference pending reconciliation.
- `fact_91139e03b30146e2b133` (EBD-6 Springs and supports): Spring supports isolate mechanical vibration; no separate vibration trip instrument is established by this GA. Exciter bearing/lubricant details need applicable vendor maintenance data.
- `fact_d4799a51c6d54476b786` (KF-1 Drive assembly Thruster brake): Local GA establishes a thruster brake. Exact thruster model, fluid grade/fill and brake-release switch field tag require the applicable vendor detail; do not copy another conveyor size.
- `fact_597b19fe822c4a678d26` (KF-2 Drive assembly Thruster brake): Local GA establishes a thruster brake. Exact thruster model, fluid grade/fill and brake-release switch field tag require the applicable vendor detail; do not copy another conveyor size.
- `fact_cc358c4ed1cb415c9992` (KF-1): General feeder section calls drive LT; KF1/2 GA specifies3.3kV motor. Retain source-specific wording and verify switchgear designation.
- `fact_609adc00faae4ac68908` (KF-2): General feeder section calls drive LT; KF1/2 GA specifies3.3kV motor. Retain source-specific wording and verify switchgear designation.
- `fact_60decb75da6649a18837` (UEE-3 Maintenance access and lifting Monorails and hoists): House hoist schedule names EBD1/2 and FG16A; flow diagram establishes secondary EBD5/6 and bypass FG15A/B. Capacities retained with exact schedule scope; ambiguous hoist-to-screen/gate assignments are not silently corrected.
- `fact_b247e8d908454dffbe84` (FG-15A): Bypass gate added on flow Rev8 and house GA; reviewed older generic flap-gate175065 sheets do not schedule FG15A/B. Do not borrow FG15/16 actuator ratings.
- `fact_3a1b5da2ced04af4b02e` (FG-15B): Bypass gate added on flow Rev8 and house GA; reviewed older generic flap-gate175065 sheets do not schedule FG15A/B. Do not borrow FG15/16 actuator ratings.
- `fact_98c44c276c1043da8a2e` (FG-15): Type5 schedule location column repeats KF-1 for FG-16, while marking/casing code identifies KF-2 and process drawing connects KF-2 to FG-16. Preserve distinct gate identities.
- `fact_88192b9e264f487b8cfa` (FG-16): Type5 schedule location column repeats KF-1 for FG-16, while marking/casing code identifies KF-2 and process drawing connects KF-2 to FG-16. Preserve distinct gate identities.
- `fact_be6aab033cad40b4bfae` (Crusher House DE System DE-1 and DE-2): Schematic upper schedule lists5 motorized dampers, while tagged layout/lower schedule and philosophy identify MD-CH-001 through006. Six identities retained without silently editing either source.
- `fact_4aa14e10037441478aaa` (Crusher House DE System DE-1 and DE-2 Compressed-air connection): Schematic connects to compressor house. Shared compressor/dryer data remain plant utility references; dedicated UEE-3 compressor assets are not established.
- `fact_587d01507da54ae0aa93` (Crusher House DE System DE-1 and DE-2): Philosophy contains copied tags: p6 stop clause says RAL003 where stream1 starts001/002/005; stream2 timer clause mentions PS001; interchange2 stop clause lists001/003/005 where start list is001/002/005. Preserve mode intent and unresolved exact logic; do not execute copied sequences as commissioning instructions.
- `fact_568b8de6ac154ec8ae00` (DE-1 Bag-filter compartment Bags and cages): Combined GA says480 bags each compartment and480 in assembly BOM; model2x20x12 and two35900m3/h streams leave count basis ambiguous. Do not infer240 or480 per DE stream without reconciliation.
- `fact_8cc77603dedd413aba6b` (DE-2 Bag-filter compartment Bags and cages): Combined GA says480 bags each compartment and480 in assembly BOM; model2x20x12 and two35900m3/h streams leave count basis ambiguous. Do not infer240 or480 per DE stream without reconciliation.
- `fact_3183435fd1af4c519c82` (FAN-CH-001): Schematic175100 lists110kW tentative pending GA; this later FIO fan GA selects90kW. Also GA says fan quantity01 despite system1&2 applicability. Retain two process fan identities established by schematic and philosophy; procurement/installed count and motor nameplate remain to verify.
- `fact_79d3238b102d4d6dba01` (FAN-CH-002): Schematic175100 lists110kW tentative pending GA; this later FIO fan GA selects90kW. Also GA says fan quantity01 despite system1&2 applicability. Retain two process fan identities established by schematic and philosophy; procurement/installed count and motor nameplate remain to verify.
- `fact_62d1bd66a0974aec981e` (UEE-3 Local DFDS): Application schedule misprints UEF-3 (Crusher House); sheet schematic, local panel and piping identify UEE-3. Identical AP/FAS/PRU numbers also occur in DFDS System1; identities are scoped to UEE-3/System2.
- `fact_5b0e0d4f76fa4e00b8b8` (UEE-3 Local DFDS): Philosophy uses EBA17 running-with-load for KF discharge sprays rather than KF feedback, and does not explicitly resolve residual feeder discharge after EBA17 stops or screening/direct-bypass cases. Verify final logic; no automatic substitution is made.
- `fact_55302a55bfe94a7e9871` (EBC-1 Drive assembly Scoop coupling PST-1150 Oil circulation pump): Start/stop description says30s adjustable stop delay; trip list says300s after main motor OFF. Retain both clauses; final cause/effect and timer settings need reconciliation.
- `fact_27bdbd2c124b4097adad` (EBC-1 Drive assembly Scoop coupling PST-1150 Scoop actuator): Engage permissive requires both CBS NOT operated, while disengage clause says ANY CBS NOT operated. Likely wording error is not corrected into an executable rule; reconcile with approved logic and field verification.
- `fact_be4ed0df6c5e44ee9b91` (EBC-2 Drive assembly Scoop coupling PST-1150 Oil circulation pump): Start/stop description says30s adjustable stop delay; trip list says300s after main motor OFF. Retain both clauses; final cause/effect and timer settings need reconciliation.
- `fact_f9bea946c2f44755a74f` (EBC-2 Drive assembly Scoop coupling PST-1150 Scoop actuator): Engage permissive requires both CBS NOT operated, while disengage clause says ANY CBS NOT operated. Likely wording error is not corrected into an executable rule; reconcile with approved logic and field verification.
- `fact_2114b2e5d4c246938798` (Crusher House Passenger and Goods Elevator): GA lists protective features but does not establish present inspection status, emergency procedures, brake/safety-gear settings or a verified isolation plan. Detailed vendor and commissioned maintenance records remain required.
- `fact_7c729d367c7941fb9186` (RAL-CH-001): RAL GA states20rpm; compare the separately sourced bag-filter output-speed facts on the applicable geared motors. Review requests wear-resistant lining while vendor reply asks acceptance of MS fabricated casing/rotor. Final installed speed and material remain to verify.
- `fact_288a6e7f4ff14a48874f` (RAL-CH-002): RAL GA states20rpm; compare the separately sourced bag-filter output-speed facts on the applicable geared motors. Review requests wear-resistant lining while vendor reply asks acceptance of MS fabricated casing/rotor. Final installed speed and material remain to verify.
- `fact_dc5e07777c2f41228c2d` (RAL-CH-003): RAL GA states20rpm; compare the separately sourced bag-filter output-speed facts on the applicable geared motors. Review requests wear-resistant lining while vendor reply asks acceptance of MS fabricated casing/rotor. Final installed speed and material remain to verify.
- `fact_2c78449103a249b6bf50` (RAL-CH-004): RAL GA states20rpm; compare the separately sourced bag-filter output-speed facts on the applicable geared motors. Review requests wear-resistant lining while vendor reply asks acceptance of MS fabricated casing/rotor. Final installed speed and material remain to verify.
- `fact_4b7799511fdf40cdb0a3` (RAL-CH-005): RAL GA states20rpm; compare the separately sourced bag-filter output-speed facts on the applicable geared motors. Review requests wear-resistant lining while vendor reply asks acceptance of MS fabricated casing/rotor. Final installed speed and material remain to verify.
