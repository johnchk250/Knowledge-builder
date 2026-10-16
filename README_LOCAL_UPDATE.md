# CHP Knowledge v670 -> v718 Minimal Delta Package

This archive contains ONLY the new/updated files from Pass A Batches B20 through B46 (v671 -> v718),
plus `apply_b20_to_b46_to_sqlite.py` to upgrade your existing local `data/plant/plant.sqlite3` in-place
without re-downloading the 95 MB database or multi-GB `originals/` folder.

## Quick Start (30 seconds)
1. Extract this `.zip` directly into the root of your existing local `CHP knowledge` folder
   (allowing it to merge `output/`, `tools/`, and `docs/`).
2. Open a terminal / Command Prompt in your local `CHP knowledge` folder and run:
   ```
   python apply_b20_to_b46_to_sqlite.py
   ```
   - This automatically creates a safety backup (`data/plant/plant.sqlite3.v670.bak`),
     commits all 48 packages (`v671` -> `v718`) with full SHA-256 hash-chain integrity,
     and runs `chp.verify` checks.
3. Launch the app as usual:
   ```
   start.bat
   ```
   or:
   ```
   python -m chp.launcher
   ```
   Your local server at `http://127.0.0.1:8765` will immediately display `Documented model · v718`.
