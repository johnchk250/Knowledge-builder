# UEF-13

Planning card at model v628. Package **P12** — EBA-18, UEF-13 and sampling. Primary implementation batch **B36**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p12) and [family contract](../ASSEMBLY_CONTRACTS.md#transfer) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_1d5055a3fcb74ba6a593`.
- Existing containment closure: 142 record(s) including root; 17 assertions on root. These are model records, not a count of physical devices.
- Aliases: UEF-13
- Existing parents: Maitree Coal Handling Plant
- Direct components: UEF-13 Coal Sampling System, UEF-13 Local DFDS, UEF-13 Service and drinking water, UEF-13 Sump Pumps SP-2A/2B
- Located equipment: FG-17, FG-18, SNC-2, DFDSS-2 PS-03, EBA-18A Drive assembly, EBA-18B Drive assembly, EBA-18A Discharge chute interface, EBA-18B Discharge chute interface, UEF-13 FAS-11, UEF-13 PRU-11, UEF-13 FAS-12, UEF-13 PRU-12, UEF-13 FAS-13, UEF-13 PRU-13, UEF-13 FAS-14, UEF-13 PRU-14, UEF-13 FAS-15, UEF-13 PRU-15, UEF-13 FAS-16, UEF-13 PRU-16, UEF-13 Sump Pumps SP-2A/2B

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_a9043e95d82c40f399ec` — GA & MECH LOAD OF TP-13.pdf; available PDF pp. 1–5. Retrieval candidate, not reviewed applicability.
- `doc_800245b27bbd4afb900b` — Piping Layout for DFDS, SW & PW System at UEF-13.pdf; available PDF pp. 1–2. Retrieval candidate, not reviewed applicability.

Common source groups: **transfer, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_5a3fa71dadb642b7910a` — CALCULATIONS FOR COAL SAMPLING SYSTEM.pdf, PDF pp. 3.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 19, 21–23, 26, 53, 55.
- `doc_40568f1cddaf46f08262` — DUCTING & EQUIPMENT LAYOUT FOR BUNKER HOUSE DE SYSTEM.pdf, PDF pp. 1.
- `doc_31b03f5030bc4db69d8d` — GA & Data Sheet of Sump Pump.pdf, PDF pp. 9–10, 13–14.
- `doc_6a078e0b46ea4b6bab33` — GA & LOAD DATA OF BELT CONVEYOR-19 A&B.pdf, PDF pp. 3.
- `doc_a9043e95d82c40f399ec` — GA & MECH LOAD OF TP-13.pdf, PDF pp. 2, 4–5.
- `doc_5537009e2cff4fad875e` — GA - DATA SHEET OF NOZZLES FOR DFDS SYSTEM.pdf, PDF pp. 2.
- `doc_98b9805fdd334190a93f` — GA OF COAL SAMPLING UNIT AT UEF-13.pdf, PDF pp. 9–10.
- `doc_3cfdfb0f23c6429eb268` — GA OF FAS PRU FOR DFDS SYSTEM.pdf, PDF pp. 2–3.
- `doc_9b7d3360a5e84ec2abc3` — GA OF SPRAY HEADER FOR DFDS SYSTEM.pdf, PDF pp. 1–2.
- `doc_294aacf286d246769e32` — OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf, PDF pp. 23–25, 31.
- `doc_bca09d68af9b43e3b633` — P & ID FOR DFDS SYSTEM.pdf, PDF pp. 2.
- `doc_0453a0a014424f1cae06` — P & ID FOR SUMP PUMP & STOCK YARD RUNOFF WATER PUMP SYSTEM.pdf, PDF pp. 1–2.
- `doc_800245b27bbd4afb900b` — Piping Layout for DFDS, SW & PW System at UEF-13.pdf, PDF pp. 1.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EBA-18A | UEF-13 | No condition recorded; review source | `fact_cc8a0c7da213447fb2fb` |
| EBA-18B | UEF-13 | No condition recorded; review source | `fact_964eebfb575f4f148d22` |
| UEF-13 | EBA-19A | No condition recorded; review source | `fact_c4710146938f4c409f80` |
| UEF-13 | EBA-19B | No condition recorded; review source | `fact_d827190d9e5041c7ac37` |
| EBA-18A | FG-17 | No condition recorded; review source | `fact_466816948a474919820d` |
| FG-17 | EBA-19A | Gate REV | `fact_63a06c622bce4408855b` |
| FG-17 | EBA-19B | Gate FWD | `fact_dcc7c9484f844d608435` |
| EBA-18B | FG-18 | No condition recorded; review source | `fact_6dd146cdca1c4be890f4` |
| FG-18 | EBA-19A | Gate REV | `fact_b20f6aa9f7d1495dbca4` |
| FG-18 | EBA-19B | Gate FWD | `fact_dda62f8a537d4c88990f` |
| EBA-18A | EAU-2 Primary Sampler-1 | Sample cut only | `fact_258bc6ba977c4fe8ab9d` |
| EAU-2 Primary Sampler-1 | EAU-2 Reversible Belt Feeder | No condition recorded; review source | `fact_be3b0d88b5284238ab38` |
| EBA-18B | EAU-2 Primary Sampler-2 | Sample cut only | `fact_c4e2ed0d7e0f4d17bf08` |
| EAU-2 Primary Sampler-2 | EAU-2 Reversible Belt Feeder | No condition recorded; review source | `fact_a32b04995813474396f8` |
| EAU-2 Reversible Belt Feeder | EAU-2 Hammer Crusher | Normal sampling; collected sample or reject branch as appropriate | `fact_7ba783f789f3422b9d73` |
| EAU-2 Hammer Crusher | EAU-2 Secondary Sampler | Normal sampling; collected sample or reject branch as appropriate | `fact_63f50b2f391b4146b858` |
| EAU-2 Secondary Sampler | EAU-2 Rotary Sample Collector | Normal sampling; collected sample or reject branch as appropriate | `fact_efaedddcaaa94875b317` |
| EAU-2 Secondary Sampler | EAU-2 Reject Screw Conveyor | Normal sampling; collected sample or reject branch as appropriate | `fact_6e7825d6f15341cdbd4d` |
| EAU-2 Reject Screw Conveyor | EAU-2 Reject Slide Gate | Normal sampling; collected sample or reject branch as appropriate | `fact_c1d4d22de16d4ec19952` |
| EAU-2 Reversible Belt Feeder | EAU-2 Bias Sample Bin | Bias mode: feeder reverse | `fact_000fe01020f341cba27c` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_f4c0b6c210bb4d6282be` (UEF-13): Existing sampling/elevator identities and sampling material branches are preserved. B37 must resolve SNC-2/elevator identity, sample return and access expansion separately.
- `fact_41c6bda9c8ea494c8822` (UEF-13 Local DFDS): P&ID/operation philosophy maps12/13 to18A and15/16 to18B; piping view4-4 labels FAS12 to18B and FAS15 to18A. Piping view3-3 labels PRU13 destination19A although P&ID AP13 serves19B. These design associations are qualified, not installed routing confirmation.
- `fact_4d4b4f2c542946b5af3d` (UEF-13 Service and drinking water): Shared potable-pump PWP-1/PWP-2 name disagreement is outside this local boundary. Source does not establish commissioned isolation/tag/feeder mapping.
- `fact_2295466ba5d94a0c976b` (UEF-13 Local DFDS): Piping drawing view4-4 prints upstream conveyor18 labels on FAS12/15 while plan and P&ID place them on receiving19A. View3-3 PRU13 has19A text at a19B level. Keep the exact drawing for reconciliation.
- `fact_304474b422d3411dbf42` (UEF-13 Sump Pumps SP-2A/2B Sump pit): P&ID UEF13 annotation still shows5 m3 and2.0 x1.5 x1.7 m; review p2 requests5 m3 ->10 m3 per DBR24-Aug-2019 and vendor replies Revised. The depicted pit and revision response disagree; final civil/as-built pit drawing needed.
- `fact_9e2ec12a883e456bbae0` (UEF-13 Sump Pumps SP-2A/2B SP-2A): Installed seal clearances, oil grade/fill, maintenance interval, local isolation and field loop tags need matching O&M/installation records.
- `fact_40abd848682c47ae97f4` (UEF-13 Sump Pumps SP-2A/2B SP-2B): Installed seal clearances, oil grade/fill, maintenance interval, local isolation and field loop tags need matching O&M/installation records.
- `fact_c75c2692a4f648f586ec` (UEF-13 FAS-11): Commissioned selector/interlock wiring and final receiving branch are unresolved; do not execute this descriptive Boolean as field logic.
- `fact_cca4f08e41bd4f3182a2` (UEF-13 FAS-12): Commissioned selector/interlock wiring and final receiving branch are unresolved; do not execute this descriptive Boolean as field logic.
- `fact_e4689c0771cf4946afa6` (UEF-13 FAS-13): Commissioned selector/interlock wiring and final receiving branch are unresolved; do not execute this descriptive Boolean as field logic.
- `fact_9f6bb66da9ae4930bb9a` (UEF-13 FAS-14): Commissioned selector/interlock wiring and final receiving branch are unresolved; do not execute this descriptive Boolean as field logic.
- `fact_75aba49d78484db5a110` (UEF-13 FAS-15): Commissioned selector/interlock wiring and final receiving branch are unresolved; do not execute this descriptive Boolean as field logic.
- `fact_d4adf4a54d604617a1f4` (UEF-13 FAS-16): Commissioned selector/interlock wiring and final receiving branch are unresolved; do not execute this descriptive Boolean as field logic.
