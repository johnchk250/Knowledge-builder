# B23 Checkpoint — Yard 4 Conveyors and Place Structure (`v680`–`v682`)

## Status
- **Batch**: `B23` (`Phase 3: Stockyards and reclaim`, section `P08`)
- **Mode**: Pass A (`breadth_first`, Tier 1 operational breadth)
- **Baseline → Accepted Versions**: `v679` → `v680` (`area`), `v681` (`thirteen`), `v682` (`fourteen`)
- **Proposals**: `prop_e401b2a95c474d288a10` (`v680`), `prop_b529a67c31d8480db6ea` (`v681`), `prop_f70912bc88df4a6ab29e` (`v682`)
- **New Major Components**: `24` (`1` Yard 4 functional area, `10` new `EAC-13` assemblies reusing existing motor and gearbox, `13` `EBA-14` assemblies including belt weigher)
- **Assertions**: `+118` added (`17` in `v680`, `46` in `v681`, `55` in `v682`), `9` retired aggregate `part_of` facts in `v680`. Net active assertions: `19,258` → `19,366`.

## Scope Summary
1. **`B23/area` (`v680`, `doc_4f2cd96c3b1e413ea4b5` p55)**:
   - Created `Coal Yard 4` (`functional_area` under `Coal Stockpile Yard`, `ent_988efbb9fa7c4dfd89e2`) as a descriptive grouping.
   - Re-homed `EAC-13`, `EAD-4`, `EAE-4`, `EAF-4`, `EBA-14`, `UEB-4`, `UAX-4`, and `UAX-8` under `Coal Yard 4` and retired 9 aggregate `part_of` assertions (`Maitree Coal Handling Plant` and duplicate `Coal Stockpile Yard` on `EAE-4`).
   - Linked `Coal Yard 4` to interface transfer towers `UEF-3` (`TP-3`) and `UEF-8` (`TP-8`) via `associated_with` while preserving the existing `EAC-3B` fixed-tripper / diverter (`FD-3`) stacking inlet at `UEF-3` and `EBA-14 -> FG-7 -> EBA-15A/15B` reclaim outlet at `UEF-8`. Confirmed TP3 coal sampling system is not wrongly owned by Yard 4.
2. **`B23/thirteen` (`v681`, `doc_99b04888284c4cf0802b` — `175023` Rev 2 approved `26-Nov-2018`)**:
   - Reused existing `EAC-13 Main Drive Motor` (`ent_dca2f99658244a2a9be6`) and `EAC-13 Main Drive Gearbox` (`ent_6e223f689ee14f2c8fab`), asserting their assembly arrangement specs (`680 kW` BHEL motor, `20.9:1` bevel-helical gearbox).
   - Added 10 new Tier 1 assemblies on `EAC-13`: `Premium PST-660` scoop fluid coupling, `GBM RG-12` low-speed coupling, `Elektromag EBTM-500 DS/I` service thruster brake, `1000 mm` head drive pulley, `2000 mm ST1000` belting (`1850 m` endless length), `800/630 mm` tail and snub pulley group at `UEF-3`, head-end HGTU at `UAX-4` (`3300 mm` travel, `17,000 kg` counterweight, `800 mm` pulley), idler/support group, head/tail cleaner group, and `PCS BSS and ZSS protection group` (`18` BSS pairs, `30` PCS without explicit pair-unit, `1` tail ZSS).
   - Recorded review qualifications for sheet 1 copied `UAX-1 / UEF-6` text versus the numbered key plan (`UEF-3` to `UAX-4`), head pulley table/detail face width, and coasting calculation header.
3. **`B23/fourteen` (`v682`, `doc_06286613f92f4d31b83c` — `175024` Rev 2 approved `26-Nov-2018`)**:
   - Added 13 Tier 1 assemblies on `EBA-14`: `270 kW / 1488 rpm / 3.3 kV` BHEL main drive motor, `Premium PST-530` scoop fluid coupling, `B3-355` (`23.2:1`) bevel-helical gearbox, `GBM RG-10` low-speed coupling, `Elektromag EBTM-500` service thruster brake, `800 mm` head drive pulley at `UEF-8`, `1400 mm N/N HD 1250/4` belting (`1820 m` endless length), `630 mm` tail/snub pulley group at `UAX-8`, tail-end HGTU at `UAX-8` (`23,000 mm` travel, `21,000 kg` counterweight, `630 mm` pulley), idler/support group, head/tail cleaner group, `PCS BSS and ZSS protection group` (`17` BSS pairs, `31` PCS without explicit pair-unit, `1` tail ZSS), and `EBA-14 load-cell belt weigher` at `UEF-8` (`(±)2%` accuracy at `20–120%` load).

## Verification & Gates (`G1`–`G8`)
- `31/31` route/assembly checks pass (`output/plant-enrichment/B23/route-checks.json`).
- `33/33` headless scene checks pass (`output/plant-enrichment/B23/scene-checks.json`).
- `52/52` Node test assertions pass.
- Pilot audits pass with `0` canonical changes to Yard 1.
