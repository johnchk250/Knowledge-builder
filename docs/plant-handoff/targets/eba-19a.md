# EBA-19A

Planning card at model v628. Package **P13** — EBA-19 and travelling trippers. Primary implementation batch **B38**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p13) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_8c506662c0ec4ae1b2eb`.
- Existing containment closure: 5 record(s) including root; 46 assertions on root. These are model records, not a count of physical devices.
- Aliases: EBA-19A
- Existing parents: Maitree Coal Handling Plant
- Direct components: TT-1, TT-2
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_6a078e0b46ea4b6bab33` — GA & LOAD DATA OF BELT CONVEYOR-19 A&B.pdf; available PDF pp. 1–4. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 3.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 6–7, 23–24, 27–28, 39–40, 45–46, 48, 55.
- `doc_40568f1cddaf46f08262` — DUCTING & EQUIPMENT LAYOUT FOR BUNKER HOUSE DE SYSTEM.pdf, PDF pp. 1.
- `doc_6a078e0b46ea4b6bab33` — GA & LOAD DATA OF BELT CONVEYOR-19 A&B.pdf, PDF pp. 2–3.
- `doc_a786031791b9437d9479` — OPERATION & CONTROL PHILOSOPHY OF DUST EXRACTION SYSTEM.pdf, PDF pp. 14.

Existing explicitly applicable reference identities: EBA-19A/19B Power and Belt-Tension Calculation (Rev 03) (`ent_4d244942f9ae4ca5a643`), CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), 14DR2 (`ent_75f083d21aee4bbbbfbc`), 14ND4 (`ent_7ab6ab7f6a964fc78148`), 14ND3 (`ent_9f27545b4c3944169e98`), CHP HT Conveyor Drive Control Scheme (`ent_dee15248904f4820b982`), 14ND2 (`ent_f5ea7fc0dc3044f286f8`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| UEF-13 | EBA-19A | No condition recorded; review source | `fact_c4710146938f4c409f80` |
| EBA-19A | Bunker-A of Unit-2 | Unit-2 bunker-A selected: TT-2 aligned to receiving bunker and FG-20 selected to bunker feed; not a permanently active direct discharge. | `fact_750374aa038f48d2a1ad` |
| FG-17 | EBA-19A | Gate REV | `fact_63a06c622bce4408855b` |
| FG-18 | EBA-19A | Gate REV | `fact_b20f6aa9f7d1495dbca4` |
| EBA-19A | TT-1 | Tripper positioned for selected bunker | `fact_83879c2dc5af45988112` |
| TT-1 | FG-19 | No condition recorded; review source | `fact_0afacd69b931451d8652` |
| FG-19 | Unit-1 Coal Bunker Bay | Selected bunker feed; exact bunker depends on tripper position | `fact_3ab4bd954b6741cd83e6` |
| EBA-19A | TT-2 | Tripper positioned for selected bunker | `fact_fdb395ae9ed74b1eadc3` |
| TT-2 | FG-20 | No condition recorded; review source | `fact_88453b2e448a4942a798` |
| FG-20 | Unit-2 Coal Bunker Bay | Selected bunker feed; exact bunker depends on tripper position | `fact_8d748d4cc6034e81a3ab` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
