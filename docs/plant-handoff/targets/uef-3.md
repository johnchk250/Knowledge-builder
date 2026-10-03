# UEF-3

Planning card at model v628. Package **P03** — Primary screening, EAC-3 and UEF-3. Primary implementation batch **B10**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p03) and [family contract](../ASSEMBLY_CONTRACTS.md#transfer) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_d8d8763a4bc2400882b9`.
- Existing containment closure: 19 record(s) including root; 9 assertions on root. These are model records, not a count of physical devices.
- Aliases: UEF-3
- Existing parents: Maitree Coal Handling Plant
- Direct components: UEF-3 Coal Sampling System, UEF-3 FAS-13, UEF-3 FAS-14, UEF-3 FAS-15, UEF-3 FAS-16, UEF-3 FAS-17, UEF-3 FAS-18, UEF-3 FAS-19, UEF-3 FAS-20
- Located equipment: KB-FD-1, FG-1, KB-FD-2, FG-2, DFDSS-1 PS-04

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_883418b36ea44369adbe` — GA & MECH LOAD OF TP-3.pdf; available PDF pp. 1–5. Retrieval candidate, not reviewed applicability.

Common source groups: **transfer, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_5a3fa71dadb642b7910a` — CALCULATIONS FOR COAL SAMPLING SYSTEM.pdf, PDF pp. 2.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 19–21, 55.
- `doc_a02d56b879734b5db189` — GA & LOAD DATA OF BELT CONVEYOR-4 A-B.pdf, PDF pp. 4.
- `doc_883418b36ea44369adbe` — GA & MECH LOAD OF TP-3.pdf, PDF pp. 5.
- `doc_404c8747ba8047ab8f12` — GA OF COAL SAMPLING UNIT AT UEF-3.pdf, PDF pp. 9–11.
- `doc_294aacf286d246769e32` — OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf, PDF pp. 8–10, 17.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EAC-3A | UEF-3 | No condition recorded; review source | `fact_03e4c581e4514612ac36` |
| EAC-3B | UEF-3 | No condition recorded; review source | `fact_7773785c306f4f6e8dfd` |
| UEF-3 | EAC-4A | No condition recorded; review source | `fact_d9c0e0a4f45d42e1a935` |
| UEF-3 | EAC-4B | No condition recorded; review source | `fact_509e4a4c84024e249105` |
| EAC-3A | KB-FD-1 | No condition recorded; review source | `fact_180c5a998959481f8577` |
| KB-FD-1 | EAC-13 | Full or partial stacking | `fact_1445e6bd7c6c4115859c` |
| KB-FD-1 | FG-1 | Full or partial onward flow | `fact_c97d7797fcc1445280b7` |
| FG-1 | EAC-4A | Gate aligned to selected downstream conveyor | `fact_f536214811e441a5bb5c` |
| FG-1 | EAC-4B | Gate aligned to selected downstream conveyor | `fact_e2c46e0222254d87bae7` |
| EAC-3B | KB-FD-2 | No condition recorded; review source | `fact_e663aade8b3a471cad8c` |
| KB-FD-2 | EAC-13 | Full or partial stacking | `fact_68a14314e9fc4f71a3e8` |
| KB-FD-2 | FG-2 | Full or partial onward flow | `fact_9be7b127efd74bb2bd67` |
| FG-2 | EAC-4A | Gate aligned to selected downstream conveyor | `fact_fe9e31c6d462459ea839` |
| FG-2 | EAC-4B | Gate aligned to selected downstream conveyor | `fact_5becb6f600ef4c47a17b` |
| EAC-3A | EAU-1 Primary Sampler-1 | Sample cut only | `fact_d2f1acd1650845e4a53e` |
| EAU-1 Primary Sampler-1 | EAU-1 Reversible Belt Feeder | No condition recorded; review source | `fact_ca7e1a74776a49808ea7` |
| EAC-3B | EAU-1 Primary Sampler-2 | Sample cut only | `fact_43ba48115b804959b246` |
| EAU-1 Primary Sampler-2 | EAU-1 Reversible Belt Feeder | No condition recorded; review source | `fact_c1ab4e630b6c42c6bf47` |
| EAU-1 Reversible Belt Feeder | EAU-1 Hammer Crusher | Normal sampling; collected sample or reject branch as appropriate | `fact_aa6e94de636c4e799741` |
| EAU-1 Hammer Crusher | EAU-1 Secondary Sampler | Normal sampling; collected sample or reject branch as appropriate | `fact_b2ea5b6f45104d5db275` |
| EAU-1 Secondary Sampler | EAU-1 Rotary Sample Collector | Normal sampling; collected sample or reject branch as appropriate | `fact_9e488f4a853946ddbc91` |
| EAU-1 Secondary Sampler | EAU-1 Reject Screw Conveyor | Normal sampling; collected sample or reject branch as appropriate | `fact_b0d681809c65453fbaa1` |
| EAU-1 Reject Screw Conveyor | EAU-1 Reject Slide Gate | Normal sampling; collected sample or reject branch as appropriate | `fact_4753cd030eff43e69924` |
| EAU-1 Reversible Belt Feeder | EAU-1 Bias Sample Bin | Bias mode: feeder reverse | `fact_de52bdc44f024c65a871` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
