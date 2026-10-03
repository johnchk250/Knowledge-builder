# EAF-1

Planning card at model v628. Package **P05** — Coal Yard 1: preserve and close pilot gaps. Primary implementation batch **B15**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p05) and [family contract](../ASSEMBLY_CONTRACTS.md#reclaimer) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_45234a96c4714e14a638`.
- Existing containment closure: 57 record(s) including root; 17 assertions on root. These are model records, not a count of physical devices.
- Aliases: EAF-1
- Existing parents: Maitree Coal Handling Plant, Coal Yard 1
- Direct components: EAF-1 Main scraper boom, EAF-1 Auxiliary scraper boom, EAF-1 Hoist system, EAF-1 Travel system, EAF-1 Power cable reel, EAF-1 Control cable reel, EAF-1 Central grease lubrication, EAF-1 Chain oil lubrication, EAF-1 Onboard plain-water DSS
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **reclaimer** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_498f70490d294542b8b0` — Basis of Design for Portal Reclaimer.pdf, PDF pp. 5–6.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 7, 55.
- `doc_a6a2fa82944f4d12b8aa` — DBR for Machine mounted DS system for Portal Type Scraper Reclaimer Machine.pdf, PDF pp. 3–5.
- `doc_3e81ea1c32df4215968d` — GA & TDS of Portal Type Scraper Reclaimer Machine.pdf, PDF pp. 3.
- `doc_42554b5718fc423997b3` — GA , TDS & P&ID of Motorized Central lubrication system for Portal Type Scraper Reclaimer Machine.pdf, PDF pp. 4, 10.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EAE-1 | EAF-1 | Selected pile reclaiming | `fact_4878544d9bc54b96a73f` |
| EAF-1 | EBA-8 | No condition recorded; review source | `fact_2d1db428261446b78d76` |
| EAE-1 | EAF-1 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_5ee5189b6c77464e8d3e` |
| EAF-1 | EBA-8 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_b8fe8e423a5c4cdebdc6` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_0334e15d95fc49748d4f` (EAF-1): Safety-instrument GA 179103 is referenced here; exact travel/collision/hoist interlock loops and wind trip settings still need verification. Do not infer the installed settings from structural design limits.
- `fact_e666ba65ec8149399451` (EAF-1): GA wind rows print 16 km/h operating and 73 km/h non-operating. Reclaimer BOD page 6 prints 16, 35 and 73 m/s. Units conflict; no authoritative trip or safe operating threshold is inferred.
- `fact_f7c5d1aafb184613b175` (EAF-1 Travel system): BOD travel row shows 2 m/min and a separate 5 m/min entry without a clear range; GA page 3 states operating 2 to 8 m/min. Retained as competing design information.
- `fact_f89c6ce6e6ed44f3b33e` (EAF-1 Auxiliary scraper boom): BOD gives 500-650 t/h depending on boom inclination; GA page 3 gives 500-660 t/h. Final applicable rating remains to be reconciled.
- `fact_ebbdf3e8f47746caa601` (EAF-1 Onboard plain-water DSS): Machine GA lists approximate DSS power 2.2 kW; this later BOD lists tentative 0.55 kW pump motor. A final vendor/nameplate check is required before assigning installed motor power.
- `fact_a8aa20262c3f4e559dee` (EAF-1 Central grease lubrication): Machine GA shows 0.37 kW lubrication motors; later Lincoln grease pump datasheet gives 0.55 kW. Source-specific values are retained pending final configuration confirmation.
