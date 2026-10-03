# KF-3

Planning card at model v628. Package **P10** — Blending silos and extraction. Primary implementation batch **B31**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p10) and [family contract](../ASSEMBLY_CONTRACTS.md#feeder) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_55e7674df8d54ac78d50`.
- Existing containment closure: 25 record(s) including root; 49 assertions on root. These are model records, not a count of physical devices.
- Aliases: KF-3, Belt Feeder KF-3
- Existing parents: Coal Blending Silo House, Maitree Coal Handling Plant, Coal Blending Silo House
- Direct components: KF-3 Drive assembly, KF-3 Belt and mechanical assemblies, KF-3 Belt protection devices
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
| EBE-CES-1 | KF-3 | No condition recorded; review source | `fact_aecf9acb41ce4ce0bdd4` |
| KF-3 | FG-13 | No condition recorded; review source | `fact_2aa60b29c9444712a430` |
| EBE-CES-1 Rotating tubular chute Conical outlet | KF-3 | No condition recorded; review source | `fact_28ee5a683eb846d4bf80` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_85f68b7ab1ca4b95a6cc` (KF-3 Drive assembly Thruster brake): GA coupling row gives brake drum diameter 250 mm while brake model row says EBTM 300/H; reconcile brake GA/drive schedule before selecting spares.
- `fact_61f9058ce4954d5db5de` (KF-3): GA table gives 8.000 m horizontal/profile length while its elevation dimensions pulley centres 8500 mm; prior power calculation uses 17 m horizontal length. Do not treat these as one reconciled length.
- `fact_eaf418b00e9940cda713` (KF-3): GA specifies screw take-up, 210 degree wrap and skirt 5.4 m (elevation 6.4 m); prior calculation uses vertical-gravity take-up, 180 degree wrap and 14.5 m skirt. Calculation facts remain design-case records, not confirmed installed geometry.
- `fact_04fb7c2c40214b25a789` (KF-3): Drive vendor part details, brake setting, lubricant grades and commissioned PCS/BSS/ZSS settings require their applicable vendor and field records.
- `fact_9d46f4ee10e3494aa9a7` (KF-3): General belt-feeder control says LT electrical healthy, while local KF3/4 GA lists3.3 kV motor supply. Preserve source-specific wording; confirm applicable switchgear before using an electrical designation.
