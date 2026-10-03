# SUL-2

Planning card at model v628. Package **P02** — Jetty, ship unloaders, EAC-1/2 and UEF-1. Primary implementation batch **B08**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p02) and [family contract](../ASSEMBLY_CONTRACTS.md#unloader) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_63f51ca2fe4d40508384`.
- Existing containment closure: 2 record(s) including root; 108 assertions on root. These are model records, not a count of physical devices.
- Aliases: SUL-2
- Existing parents: none
- Direct components: SUL-2 Shuttle Conveyor
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **unloader** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_0d848e40b9394c72810b` — 019676_03.PDF, PDF pp. 2, 5.
- `doc_cd1aae66b455491b8883` — DBR for Ship Unloader.pdf, PDF pp. 2.
- `doc_1518e219127b4b0eaa3a` — G A of Ship Unloader Type 1 & Type2 with cycle time calculation.pdf, PDF pp. 2–3, 6–9, 13, 15–16, 20, 22–23, 25, 27–28.
- `doc_36b7ccb722c941269b69` — G A of Ship Unloader Type 1 & Type2.pdf, PDF pp. 6.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| No documented material connection in this scope | — | Review the section interface plan; this is not proof that no route exists | — |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_43cf2bbfa5f147538c66` (SUL-2): Shuttle GA 019676_03.PDF (title block 47043041 Rev4, FIO 18-Mar-2021) p2 identifies SUL-1/2 as Type 1, while p5 caption reads SUL 1 & SUL 2 (TYPE-2). Preserve this internal source wording conflict; do not change the numbered machine type or clone Type 2 equipment from the p5 caption.
