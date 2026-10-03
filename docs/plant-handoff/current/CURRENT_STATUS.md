# Current plant detail inventory

Reviewed 2026-10-03 at model v635. Fresh read-only snapshot: `output/plant-enrichment/B05/accepted-v635.json`. All 179 targets and 47 batches reconciled. Integrity/FK checks pass. Counts describe records, not physical quantities or engineering completion.

9 batches accepted with qualifications; 4 further batches breadth-complete; 34 remain in Pass A. Phase 1: 6/6 batches. Finer work stays in [the depth queue](depth-queue.json).

## Main conveyors

| Conveyor | Owned records | Current work disposition | Batch / phase |
|---|---:|---|---|
| EAC-1A | 66 | Existing pilot; targeted follow-up | B05 / phase-1 |
| EAC-1B | 66 | Existing pilot; targeted follow-up | B05 / phase-1 |
| EAC-2A | 2 | Detailed work remains; reuse current facts | B06 / phase-2 |
| EAC-2B | 2 | Detailed work remains; reuse current facts | B06 / phase-2 |
| EAC-3A | 1 | Detailed work remains; reuse current facts | B10 / phase-2 |
| EAC-3B | 1 | Detailed work remains; reuse current facts | B10 / phase-2 |
| EAC-4A | 2 | Detailed work remains; reuse current facts | B12 / phase-2 |
| EAC-4B | 2 | Detailed work remains; reuse current facts | B12 / phase-2 |
| EAC-5A | 2 | Detailed work remains; reuse current facts | B13 / phase-2 |
| EAC-5B | 2 | Detailed work remains; reuse current facts | B13 / phase-2 |
| EBA-6A | 1 | Detailed work remains; reuse current facts | B14 / phase-2 |
| EBA-6B | 1 | Detailed work remains; reuse current facts | B14 / phase-2 |
| EAC-7 | 41 | Existing pilot; targeted follow-up | B16 / phase-3 |
| EBA-8 | 42 | Existing pilot; targeted follow-up | B16 / phase-3 |
| EAC-9 | 1 | Detailed work remains; reuse current facts | B17 / phase-3 |
| EBA-10 | 1 | Detailed work remains; reuse current facts | B17 / phase-3 |
| EAC-11 | 1 | Detailed work remains; reuse current facts | B20 / phase-3 |
| EBA-12 | 1 | Detailed work remains; reuse current facts | B20 / phase-3 |
| EAC-13 | 3 | Detailed work remains; reuse current facts | B23 / phase-3 |
| EBA-14 | 1 | Detailed work remains; reuse current facts | B23 / phase-3 |
| EBA-15A | 1 | Detailed work remains; reuse current facts | B28 / phase-3 |
| EBA-15B | 1 | Detailed work remains; reuse current facts | B28 / phase-3 |
| EBA-16A | 1 | Detailed work remains; reuse current facts | B29 / phase-3 |
| EBA-16B | 1 | Detailed work remains; reuse current facts | B29 / phase-3 |
| EBA-17A | 33 | Accepted with qualifications; reuse | B34 / accepted-reuse |
| EBA-17B | 33 | Accepted with qualifications; reuse | B34 / accepted-reuse |
| EBA-18A | 126 | Accepted with qualifications; reuse | B36 / accepted-reuse |
| EBA-18B | 126 | Accepted with qualifications; reuse | B36 / accepted-reuse |
| EBA-19A | 5 | Detailed work remains; reuse current facts | B38 / phase-4 |
| EBA-19B | 5 | Detailed work remains; reuse current facts | B38 / phase-4 |

## Transfer points

| Place | Owned records | Located records | Disposition | Batch / phase |
|---|---:|---:|---|---|
| UEF-1 | 66 | 17 | Existing pilot; GA/place correction and extension | B05 / phase-1 |
| UEF-3 | 19 | 5 | Detailed local assemblies remain | B10 / phase-2 |
| UEF-4 | 1 | 3 | Detailed local assemblies remain | B12 / phase-2 |
| UEF-5 | 1 | 5 | Detailed local assemblies remain | B13 / phase-2 |
| UEF-6 | 1 | 3 | Detailed local assemblies remain | B13 / phase-2 |
| UEF-7 | 1 | 3 | Detailed local assemblies remain | B14 / phase-2 |
| UEF-10 | 1 | 2 | Detailed local assemblies remain | B27 / phase-3 |
| UEF-11 | 1 | 2 | Detailed local assemblies remain | B27 / phase-3 |
| UEF-12 | 1 | 3 | Detailed local assemblies remain | B28 / phase-3 |
| UEF-8 | 1 | 2 | Detailed local assemblies remain | B26 / phase-3 |
| UEF-9 | 1 | 2 | Detailed local assemblies remain | B26 / phase-3 |
| UEF-13 | 142 | 21 | B36 accepted; B37 sampling/access remains | B36 / accepted-reuse |

## Review limits and additional queues

- Accepted-package targets without owned children: TP-16, TP-17, TP-18, UEF-2, CV-5, CV-6, FG-15A, FG-15B. See accepted-followups.json; B45 must review available detail and scope before closure.
- 661 non-reference canonical records are outside the current process-area projection; some are legitimate shared services or design/identity candidates. Every row is recorded in record-review-queue.json for source-based disposition, not automatic placement.
- Current documented electrical-network assertions: 10; the old v510 statement of zero electrical edges is historical. Plant-wide SLD/feeder closure remains B43.
- target-status.json records every target, including reference boundaries and planned yard area identities. No missing target is silently created.
- Existing pilot source gaps, unwritten source dispositions and unresolved identities remain work even when a root has many assertions.
- B37 sampling/access, shared utilities B01–B04 and final integration B43–B46 have scope beyond named target-card roots; batch coverage is not inferred from target-card counts.
