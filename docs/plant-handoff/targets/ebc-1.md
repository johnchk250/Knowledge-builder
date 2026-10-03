# EBC-1

Planning card at model v628. Package **P11** — Crusher house and EBA-17. Primary implementation batch **B33**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p11) and [family contract](../ASSEMBLY_CONTRACTS.md#crusher) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_ddae1f83adae43b484cc`.
- Existing containment closure: 64 record(s) including root; 17 assertions on root. These are model records, not a count of physical devices.
- Aliases: EBC-1
- Existing parents: Maitree Coal Handling Plant, UEE-3
- Direct components: EBC-1 Housing and access, EBC-1 Rotor assembly, EBC-1 Screen cage and adjustment, EBC-1 Rotor bearings and seals, EBC-1 Hydraulic opening system, EBC-1 Drive assembly, EBC-1 Protection and monitoring, EBC-1 Isolated foundation
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **crusher** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 15–17, 39–40, 44–45, 47–48, 55.
- `doc_d4f87b906a964bd58c17` — G.A. OF VIBRATION ISOLATION SYSTEM FOR CRUSHERS.pdf, PDF pp. 1.
- `doc_e082675ac82d4ad280d2` — GA & MECH LOAD OF CRUSHER HOUSE.pdf, PDF pp. 1.
- `doc_f608e15aedbf4f368692` — GA OF CRUSHER (RING GRANULATOR).pdf, PDF pp. 1.
- `doc_624bd9eb971746e293a8` — GA OF SCOOP TYPE COUPLING FOR CRUSHER.pdf, PDF pp. 1–2, 12.

Existing explicitly applicable reference identities: CHP Crusher Drive Control Scheme (`ent_0b0491f7873644bc8c5c`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EBD-5 | EBC-1 | Oversize +20 mm | `fact_1051da9400424381a4b2` |
| EBC-1 | KF-1 | Crushed coal | `fact_a029f39e96704c91b110` |
| EBD-5 | EBC-1 | Screen oversize | `fact_70dc680f38cd43a8a902` |
| EBC-1 | KF-1 | Crushed product | `fact_6580c004ead24307a7c5` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_15e7c2e63628408c977a` (EBC-1): Two machines are one LH and one RH; reviewed machine GA alone does not map handedness to EBC-1 versus EBC-2. Shaft/bearing selection remains design data.
- `fact_728403f7b74b4c0f800f` (EBC-1 Hydraulic opening system Power pack): Hydraulic motor rating, pump duty, oil grade/volume, valve circuit and commissioned pressure are not established by the reviewed crusher GA.
- `fact_9643e61b5638479c8896` (EBC-1 Protection and monitoring Rotor bearing RTDs): GA bearing alarm/trip80/90 degC differs from crusher control p16/17 rotor-bearing scoop permission <=70 and disengagement >80 degC. Motor bearing limits are separate. Do not choose a commissioned setting from these documents.
- `fact_89ac829932224a2ba0b2` (EBC-1 Drive assembly Scoop coupling PST-1150 Scoop actuator Motor): GA detailed box and actuator datasheet give0.1/0.25kW; a separate GA notes line says0.37kW. Speed labels for8/4second engagement also differ from datasheet685/1380rpm. Final actuator selection/timing needs reconciliation.
- `fact_889dccd55168484a82d2` (EBC-1 Drive assembly Scoop coupling PST-1150): P&I TS1/TS2 alarm/trip>85/>110degC coexists with GA maximum operating oil75degC and review request to restrict maximum75degC. These are different reported limits, not verified commissioned settings. P&I nominal flow405L/min differs from GA pump415L/min.
- `fact_4e20ab618fa1435a8afb` (EBC-1 Drive assembly Scoop coupling PST-1150): Local terminal/relay drawings are retained in source sheets5–11; field cable/MCC assignment and commissioned cause/effect are not established by the GA/P&I.
- `fact_55302a55bfe94a7e9871` (EBC-1 Drive assembly Scoop coupling PST-1150 Oil circulation pump): Start/stop description says30s adjustable stop delay; trip list says300s after main motor OFF. Retain both clauses; final cause/effect and timer settings need reconciliation.
- `fact_27bdbd2c124b4097adad` (EBC-1 Drive assembly Scoop coupling PST-1150 Scoop actuator): Engage permissive requires both CBS NOT operated, while disengage clause says ANY CBS NOT operated. Likely wording error is not corrected into an executable rule; reconcile with approved logic and field verification.
