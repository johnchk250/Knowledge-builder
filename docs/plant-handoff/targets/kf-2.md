# KF-2

Planning card at model v628. Package **P11** — Crusher house and EBA-17. Primary implementation batch **B34**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p11) and [family contract](../ASSEMBLY_CONTRACTS.md#feeder) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_cb2f76d5de0d48e8857e`.
- Existing containment closure: 26 record(s) including root; 47 assertions on root. These are model records, not a count of physical devices.
- Aliases: KF-2, Belt Feeder KF-2
- Existing parents: UEE-3, Maitree Coal Handling Plant, UEE-3
- Direct components: KF-2 Drive assembly, KF-2 Belt and mechanical assembly, KF-2 Belt protection devices
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **feeder** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 17, 29, 39, 44, 47, 55.
- `doc_3aed51331d5243ab85ab` — GA & LOAD DATA OF BELT FEEDER 1 & 2 AT CRH.pdf, PDF pp. 1.
- `doc_e082675ac82d4ad280d2` — GA & MECH LOAD OF CRUSHER HOUSE.pdf, PDF pp. 1.
- `doc_a786031791b9437d9479` — OPERATION & CONTROL PHILOSOPHY OF DUST EXRACTION SYSTEM.pdf, PDF pp. 5, 7, 11.
- `doc_ba5c790519f14234851a` — POWER & BELT TENSION CALC. FOR BELT FEEDER.pdf, PDF pp. 2–4.

Existing explicitly applicable reference identities: 16DR1 (`ent_607e95fe2742416fad57`), 16ND1 (`ent_d1ef0f785f74498e91ef`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| FG-15B | KF-2 | Gate REV: crusher-house bypass selected | `fact_55446b60756a45c98a38` |
| EBD-6 | KF-2 | Undersize -20 mm bypasses crusher | `fact_8672afd6b8a544d0b9ba` |
| EBC-2 | KF-2 | Crushed coal | `fact_aa4644756f8e4c7f92af` |
| KF-2 | FG-16 | No condition recorded; review source | `fact_4ac417b174eb4dbfa8bb` |
| FG-15B | KF-2 | Direct bypass selected | `fact_5bc3716e836d4244a5c5` |
| EBD-6 | KF-2 | Screen undersize | `fact_b58d818e433c4adab6e1` |
| EBC-2 | KF-2 | Crushed product | `fact_c583169502984e2e975b` |
| KF-2 | FG-16 | Feeder discharge | `fact_15916508c03747f7a549` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_597b19fe822c4a678d26` (KF-2 Drive assembly Thruster brake): Local GA establishes a thruster brake. Exact thruster model, fluid grade/fill and brake-release switch field tag require the applicable vendor detail; do not copy another conveyor size.
- `fact_609adc00faae4ac68908` (KF-2): General feeder section calls drive LT; KF1/2 GA specifies3.3kV motor. Retain source-specific wording and verify switchgear designation.
