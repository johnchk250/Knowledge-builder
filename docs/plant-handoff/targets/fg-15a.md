# FG-15A

Planning card at model v628. Package **P11** — Crusher house and EBA-17. Primary implementation batch **B32**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p11) and [family contract](../ASSEMBLY_CONTRACTS.md#transfer) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_a716de013647437b96ec`.
- Existing containment closure: 1 record(s) including root; 12 assertions on root. These are model records, not a count of physical devices.
- Aliases: FG-15A
- Existing parents: Maitree Coal Handling Plant, UEE-3
- Direct components: none recorded
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **transfer, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 40, 55.
- `doc_e082675ac82d4ad280d2` — GA & MECH LOAD OF CRUSHER HOUSE.pdf, PDF pp. 1.
- `doc_9258f527621741938b79` — GA OF FLAP GATE.pdf, PDF pp. 1.

Existing explicitly applicable reference identities: CHP Gate and Flow Divider Control Scheme (`ent_57fc8512e7f94395a9bd`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EBA-17A | FG-15A | No condition recorded; review source | `fact_ce8aac2be5764dff9fb7` |
| FG-15A | EBD-5 | Gate FWD: screening/crushing selected | `fact_1589c991a1314911beb5` |
| FG-15A | KF-1 | Gate REV: crusher-house bypass selected | `fact_82427b68ba4546faaca3` |
| EBA-17A | FG-15A | Incoming coal | `fact_664e6554e9e14299995b` |
| FG-15A | EBD-5 | Screening route | `fact_7bea5f832caa4ffbbe99` |
| FG-15A | KF-1 | Direct bypass selected | `fact_50af8df79ca14bb1aba6` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_b247e8d908454dffbe84` (FG-15A): Bypass gate added on flow Rev8 and house GA; reviewed older generic flap-gate175065 sheets do not schedule FG15A/B. Do not borrow FG15/16 actuator ratings.
