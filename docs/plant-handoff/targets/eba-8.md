# EBA-8

Planning card at model v628. Package **P05** — Coal Yard 1: preserve and close pilot gaps. Primary implementation batch **B16**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p05) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_97010a833b584e8d86c4`.
- Existing containment closure: 42 record(s) including root; 56 assertions on root. These are model records, not a count of physical devices.
- Aliases: EBA-8
- Existing parents: Maitree Coal Handling Plant, Coal Yard 1
- Direct components: EBA-8 Drive assembly, EBA-8 Head pulley, EBA-8 Belt, EBA-8 Take-up assembly, EBA-8 Belt protection devices, EBA-8 Idlers, EBA-8 External scrapers, EBA-8 Internal scraper, EBA-8 Belt weigher
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_75a88e7148014a83aefd` — GA & LOAD DATA OF BELT CONVEYOR-8.pdf; available PDF pp. 1–8. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 2.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 9, 26–29, 46, 55.
- `doc_75a88e7148014a83aefd` — GA & LOAD DATA OF BELT CONVEYOR-8.pdf, PDF pp. 5.
- `doc_7aa49cc0d1c34af7ac06` — GA OF SCOOP TYPE FLUID COUPLING FOR CHP CONVEYORS.pdf, PDF pp. 1.

Existing explicitly applicable reference identities: CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), 14DR2 (`ent_75f083d21aee4bbbbfbc`), 14ND3 (`ent_9f27545b4c3944169e98`), 14ND2 (`ent_f5ea7fc0dc3044f286f8`), EBA-8/10/12/14 Power and Belt-Tension Calculation (Rev 03) (`ent_fc7b03c245e6419cb264`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| UAX-5 | EBA-8 | No condition recorded; review source | `fact_0f1bb930b8ad415a81d9` |
| EBA-8 | UEF-11 | No condition recorded; review source | `fact_28e2e07361f3458c877b` |
| EAF-1 | EBA-8 | No condition recorded; review source | `fact_2d1db428261446b78d76` |
| EBA-8 | FG-10 | No condition recorded; review source | `fact_5cd3fff5d2b24a0abf89` |
| EAF-1 | EBA-8 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_b8fe8e423a5c4cdebdc6` |
| EBA-8 | UEF-11 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_c8d46fce0758442aa99e` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_75055f2203154fda954a` (EBA-8 Belt protection devices Pull-cord switches (PCS)): PCS total needs reconciliation of both-side symbols, schedule and quantity unit. No multiplication into an installed switch count has been made.
- `fact_a95eb9ff543044cfa77c` (EBA-8): Field sensor loop IDs, brake setting and final equipment-specific control settings require confirmation. Coupling oil details are recorded separately from the vendor design, with model applicability qualifications.
- `fact_044f267008454763aacc` (EBA-8 Drive assembly Scoop coupling): Conveyor GA sheet 5 selects PST-530; vendor scoop GA sheet 1 explicitly assigns EBA-8 to 500 PST. The auxiliaries below describe that vendor selection. Final installed model and component applicability remain unresolved.
- `fact_1c378fb544124fa888c9` (EBA-8 Drive assembly Scoop coupling): Instrument drawing symbols do not establish plant loop IDs. Alarm/trip thresholds, controller wiring and actual oil fill require applicable final records.
- `fact_c0ad9baf77444b18aeeb` (EBA-8 Drive assembly Scoop coupling Scoop actuator): General CBS permissive and trip wording both say not operated, leaving trip polarity unresolved. Succeeding-conveyor/scoop conditions also require application review; no executable Boolean logic is inferred.
