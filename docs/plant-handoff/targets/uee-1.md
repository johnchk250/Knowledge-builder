# UEE-1

Planning card at model v628. Package **P03** — Primary screening, EAC-3 and UEF-3. Primary implementation batch **B09**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p03) and [family contract](../ASSEMBLY_CONTRACTS.md#area) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_92291cd617b04811bc28`.
- Existing containment closure: 5 record(s) including root; 12 assertions on root. These are model records, not a count of physical devices.
- Aliases: UEE-1
- Existing parents: Maitree Coal Handling Plant
- Direct components: KB-RG-1, KB-RG-2, KB-RG-3, KB-RG-4
- Located equipment: UEE-1 Oversize Reject Bins, KB-RG-1, KB-RPG-1, EBD-1, KB-RG-2, KB-RPG-2, EBD-2, KB-RG-3, KB-RPG-3, EBD-3, KB-RG-4, KB-RPG-4, EBD-4, DFDSS-1 PS-03

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **screening, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_9c169bf7536b4ebca236` — COAL FLOW DIAGRAM.pdf, PDF pp. 1.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 55.
- `doc_d91f96a250d048aeb54f` — GA & DETAIL OF ROD GATE.pdf, PDF pp. 1.
- `doc_3eab668d697f4e4598c8` — GA & LOAD DATA OF BELT CONVEYOR-3A-B.pdf, PDF pp. 1.
- `doc_8d973a7544ef4a488e98` — GA & MECH LOAD OF PSH.pdf, PDF pp. 3.
- `doc_294aacf286d246769e32` — OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf, PDF pp. 17.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EAC-2A | UEE-1 | No condition recorded; review source | `fact_b6abaaf2ed93451bb3f7` |
| EAC-2B | UEE-1 | No condition recorded; review source | `fact_aaaa198ecc9d4b7e825d` |
| UEE-1 | EAC-3A | No condition recorded; review source | `fact_551f69a5732d442c9559` |
| UEE-1 | EAC-3B | No condition recorded; review source | `fact_dcf7107d47574f3fb948` |
| EAC-2A | KB-RG-1 | Selected primary screening chute | `fact_39fbc17c859f4899b093` |
| KB-RG-1 | KB-RPG-1 | No condition recorded; review source | `fact_accece00a32644bebd05` |
| KB-RPG-1 | EBD-1 | No condition recorded; review source | `fact_b1e370eb89cb4a2c9e99` |
| EBD-1 | EAC-3A | Undersize -100 mm | `fact_82930e30ba0942118fd6` |
| EBD-1 | UEE-1 Oversize Reject Bins | Oversize +100 mm | `fact_a378cbf41ebe4cab8a9c` |
| EAC-2A | KB-RG-2 | Selected primary screening chute | `fact_7e0fb04799244ec3a374` |
| KB-RG-2 | KB-RPG-2 | No condition recorded; review source | `fact_c6ec01a6a60246b8a7e7` |
| KB-RPG-2 | EBD-2 | No condition recorded; review source | `fact_3ef72a2f3c9c4a1aa04c` |
| EBD-2 | EAC-3A | Undersize -100 mm | `fact_06e36e9dd1bb4a299915` |
| EBD-2 | UEE-1 Oversize Reject Bins | Oversize +100 mm | `fact_571e6719d1eb406db17b` |
| EAC-2B | KB-RG-3 | Selected primary screening chute | `fact_df9b3c3981024b568b92` |
| KB-RG-3 | KB-RPG-3 | No condition recorded; review source | `fact_848488a0e2e140d69d86` |
| KB-RPG-3 | EBD-3 | No condition recorded; review source | `fact_66c36db77b204b1d8b0a` |
| EBD-3 | EAC-3B | Undersize -100 mm | `fact_454fa066db614765bc6c` |
| EBD-3 | UEE-1 Oversize Reject Bins | Oversize +100 mm | `fact_301e0fca652b435d95ba` |
| EAC-2B | KB-RG-4 | Selected primary screening chute | `fact_3c5fdf24b3f04dfb9dec` |
| KB-RG-4 | KB-RPG-4 | No condition recorded; review source | `fact_725d775682634abb8976` |
| KB-RPG-4 | EBD-4 | No condition recorded; review source | `fact_1738d9fc77144ea9ad97` |
| EBD-4 | EAC-3B | Undersize -100 mm | `fact_da997f277f2a456ea0a7` |
| EBD-4 | UEE-1 Oversize Reject Bins | Oversize +100 mm | `fact_2607137fb64d44449ec0` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
