# Review scope and reproducibility

## Continuation-guide review — 1 October 2026

Read the existing generic prompt, design, execution protocol, section/family plans, backlog, pilot reports and B30–B35 checkpoints; checked the live database version read-only at v558. Added CONTINUATION_GUIDE.md and READY_TO_PASTE_PROMPT.md, redirected the older Sol starter, and aligned the main handoff and related entry documents. Corrected B30/B31 manifest status to match their existing v527 acceptance; did not mark their prerequisites complete. Clarified historical v510 inventories and runtime discovery. This was a documentation-only review, not new extraction, source revalidation or a fresh claim of whole-model integrity/browser testing. Canonical plant data and application code were not changed.

Documentation validation: 10 Markdown files, 135 local links with no missing targets, section anchors and code fences checked; B30–B35 manifest states match existing checkpoint/report files. Read-only version recheck remained v558. No application regression tests were needed for this documentation change.

## Crusher-house implementation checkpoint

On 29 September 2026, user-selected P11 / B32–B35 reached v558 through31 reviewed batches from v527. There are418 new active canonical component/assembly records and1818 active assertions, including51 source qualifications. Twenty sources supplied accepted claims;24 candidate original hashes remain unchanged. See [the implementation report](../../CRUSHER_HOUSE_PILOT_REPORT.md) and `output/crusher-pilot/verification.md` for tested scope and limitations. The original v510 inventory remains historical. No whole-corpus or as-built verification is claimed.

## Subsequent implementation checkpoint

On 20 September 2026 the user explicitly selected the coal blending silo. B30/B31 were implemented at **v527**, following an isolated rehearsal, through 17 reviewed ingestion batches. This later work changes both canonical data and the visual explorer; the design-only statements below describe the original v510 review. See [the implementation report](../../COAL_BLENDING_SILO_PILOT_REPORT.md) for source scope, 228 new components, 1,253 assertions, 13 retired interpretations, source qualifications and continuation rules. The original inventories were not overwritten.

Validation: 30 projection/scene tests passed; read-only semantic audit checks exact crossovers, two extractor identities, dual motors/common VFD, mode separation, feeder protection quantities, ten spray applications and individual evidence. Integrity verification passed 266 documents, 5,196 evidence blocks and 527 versions. Browser journey verified house → extractor → drive → motor → original source detail. No full Python regression suite was required for this UI/data change; backend code was not modified by this implementation.

Date: 20 September 2026 (Asia/Dhaka). Consistent snapshot captured19 September 2026 19:57:23 UTC, accepted model v510. No canonical or UI edits were made as part of this design review.

## Examined

- Active repository workflow, existing generic continuation prompt, equipment/Yard 1 pilot reports, visual-model documentation and application projection/scene architecture; reviewed-ingestion, intake and patch API contracts.
- Entire current canonical model and document/evidence inventory through a **read-only SQLite transaction**. Application projection used at the snapshot timestamp, not a separately invented grouping algorithm.
- All 1660 active canonical records indexed; all 1461non-reference records routed into a review queue; all 266documents and 5196 evidence blocks indexed with original hashes and page/evidence mappings.
- Current hierarchy closure and counts for major plant equipment, current documented material/mechanical/utility/control networks, explicit applicability and 85`source_gap`/`source_discrepancy` assertions.
- Source-level retrieval and targeted reading of the control write-up, TP1 GA/review reply, blending-silo/extractor philosophy, bunker sizing calculation and boundary utility layout; inventories and applicable citations for all main equipment families.
- Original visual inspection of control p55 flow diagram, enlarged legend and silo/crusher routing region; TP1 GA p1; travelling-tripper GA p1; silo-extractor GA p1. Original renders were made locally with PyMuPDF. The control layout p56 was inventoried/rendered and its existing source context reviewed, but not given a new detailed visual interpretation in this pass.

Local review render paths are under `output/plant-handoff/review/`. They are retrieval/review artifacts, not replacement source evidence or new canonical facts. Immutable originals remain in `data/plant/originals/<sha256>`.

## Source decisions from this pass

| Source | Scope of examination | Outcome |
|---|---|---|
| `doc_4f2cd96c3b1e413ea4b5` control write-up | Targeted text pp 4–8 and section/page retrieval9–54; visual p55 plus enlarged legend and silo/crusher region; p56 metadata/context | Confirmed main route inventory, UGA legend mismatch, UEF-2 boundary, exact silo crossover and distinct crusher bypasses. Other details remain source-review tasks. |
| `doc_71a0d8fc66304e93b9c1` TP1 GA | Visual p1 and extracted review text p2 | Confirmed source exists for 175033; GA and older review reply have different revision context; found tank-capacity comment. Detailed civil/hoist/mechanical values require local crops during implementation. |
| `doc_1217799da7124df5bbe5` tripper GA | Visual p1, document inventory pp 1–6 | Confirmed rich physical assembly/BOM, handed/travel-range distinctions to review; no new installed selections committed. |
| `doc_40baa8f059a0427f9567` extractor GA | Visual p1, inventory pp 1–3 | Confirmed vertical assembly, drive/lube/liner information, machine versus vessel scope and useful visual composition. |
| `doc_ef73ffa11a1748979909` extractor philosophy | Extracted pp 1–10, focused pp 4–8 and review p10 | Source leads for dual motors/common VFD, mode-specific permissives, capacity/density bases; filename scope correction matters. Main text and review replies need revision-aware comparison. |
| `doc_dd46f2c1532c4467a6e6` bunker sizing | Extracted p2, inventory pp 1–9 | Established design-case calculation leads; no blanket application to 12installed bunkers accepted. |
| `doc_411147c712284bc5a957` SW/DW boundary layout | Title/page inventory and existing cited assertions/text | UEF-2/TP16/17/18 records exist; no new proof they belong to the main coal route. |
| `doc_9c169bf7536b4ebca236` standalone coal flow | Metadata and retrieved annex text | Imported authority must be checked against original; Rihand annex context must not become Maitree equipment facts. |

## Not claimed

This was a whole-model **structural and implementation-design review with targeted source checking**, not a fresh engineering re-extraction of every page of 266 documents. Generated candidates, title matches, cited-page lists and review-package assignments are not proof of original-source applicability. No new installation/commissioning verification, physical survey, approved isolation plan or live DCS data was obtained.

No browser redesign or new application behaviour was implemented. The existing 27 projection/scene tests were rerun and passed; the previous pilot's browser checks remain historical. Every future UI/data batch must perform its own prescribed actual-browser checks. Python application tests were not rerun for this documentation/indexing-only change.

Integrity verification passed at v510: 266 originals, 5,196 evidence blocks, 510 versions, zero errors. SQLite integrity and foreign-key checks passed on the snapshot. The final handoff validator records coverage/link/source/reference checks and the unchanged-model comparison in `inventory/handoff-validation.json`.

All 10,721 active assertions have `context.kind`; all checked exact quotes and normalized source regions are structurally valid. 5,130 assertions use at least one region covering 90% or more of a page, making focused readability review important. Structural validity does not establish that a cited region proves the claim.

## Refresh tools

```powershell
.venv/Scripts/python.exe tools/snapshot_plant_handoff.py --out output/plant-handoff/snapshot.json
.venv/Scripts/python.exe tools/build_plant_handoff_inventory.py --snapshot output/plant-handoff/snapshot.json --node 'C:/Program Files/nodejs/node.exe'
.venv/Scripts/python.exe tools/validate_plant_handoff.py --snapshot output/plant-handoff/snapshot.json
```

The snapshot exporter uses SQLite `mode=ro`, `query_only=ON`, a transaction and `Store.__new__(Store).model(db=...)`; it does not run Store initialization. The index builder writes only documentation/index artifacts. The validator also reads live canonical data without initializing it.

**Refresh caution:** the builder intentionally rewrites generated target cards and inventories. Keep actual progress in separate batch checkpoints. The authored section plans, finding numbers and batch mapping represent the v510 review and need conscious reconciliation if identities or scope change. Never silently use a refreshed numerical snapshot to claim the authored plan was re-reviewed.
