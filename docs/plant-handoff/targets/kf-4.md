# KF-4

Planning card at model v628. Package **P10** — Blending silos and extraction. Primary implementation batch **B31**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p10) and [family contract](../ASSEMBLY_CONTRACTS.md#feeder) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_2386258cf7564b4cb443`.
- Existing containment closure: 25 record(s) including root; 49 assertions on root. These are model records, not a count of physical devices.
- Aliases: KF-4, Belt Feeder KF-4
- Existing parents: Coal Blending Silo House, Maitree Coal Handling Plant, Coal Blending Silo House
- Direct components: KF-4 Drive assembly, KF-4 Belt and mechanical assemblies, KF-4 Belt protection devices
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **feeder** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 29, 40, 45, 48, 55.
- `doc_ef73ffa11a1748979909` — DESIGN BASIS & OPERATION PHILOSOPHY OF BLENDING SILO.pdf, PDF pp. 6.
- `doc_396739a89bde48f28f61` — G.A. & LOAD DATA OF BELT FEEDER-1 & 2 AT CBSH.pdf, PDF pp. 1.
- `doc_17dab58f999c4939bbc7` — GA & MECH LOAD OF CBSH.pdf, PDF pp. 5.
- `doc_ba5c790519f14234851a` — POWER & BELT TENSION CALC. FOR BELT FEEDER.pdf, PDF pp. 2–4.

Existing explicitly applicable reference identities: 16DR1 (`ent_607e95fe2742416fad57`), 16ND1 (`ent_d1ef0f785f74498e91ef`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EBE-CES-2 | KF-4 | No condition recorded; review source | `fact_740c9764dfb942719039` |
| KF-4 | FG-14 | No condition recorded; review source | `fact_0f3b0781a5d74afda8de` |
| EBE-CES-2 Rotating tubular chute Conical outlet | KF-4 | No condition recorded; review source | `fact_89a7b01601714d5a907c` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_be0a13f61d394a1f9ee4` (KF-4 Drive assembly Thruster brake): GA coupling row gives brake drum diameter 250 mm while brake model row says EBTM 300/H; reconcile brake GA/drive schedule before selecting spares.
- `fact_371d9cd5b56643fca1fb` (KF-4): GA table gives 8.000 m horizontal/profile length while its elevation dimensions pulley centres 8500 mm; prior power calculation uses 17 m horizontal length. Do not treat these as one reconciled length.
- `fact_e992ee65e4dc4ad2a3bc` (KF-4): GA specifies screw take-up, 210 degree wrap and skirt 5.4 m (elevation 6.4 m); prior calculation uses vertical-gravity take-up, 180 degree wrap and 14.5 m skirt. Calculation facts remain design-case records, not confirmed installed geometry.
- `fact_43d38f02350945e5acfc` (KF-4): Drive vendor part details, brake setting, lubricant grades and commissioned PCS/BSS/ZSS settings require their applicable vendor and field records.
- `fact_614d604668a342858d31` (KF-4): General belt-feeder control says LT electrical healthy, while local KF3/4 GA lists3.3 kV motor supply. Preserve source-specific wording; confirm applicable switchgear before using an electrical designation.
- `fact_bc2aa02a45bd4b66bc6f` (KF-4): Path2 p40: FG14 FWD→17A with17A running; Path3 p45: both FWD and REV text refer to17B; Path4 p48: FWD destination17A but running requirement17B. Physical branches to both conveyors are established; FWD/REV permissive assignment is unresolved.
