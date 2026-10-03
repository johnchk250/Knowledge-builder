# EBD-6

Planning card at model v628. Package **P11** — Crusher house and EBA-17. Primary implementation batch **B32**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p11) and [family contract](../ASSEMBLY_CONTRACTS.md#screen) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_b271faee021c4846abf4`.
- Existing containment closure: 16 record(s) including root; 22 assertions on root. These are model records, not a count of physical devices.
- Aliases: EBD-6
- Existing parents: Maitree Coal Handling Plant, UEE-3
- Direct components: EBD-6 Screen body and deck, EBD-6 Vibrating drive assembly, EBD-6 Springs and supports
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **screening, crusher** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 5, 14, 40, 45, 48, 55.
- `doc_e082675ac82d4ad280d2` — GA & MECH LOAD OF CRUSHER HOUSE.pdf, PDF pp. 1.
- `doc_4581250ffd114bacba82` — GA OF VIBRATING GRIZZLY FEEDER (INCLUDING TECH. DATA SHEET).pdf, PDF pp. 1–2, 4.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| FG-15B | EBD-6 | Gate FWD: screening/crushing selected | `fact_2b2588f496ba46aba1eb` |
| EBD-6 | EBC-2 | Oversize +20 mm | `fact_6636bddad0e347958fa1` |
| EBD-6 | KF-2 | Undersize -20 mm bypasses crusher | `fact_8672afd6b8a544d0b9ba` |
| FG-15B | EBD-6 | Screening route | `fact_1fdf5f4b2e4247029fb4` |
| EBD-6 | EBC-2 | Screen oversize | `fact_bbf422a7662845a8aaa0` |
| EBD-6 | KF-2 | Screen undersize | `fact_b58d818e433c4adab6e1` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_8598a306091b46e8be70` (EBD-6): Control narrative p5 calls the crusher-house pair EBD-1/2, but flow p55 identifies EBD-5/6; primary EBD-1–4 are different assets. No identity merge or alias is established.
- `fact_3db5980ddb284ee0947c` (EBD-6): GA design capacity1375t/h; selection/calculation headings state1370t/h. Preserve the difference pending reconciliation.
- `fact_91139e03b30146e2b133` (EBD-6 Springs and supports): Spring supports isolate mechanical vibration; no separate vibration trip instrument is established by this GA. Exciter bearing/lubricant details need applicable vendor maintenance data.
