# Coal Blending Silo House

Planning card at model v628. Package **P10** — Blending silos and extraction. Primary implementation batch **B30**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p10) and [family contract](../ASSEMBLY_CONTRACTS.md#silo) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_5d8ffc4cfe6c4d8a92bb`.
- Existing containment closure: 270 record(s) including root; 16 assertions on root. These are model records, not a count of physical devices.
- Aliases: UEE-2, Coal Blending Silo House, CBSH
- Existing parents: Maitree Coal Handling Plant
- Direct components: KF-3, KF-4, Blending Silo EBB-1/EBB-2 Vent-Filter DE System, EBE-CES-1, EBE-CES-2, EBB-1, FG-13, EBB-2, FG-14, UEE-2 Maintenance access and lifting, UEE-2 Local DFDS, UEE-2 Service and drinking water, UEE-2 Sump Pumps SP-7A/7B
- Located equipment: EBB-1, KF-3, FG-13, EBB-2, KF-4, FG-14, DFDSS-2 PS-02A, DFDSS-2 PS-02B

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **silo, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_9c169bf7536b4ebca236` — COAL FLOW DIAGRAM.pdf, PDF pp. 1.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 5, 29, 40, 45, 48, 55.
- `doc_ef73ffa11a1748979909` — DESIGN BASIS & OPERATION PHILOSOPHY OF BLENDING SILO.pdf, PDF pp. 4–8.
- `doc_396739a89bde48f28f61` — G.A. & LOAD DATA OF BELT FEEDER-1 & 2 AT CBSH.pdf, PDF pp. 1.
- `doc_17dab58f999c4939bbc7` — GA & MECH LOAD OF CBSH.pdf, PDF pp. 1, 4–7.
- `doc_9258f527621741938b79` — GA OF FLAP GATE.pdf, PDF pp. 4.
- `doc_40baa8f059a0427f9567` — GA OF SILO EXTRACTION SYSTEM.pdf, PDF pp. 1.
- `doc_294aacf286d246769e32` — OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf, PDF pp. 21–23, 31.
- `doc_a786031791b9437d9479` — OPERATION & CONTROL PHILOSOPHY OF DUST EXRACTION SYSTEM.pdf, PDF pp. 4, 15–16.
- `doc_bca09d68af9b43e3b633` — P & ID FOR DFDS SYSTEM.pdf, PDF pp. 2.
- `doc_0453a0a014424f1cae06` — P & ID FOR SUMP PUMP & STOCK YARD RUNOFF WATER PUMP SYSTEM.pdf, PDF pp. 1.
- `doc_ba5c790519f14234851a` — POWER & BELT TENSION CALC. FOR BELT FEEDER.pdf, PDF pp. 2–4.
- `doc_e87ceea2e93c40d7ad8b` — Piping Layout for DFDS, SW & PW System at UEE-2.pdf, PDF pp. 1–3.
- `doc_84156b4bfaae4e6184fe` — SCHEMATIC DIAGRAM FOR DE SYSTEM.pdf, PDF pp. 3.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EBA-6A | Coal Blending Silo House | No condition recorded; review source | `fact_9151c5c4a1b84210b35a` |
| EBA-6B | Coal Blending Silo House | No condition recorded; review source | `fact_2143a4b2fa044e35ab45` |
| EBA-6A | EBB-2 | Corresponding silo not at high level | `fact_fe225482053943a58073` |
| EBA-6B | EBB-1 | Corresponding silo not at high level | `fact_8eb4e71722eb4cd9a530` |
| EBA-16A | EBB-1 | Corresponding silo not at high level | `fact_a2e6199beba14e94a75d` |
| EBA-16B | EBB-2 | Corresponding silo not at high level | `fact_8525d8d5a90542509ebb` |
| EBB-1 | EBE-CES-1 | No condition recorded; review source | `fact_0acbd16833d14ba5bc09` |
| EBE-CES-1 | KF-3 | No condition recorded; review source | `fact_aecf9acb41ce4ce0bdd4` |
| KF-3 | FG-13 | No condition recorded; review source | `fact_2aa60b29c9444712a430` |
| FG-13 | EBA-17A | Selected downstream conveyor; direction assignments require reconciliation | `fact_00c009d0811146d5aa3d` |
| FG-13 | EBA-17B | Selected downstream conveyor; direction assignments require reconciliation | `fact_897f4ca4bd1f46618fd5` |
| EBB-2 | EBE-CES-2 | No condition recorded; review source | `fact_c4283ca9fa2d4c4c9c96` |
| EBE-CES-2 | KF-4 | No condition recorded; review source | `fact_740c9764dfb942719039` |
| KF-4 | FG-14 | No condition recorded; review source | `fact_0f3b0781a5d74afda8de` |
| FG-14 | EBA-17A | Selected downstream conveyor; direction assignments require reconciliation | `fact_bf5ce0d9e64f4a06b22f` |
| FG-14 | EBA-17B | Selected downstream conveyor; direction assignments require reconciliation | `fact_b7ceb21f175b42a58c2c` |
| EBE-CES-1 Rotating blade | EBE-CES-1 Rotating tubular chute | No condition recorded; review source | `fact_5a22d09a5da74568a671` |
| EBE-CES-1 Rotating tubular chute | EBE-CES-1 Rotating tubular chute Conical outlet | No condition recorded; review source | `fact_211a179479e342dbbdeb` |
| EBE-CES-1 Rotating tubular chute Conical outlet | KF-3 | No condition recorded; review source | `fact_28ee5a683eb846d4bf80` |
| EBE-CES-2 Rotating blade | EBE-CES-2 Rotating tubular chute | No condition recorded; review source | `fact_0799b21cba5340548de1` |
| EBE-CES-2 Rotating tubular chute | EBE-CES-2 Rotating tubular chute Conical outlet | No condition recorded; review source | `fact_ff268d8421a64de8bc6c` |
| EBE-CES-2 Rotating tubular chute Conical outlet | KF-4 | No condition recorded; review source | `fact_89a7b01601714d5a907c` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_ba66f3a47ba644e288de` (EBE-CES-1 Automatic lubrication): Reviewed GA and philosophy identify the lubrication destinations but do not establish pump model, lubricant grade, dosage, cycle setting or a separate hydraulic dust-seal circuit.
- `fact_ddc228d18a1441158c3d` (EBE-CES-1 Drive assembly 1): Gearbox ratio, coupling model, bearing part numbers and installed motor identification are not established by these reviewed pages.
- `fact_9f5c1dd7a05f4bbf9cb3` (EBE-CES-1 Drive assembly 2): Gearbox ratio, coupling model, bearing part numbers and installed motor identification are not established by these reviewed pages.
- `fact_b871297081574b2a86a0` (EBE-CES-1): Earlier review response broadly lists a reverse pushbutton for local operation; revised main text separates Local forward start from Maintenance forward/reverse. Keep mode-specific main-text conditions and confirm commissioned logic.
- `fact_0b75071838164aefb18c` (EBE-CES-2 Automatic lubrication): Reviewed GA and philosophy identify the lubrication destinations but do not establish pump model, lubricant grade, dosage, cycle setting or a separate hydraulic dust-seal circuit.
- `fact_f6800fdce8dc45cf97cd` (EBE-CES-2 Drive assembly 1): Gearbox ratio, coupling model, bearing part numbers and installed motor identification are not established by these reviewed pages.
- `fact_ba0e9febb0614e15be3e` (EBE-CES-2 Drive assembly 2): Gearbox ratio, coupling model, bearing part numbers and installed motor identification are not established by these reviewed pages.
- `fact_35c5e99c39644bdd98ca` (EBE-CES-2): Earlier review response broadly lists a reverse pushbutton for local operation; revised main text separates Local forward start from Maintenance forward/reverse. Keep mode-specific main-text conditions and confirm commissioned logic.
- `fact_ad7b46685f5a4413bbca` (EBE-CES-1): GA lists automatic lubrication for slew bearing and drives but gives no complete hydraulic dust-seal circuit requested in philosophy review. Treat that circuit and its settings as unresolved.
- `fact_42eff5ee12264bd89ca8` (EBE-CES-1 Common VFD): Extractor GA indicates a panel enclosure between silos near EL+17.500 m. CBSH review p7 instead states an air-conditioned MCC room near DS Pump House-2; installed panel location remains unverified.
- `fact_f9f8625789e245f0a62f` (EBE-CES-2): GA lists automatic lubrication for slew bearing and drives but gives no complete hydraulic dust-seal circuit requested in philosophy review. Treat that circuit and its settings as unresolved.
- `fact_4878983c28a54eae974d` (EBE-CES-2 Common VFD): Extractor GA indicates a panel enclosure between silos near EL+17.500 m. CBSH review p7 instead states an air-conditioned MCC room near DS Pump House-2; installed panel location remains unverified.
- `fact_27041a01cfb34f1a95e6` (EBB-1 Level and temperature instruments Level indication): GA notes establish the provision, not an installed tag, measurement range or alarm/trip setpoint.
- `fact_304e3dc38bea4a8e93a1` (EBB-1 Level and temperature instruments Temperature detector): GA notes establish the provision, not an installed tag, measurement range or alarm/trip setpoint.
- `fact_4e432eac47254430997b` (EBB-1 Emergency bypass chute): Bypass chute and rod gate are documented; discharge endpoint and operating/isolation procedure are not established by these reviewed views.
- `fact_09b6a19f49e2478c8def` (EBE-CES-1 Common VFD): CBSH review reply differs from extractor GA/philosophy showing a silo-building panel. Retain both source locations; verify latest electrical GA and field installation.
- `fact_c76cadd4f25941aba45f` (EBB-2 Level and temperature instruments Level indication): GA notes establish the provision, not an installed tag, measurement range or alarm/trip setpoint.
- `fact_fbf58bb225214ff4957c` (EBB-2 Level and temperature instruments Temperature detector): GA notes establish the provision, not an installed tag, measurement range or alarm/trip setpoint.
- `fact_d597f67a59b447159168` (EBB-2 Emergency bypass chute): Bypass chute and rod gate are documented; discharge endpoint and operating/isolation procedure are not established by these reviewed views.
- `fact_dff2b9a7def442da9391` (EBE-CES-2 Common VFD): CBSH review reply differs from extractor GA/philosophy showing a silo-building panel. Retain both source locations; verify latest electrical GA and field installation.
- `fact_85f68b7ab1ca4b95a6cc` (KF-3 Drive assembly Thruster brake): GA coupling row gives brake drum diameter 250 mm while brake model row says EBTM 300/H; reconcile brake GA/drive schedule before selecting spares.
- `fact_61f9058ce4954d5db5de` (KF-3): GA table gives 8.000 m horizontal/profile length while its elevation dimensions pulley centres 8500 mm; prior power calculation uses 17 m horizontal length. Do not treat these as one reconciled length.
- `fact_eaf418b00e9940cda713` (KF-3): GA specifies screw take-up, 210 degree wrap and skirt 5.4 m (elevation 6.4 m); prior calculation uses vertical-gravity take-up, 180 degree wrap and 14.5 m skirt. Calculation facts remain design-case records, not confirmed installed geometry.
- `fact_04fb7c2c40214b25a789` (KF-3): Drive vendor part details, brake setting, lubricant grades and commissioned PCS/BSS/ZSS settings require their applicable vendor and field records.
- `fact_be0a13f61d394a1f9ee4` (KF-4 Drive assembly Thruster brake): GA coupling row gives brake drum diameter 250 mm while brake model row says EBTM 300/H; reconcile brake GA/drive schedule before selecting spares.
- `fact_371d9cd5b56643fca1fb` (KF-4): GA table gives 8.000 m horizontal/profile length while its elevation dimensions pulley centres 8500 mm; prior power calculation uses 17 m horizontal length. Do not treat these as one reconciled length.
- `fact_e992ee65e4dc4ad2a3bc` (KF-4): GA specifies screw take-up, 210 degree wrap and skirt 5.4 m (elevation 6.4 m); prior calculation uses vertical-gravity take-up, 180 degree wrap and 14.5 m skirt. Calculation facts remain design-case records, not confirmed installed geometry.
- `fact_43d38f02350945e5acfc` (KF-4): Drive vendor part details, brake setting, lubricant grades and commissioned PCS/BSS/ZSS settings require their applicable vendor and field records.
- `fact_535bc3eddf3e4082857f` (FG-13): Commissioned travel/thrust settings and direction-to-destination field checks are not provided by this mechanical GA.
- `fact_f29ac14a291140e09550` (FG-14): Commissioned travel/thrust settings and direction-to-destination field checks are not provided by this mechanical GA.
- `fact_59ff23eb28314ddd8de6` (UEE-2 AP-01): Schedule total is established. Individual nozzle serial numbers, field condition and commissioned pressures remain unverified.
- `fact_17f0bebc36ef4a2ab686` (UEE-2 AP-02): Schedule total is established. Individual nozzle serial numbers, field condition and commissioned pressures remain unverified.
- `fact_9d6d992f572143dbbfb1` (UEE-2 AP-03): Schedule total is established. Individual nozzle serial numbers, field condition and commissioned pressures remain unverified.
- `fact_0a54c83e96a34e0ba6ed` (UEE-2 AP-04): Schedule total is established. Individual nozzle serial numbers, field condition and commissioned pressures remain unverified.
- `fact_d27b6233a25143029c4c` (UEE-2 AP-05): Schedule total is established. Individual nozzle serial numbers, field condition and commissioned pressures remain unverified.
- `fact_a18efd43f3534b2d9095` (UEE-2 AP-06): Schedule total is established. Individual nozzle serial numbers, field condition and commissioned pressures remain unverified.
- `fact_1b17b3d20c4c4c7ea5e1` (UEE-2 AP-07): Schedule total is established. Individual nozzle serial numbers, field condition and commissioned pressures remain unverified.
- `fact_1adef51dad454a4dac8e` (UEE-2 AP-08): Schedule total is established. Individual nozzle serial numbers, field condition and commissioned pressures remain unverified.
- `fact_83a214ad061a4f109bdc` (UEE-2 AP-09): Schedule total is established. Individual nozzle serial numbers, field condition and commissioned pressures remain unverified.
- `fact_6835225262e74769b005` (UEE-2 AP-10): Schedule total is established. Individual nozzle serial numbers, field condition and commissioned pressures remain unverified.
- `fact_4855bb1893904b628b2f` (UEE-2 Local DFDS): P&ID shows LCP-02 above the EBA-16A / KF-3 branch and LCP-01 above the EBA-6 branch; philosophy pp21–23 labels AP01–04 LCP01 and AP05–08 LCP02. Preserve source-specific assignments; verify wiring before treating them as installed panel allocation.
- `fact_a409faf69e2242e49d30` (UEE-2 Service and drinking water Potable water tank): Piping layout specifies300 L; CBSH GA p2 labels250 L while its elevation p1 shows300 L. Confirm procurement/as-built capacity.
- `fact_1fcf39b701484bfea558` (UEE-2 Service and drinking water): Source UGA-2 denotes pump/compressor house. Existing model label UGA-2 Dozer Shed is a conflicting identity; no automatic merge or utility ownership under that shed is made.
- `fact_33cfb7ede40745129f12` (UEE-2 AP-02): Source lists multiple upstream load signals with the feeder signal but supplies no Boolean grouping. Do not silently decide AND/OR or substitute feeder position for running-with-load.
- `fact_4992b3de21a94bc0896a` (UEE-2 AP-03): Source calls for gate position but does not specify FWD/REV in this application paragraph; retain destination from piping/P&ID and verify position contact.
- `fact_4bd38245385c456e82b9` (UEE-2 AP-04): Source calls for gate position but does not specify FWD/REV in this application paragraph; retain destination from piping/P&ID and verify position contact.
- `fact_b63eb2c3748f46968695` (UEE-2 AP-06): Source lists multiple upstream load signals with the feeder signal but supplies no Boolean grouping. Do not silently decide AND/OR or substitute feeder position for running-with-load.
- `fact_dfbe5d03328b44d5857a` (UEE-2 AP-07): Source calls for gate position but does not specify FWD/REV in this application paragraph; retain destination from piping/P&ID and verify position contact.
- `fact_908dcf7a765a42d38985` (UEE-2 AP-08): Source calls for gate position but does not specify FWD/REV in this application paragraph; retain destination from piping/P&ID and verify position contact.
- `fact_754e9d2ee93f42378081` (EBB-1 Vent filter system): Generic accessories legend also lists RAV and ZSS, but the direct-mount silo arrangement does not show a hopper/RAV. No such local components are inferred from that legend.
- `fact_5665f925834b4d63a5c4` (EBB-2 Vent filter system): Generic accessories legend also lists RAV and ZSS, but the direct-mount silo arrangement does not show a hopper/RAV. No such local components are inferred from that legend.
- `fact_d600849895014311a81e` (EBB-1 Vent filter system): Silo section inconsistently uses BU tags for fan/DP/timer in some steps and BS tags elsewhere. Existing BS identities retained with this qualification; no extra bunker-tagged devices created.
- `fact_fe74449db8b241ba91f3` (DPS-BS-1-001): DP set value and precise timer setting are not given here; source says unhealthy within2–3 min, not a single commissioned trip delay.
- `fact_63e835adbed04bc9aa51` (EBB-2 Vent filter system): Silo section inconsistently uses BU tags for fan/DP/timer in some steps and BS tags elsewhere. Existing BS identities retained with this qualification; no extra bunker-tagged devices created.
- `fact_84a6cf52e20547cba188` (DPS-BS-2-001): DP set value and precise timer setting are not given here; source says unhealthy within2–3 min, not a single commissioned trip delay.
- `fact_9d46f4ee10e3494aa9a7` (KF-3): General belt-feeder control says LT electrical healthy, while local KF3/4 GA lists3.3 kV motor supply. Preserve source-specific wording; confirm applicable switchgear before using an electrical designation.
- `fact_614d604668a342858d31` (KF-4): General belt-feeder control says LT electrical healthy, while local KF3/4 GA lists3.3 kV motor supply. Preserve source-specific wording; confirm applicable switchgear before using an electrical designation.
- `fact_bc2aa02a45bd4b66bc6f` (KF-4): Path2 p40: FG14 FWD→17A with17A running; Path3 p45: both FWD and REV text refer to17B; Path4 p48: FWD destination17A but running requirement17B. Physical branches to both conveyors are established; FWD/REV permissive assignment is unresolved.
- `fact_cd2e5d2ef3db4f2495c5` (FG-14): Path2 p40: FG14 FWD→17A with17A running; Path3 p45: both FWD and REV text refer to17B; Path4 p48: FWD destination17A but running requirement17B. Physical branches to both conveyors are established; FWD/REV permissive assignment is unresolved.
