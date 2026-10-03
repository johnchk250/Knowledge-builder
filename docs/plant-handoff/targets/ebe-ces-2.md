# EBE-CES-2

Planning card at model v628. Package **P10** — Blending silos and extraction. Primary implementation batch **B31**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p10) and [family contract](../ASSEMBLY_CONTRACTS.md#silo) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_ac511cac04344c2596f0`.
- Existing containment closure: 27 record(s) including root; 32 assertions on root. These are model records, not a count of physical devices.
- Aliases: EBE-CES-2
- Existing parents: Coal Blending Silo House
- Direct components: EBE-CES-2 Pressure cone and support arms, EBE-CES-2 Reclaim platform, EBE-CES-2 Rotating blade, EBE-CES-2 Adjusting sleeve, EBE-CES-2 Rotating tubular chute, EBE-CES-2 Slew bearing and external gear, EBE-CES-2 Labyrinth seal, EBE-CES-2 Automatic lubrication, EBE-CES-2 Drive assembly 1, EBE-CES-2 Drive assembly 2, EBE-CES-2 Common VFD, EBE-CES-2 Local control station
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **silo, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 5, 40, 45, 48, 55.
- `doc_ef73ffa11a1748979909` — DESIGN BASIS & OPERATION PHILOSOPHY OF BLENDING SILO.pdf, PDF pp. 4–8.
- `doc_17dab58f999c4939bbc7` — GA & MECH LOAD OF CBSH.pdf, PDF pp. 7.
- `doc_40baa8f059a0427f9567` — GA OF SILO EXTRACTION SYSTEM.pdf, PDF pp. 1.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EBB-2 | EBE-CES-2 | No condition recorded; review source | `fact_c4283ca9fa2d4c4c9c96` |
| EBE-CES-2 | KF-4 | No condition recorded; review source | `fact_740c9764dfb942719039` |
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

- `fact_0b75071838164aefb18c` (EBE-CES-2 Automatic lubrication): Reviewed GA and philosophy identify the lubrication destinations but do not establish pump model, lubricant grade, dosage, cycle setting or a separate hydraulic dust-seal circuit.
- `fact_f6800fdce8dc45cf97cd` (EBE-CES-2 Drive assembly 1): Gearbox ratio, coupling model, bearing part numbers and installed motor identification are not established by these reviewed pages.
- `fact_ba0e9febb0614e15be3e` (EBE-CES-2 Drive assembly 2): Gearbox ratio, coupling model, bearing part numbers and installed motor identification are not established by these reviewed pages.
- `fact_35c5e99c39644bdd98ca` (EBE-CES-2): Earlier review response broadly lists a reverse pushbutton for local operation; revised main text separates Local forward start from Maintenance forward/reverse. Keep mode-specific main-text conditions and confirm commissioned logic.
- `fact_f9f8625789e245f0a62f` (EBE-CES-2): GA lists automatic lubrication for slew bearing and drives but gives no complete hydraulic dust-seal circuit requested in philosophy review. Treat that circuit and its settings as unresolved.
- `fact_4878983c28a54eae974d` (EBE-CES-2 Common VFD): Extractor GA indicates a panel enclosure between silos near EL+17.500 m. CBSH review p7 instead states an air-conditioned MCC room near DS Pump House-2; installed panel location remains unverified.
- `fact_dff2b9a7def442da9391` (EBE-CES-2 Common VFD): CBSH review reply differs from extractor GA/philosophy showing a silo-building panel. Retain both source locations; verify latest electrical GA and field installation.
