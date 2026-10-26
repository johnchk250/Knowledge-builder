# Current plant detail inventory

Reviewed 2026-10-24 against live model v1114. Read-only SQLite integrity check passed; foreign-key check returned 0 rows. All 179 targets and 47 batches reconciled. Counts describe records, not physical quantities or engineering completion.

9 batches accepted with qualifications; 38 further batches breadth-complete; 0 remain in Pass A. Phase 1: 6/6 batches. Finer work stays in [the depth queue](depth-queue.json).

## Main conveyors

| Conveyor | Owned records | Current work disposition | Batch / phase |
|---|---:|---|---|
| EAC-1A | 78 | Tier 1 accepted; finer detail in depth queue | B05 / phase-1 |
| EAC-1B | 78 | Tier 1 accepted; finer detail in depth queue | B05 / phase-1 |
| EAC-2A | 74 | Tier 1 accepted; finer detail in depth queue | B06 / phase-2 |
| EAC-2B | 74 | Tier 1 accepted; finer detail in depth queue | B06 / phase-2 |
| EAC-3A | 49 | Tier 1 accepted; finer detail in depth queue | B10 / phase-2 |
| EAC-3B | 49 | Tier 1 accepted; finer detail in depth queue | B10 / phase-2 |
| EAC-4A | 51 | Tier 1 accepted; finer detail in depth queue | B12 / phase-2 |
| EAC-4B | 51 | Tier 1 accepted; finer detail in depth queue | B12 / phase-2 |
| EAC-5A | 52 | Tier 1 accepted; finer detail in depth queue | B13 / phase-2 |
| EAC-5B | 51 | Tier 1 accepted; finer detail in depth queue | B13 / phase-2 |
| EBA-6A | 55 | Tier 1 accepted; finer detail in depth queue | B14 / phase-2 |
| EBA-6B | 55 | Tier 1 accepted; finer detail in depth queue | B14 / phase-2 |
| EAC-7 | 60 | Tier 1 accepted; finer detail in depth queue | B16 / phase-3 |
| EBA-8 | 62 | Tier 1 accepted; finer detail in depth queue | B16 / phase-3 |
| EAC-9 | 49 | Tier 1 accepted; finer detail in depth queue | B17 / phase-3 |
| EBA-10 | 49 | Tier 1 accepted; finer detail in depth queue | B17 / phase-3 |
| EAC-11 | 49 | Tier 1 accepted; finer detail in depth queue | B20 / phase-3 |
| EBA-12 | 49 | Tier 1 accepted; finer detail in depth queue | B20 / phase-3 |
| EAC-13 | 49 | Tier 1 accepted; finer detail in depth queue | B23 / phase-3 |
| EBA-14 | 49 | Tier 1 accepted; finer detail in depth queue | B23 / phase-3 |
| EBA-15A | 60 | Tier 1 accepted; finer detail in depth queue | B28 / phase-3 |
| EBA-15B | 60 | Tier 1 accepted; finer detail in depth queue | B28 / phase-3 |
| EBA-16A | 54 | Tier 1 accepted; finer detail in depth queue | B29 / phase-3 |
| EBA-16B | 54 | Tier 1 accepted; finer detail in depth queue | B29 / phase-3 |
| EBA-17A | 48 | remaining batch: inspect existing detail before adding | B34 / accepted-reuse |
| EBA-17B | 48 | remaining batch: inspect existing detail before adding | B34 / accepted-reuse |
| EBA-18A | 123 | accepted batch: reuse and recheck qualifications | B36 / accepted-reuse |
| EBA-18B | 123 | accepted batch: reuse and recheck qualifications | B36 / accepted-reuse |
| EBA-19A | 96 | Tier 1 accepted; finer detail in depth queue | B38 / phase-4 |
| EBA-19B | 96 | Tier 1 accepted; finer detail in depth queue | B38 / phase-4 |

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

- Accepted-package targets without owned children: TP-16, TP-17, TP-18, UEF-2, CV-5, CV-6, FG-15A, FG-15B. Dispositioned in Pass 10 (v882; utility-boundary and thin-target groups in `accepted-followups.json`).
- 536 non-reference canonical records are outside the current process-area projection; some are legitimate shared services or design/identity candidates. Every row is recorded in record-review-queue.json for source-based disposition, not automatic placement.
- Current documented electrical-network assertions: 10 at v670; the old v510 statement of zero electrical edges is historical. Plant-wide SLD/feeder closure B43 depth leg closed v882; protection relay settings remain a recorded open question.
- target-status.json records every target, including reference boundaries and planned yard area identities. No missing target is silently created.
- Existing pilot source gaps, unwritten source dispositions and unresolved identities remain work even when a root has many assertions.
- B37 sampling/access, shared utilities B01–B04 and final integration B43–B46 have scope beyond named target-card roots; batch coverage is not inferred from target-card counts.
