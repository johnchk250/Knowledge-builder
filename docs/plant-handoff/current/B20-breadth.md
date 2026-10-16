# B20 Checkpoint — Yard 3 Conveyors and Place Structure (`v671`–`v673`)

## Status
- **Batch**: `B20` (`Phase 3: Stockyards and reclaim`, section `P07`)
- **Mode**: Pass A (`breadth_first`, Tier 1 operational breadth)
- **Baseline → Accepted Versions**: `v670` → `v671` (`area`), `v672` (`eleven`), `v673` (`twelve`)
- **Proposals**: `prop_8a41c209e31b46d291a4` (`v671`), `prop_4f92d18bc70e41a583c2` (`v672`), `prop_c17e3059a24d48f1b6e9` (`v673`)
- **New Major Components**: `26` (`1` Yard 3 functional area, `12` `EAC-11` assemblies, `13` `EBA-12` assemblies including belt weigher)
- **Assertions**: `+122` added (`17` in `v671`, `50` in `v672`, `55` in `v673`), `10` retired (`9` aggregate/duplicate-owner `part_of` facts in `v671`, `1` superseded protection/weigher `document_note` in `v673`). Net active assertions: `19,041` → `19,153`.

## Scope Summary
1. **`B20/area` (`v671`, `doc_4f2cd96c3b1e413ea4b5` p55)**:
   - Created `Coal Yard 3` (`functional_area` under `Coal Stockpile Yard`, `ent_988efbb9fa7c4dfd89e2`) as a descriptive grouping without inventing a field tag.
   - Re-homed `EAC-11`, `EAD-3`, `EAE-3`, `EAF-3`, `EBA-12`, `UEB-3`, `UAX-3`, and `UAX-7` under `Coal Yard 3` and retired 9 aggregate `part_of` assertions (`Maitree Coal Handling Plant` and duplicate `Coal Stockpile Yard` on `EAE-3`).
   - Linked `Coal Yard 3` to interface transfer towers `UEF-4` (`TP-4`) and `UEF-9` (`TP-9`) via `associated_with` while preserving the existing `EAC-8B` fixed-tripper / diverter (`FD-4`) stacking inlet at `UEF-4` and `EBA-12 -> FG-8 -> EBA-15A/15B` reclaim outlet at `UEF-9`. Confirmed `UAX-3` has zero false `material_flow_to` edges.
2. **`B20/eleven` (`v672`, `doc_9d6657d14f3a4c829469` — `175021` Rev 2 approved `29-Oct-2018`)**:
   - Added 12 Tier 1 assemblies on `EAC-11` (`ent_067d1133cfb64687acfb`): `680 kW / 1488 rpm / 3.3 kV` BHEL main drive motor, `Premium PST-660` scoop fluid coupling, `B3-560` (`20.9:1`) bevel-helical gearbox, `GBM RG-12` low-speed coupling, `Elektromag EBTM-500 DS/I` service thruster brake, `1000 mm` head drive pulley, `2000 mm ST1000` belting (`1850 m` endless length), `800/630 mm` tail and snub pulley group at `UEF-4`, head-end HGTU at `UAX-3` (`3300 mm` travel, `17,000 kg` counterweight, `800 mm` pulley), idler/support group, head/tail cleaner group, and `PCS BSS and ZSS protection group` (`18` BSS pairs, `30` PCS without explicit pair-unit, `1` tail ZSS).
   - Recorded review qualifications for sheet 1 copied `UAX-1 / UEF-6` text versus the numbered key plan (`UEF-4` to `UAX-3`), head pulley table/detail face width (`2200 mm` vs `2300 mm`), and the appended `1400 mm` coasting calculation header versus `2000 mm` GA belt width.
3. **`B20/twelve` (`v673`, `doc_0adf08e6189847b88503` — `175022` Rev 2 approved `26-Nov-2018`)**:
   - Added 13 Tier 1 assemblies on `EBA-12` (`ent_e0cd946e46264ec89bdc`): `270 kW / 1488 rpm / 3.3 kV` BHEL main drive motor, `Premium PST-530` scoop fluid coupling, `B3-355` (`23.2:1` schedule print vs `23.21` existing summary) bevel-helical gearbox, `GBM RG-10` low-speed coupling, `Elektromag EBTM-500` service thruster brake, `800 mm` head drive pulley at `UEF-9`, `1400 mm N/N HD 1250/4` belting (`1820 m` endless length), `630 mm` tail/snub pulley group at `UAX-7`, tail-end HGTU at `UAX-7` (`23,000 mm` travel, `21,000 kg` counterweight, `630 mm` pulley), idler/support group, head/tail cleaner group, `PCS BSS and ZSS protection group` (`17` BSS pairs, `31` PCS without explicit pair-unit, `1` tail ZSS), and `EBA-12 load-cell belt weigher` at `UEF-9`.
   - Retired `fact_fa0c579fa474451da2eb` (`0.25%` weigher note) and replaced it with an explicit qualification noting that GA `175022` sheet 5 prints `(±)25%` at `20–120%` load (an apparent missing-decimal typo compared to `(±)2%` on peer `175020` and `0.25%` in earlier summary data).

## Verification & Gates (`G1`–`G8`)
- `31/31` route/assembly checks pass (`output/plant-enrichment/B20/route-checks.json`).
- `33/33` headless scene checks pass (`output/plant-enrichment/B20/scene-checks.json`).
- `52/52` Node test assertions pass (`tests/test_plant_explorer.cjs`, `tests/test_plant_scene.cjs`, `tests/test_plant_scene_render.cjs`).
- Pilot audits (`yard1-audit.json`, `silo-audit.json`, `crusher-audit.json`) pass with `0` canonical changes to Yard 1 (`413` records / `1959` claims).
- Pass B depth items queued in `docs/plant-handoff/current/depth-queue.json` (`DQ-B20-001`, `DQ-B20-002`).
