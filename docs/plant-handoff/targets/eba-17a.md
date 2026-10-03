# EBA-17A

Planning card at model v628. Package **P11** — Crusher house and EBA-17. Primary implementation batch **B34**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p11) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_706b09d6e5b042c8a159`.
- Existing containment closure: 33 record(s) including root; 49 assertions on root. These are model records, not a count of physical devices.
- Aliases: EBA-17A, Belt Conveyor-17A
- Existing parents: Maitree Coal Handling Plant
- Direct components: EBA-17A Drive assembly, EBA-17A Belt and mechanical assembly, EBA-17A Belt protection devices
- Located equipment: CV-5, UEE-3 Local DFDS UBS-13 on EBA-17A

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_b8025e4ba6564a7e9510` — GA & LOAD DATA OF BELT CONVEYOR-17 A&B.pdf; available PDF pp. 1–6. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 3.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 27–28, 39–40, 45–46, 48, 55.
- `doc_b8025e4ba6564a7e9510` — GA & LOAD DATA OF BELT CONVEYOR-17 A&B.pdf, PDF pp. 4.
- `doc_e082675ac82d4ad280d2` — GA & MECH LOAD OF CRUSHER HOUSE.pdf, PDF pp. 1.

Existing explicitly applicable reference identities: EBA-17A/17B Power and Belt-Tension Calculation (Rev 03) (`ent_34211bbfb26644c09a1b`), CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), 14DR2 (`ent_75f083d21aee4bbbbfbc`), 14ND3 (`ent_9f27545b4c3944169e98`), CHP HT Conveyor Drive Control Scheme (`ent_dee15248904f4820b982`), 14ND2 (`ent_f5ea7fc0dc3044f286f8`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| FG-13 | EBA-17A | Selected downstream conveyor; direction assignments require reconciliation | `fact_00c009d0811146d5aa3d` |
| FG-14 | EBA-17A | Selected downstream conveyor; direction assignments require reconciliation | `fact_bf5ce0d9e64f4a06b22f` |
| EBA-17A | FG-15A | No condition recorded; review source | `fact_ce8aac2be5764dff9fb7` |
| EBA-17A | FG-15A | Incoming coal | `fact_664e6554e9e14299995b` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_c314a1dd1be14ce1a34a` (EBA-17A Drive assembly Thruster brake): Local GA establishes a thruster brake. Exact thruster model, fluid grade/fill and brake-release switch field tag require the applicable vendor detail; do not copy another conveyor size.
- `fact_aeea72180c034abda7dc` (EBA-17A Drive assembly Scoop coupling PST-500): EBA17 GA specifies PST-500. A detailed applicability check is still needed before attaching oil-pump, cooler, filter or actuator ratings from conveyor coupling family sheets. Crusher PST-1150 values do not apply.
