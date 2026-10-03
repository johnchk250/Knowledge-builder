# EBD-5

Planning card at model v628. Package **P11** — Crusher house and EBA-17. Primary implementation batch **B32**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p11) and [family contract](../ASSEMBLY_CONTRACTS.md#screen) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_1ff8c26276f2442380f1`.
- Existing containment closure: 16 record(s) including root; 22 assertions on root. These are model records, not a count of physical devices.
- Aliases: EBD-5
- Existing parents: Maitree Coal Handling Plant, UEE-3
- Direct components: EBD-5 Screen body and deck, EBD-5 Vibrating drive assembly, EBD-5 Springs and supports
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
| FG-15A | EBD-5 | Gate FWD: screening/crushing selected | `fact_1589c991a1314911beb5` |
| EBD-5 | EBC-1 | Oversize +20 mm | `fact_1051da9400424381a4b2` |
| EBD-5 | KF-1 | Undersize -20 mm bypasses crusher | `fact_07bd560f56b540d6ac57` |
| FG-15A | EBD-5 | Screening route | `fact_7bea5f832caa4ffbbe99` |
| EBD-5 | EBC-1 | Screen oversize | `fact_70dc680f38cd43a8a902` |
| EBD-5 | KF-1 | Screen undersize | `fact_185f2921d4be4133b00d` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_f2fac0660cd74d0d88b9` (EBD-5): Control narrative p5 calls the crusher-house pair EBD-1/2, but flow p55 identifies EBD-5/6; primary EBD-1–4 are different assets. No identity merge or alias is established.
- `fact_f4d3486119264cc7ba16` (EBD-5): GA design capacity1375t/h; selection/calculation headings state1370t/h. Preserve the difference pending reconciliation.
- `fact_02f3d1f600c8413086f0` (EBD-5 Springs and supports): Spring supports isolate mechanical vibration; no separate vibration trip instrument is established by this GA. Exciter bearing/lubricant details need applicable vendor maintenance data.
