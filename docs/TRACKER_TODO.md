# Tracker TODO

## Done

- Inspected repo root, README, existing files, and `KongYingMap-RC1.0.1`.
- Counted KongYing file types and identified map-relevant UnityFS bundles.
- Created safe import tooling:
  - `tools/import_kongying_assets.py`
  - `tools/build_kongying_manifest.py`
  - `tools/inspect_kongying_binaries.py`
- Imported `74` safe KongYing files into `data/kongying/raw/`.
- Generated `data/kongying/manifest.json`.
- Generated static PE inventory at `data/kongying/binary_inventory.json`.
- Added Python tracker package structure under `tracker_core/`.
- Added manifest loader, Windows capture, minimap crop, template matcher prototype, live marker helper, tracker loop, and Windows test runner.
- Added `config/tracker_windows.json`.
- Added root `requirements.txt`.
- Updated `.gitignore` for local asset caches, debug output, venvs, and unsafe binaries.
- Verified syntax with `.venv`.
- Ran `tools/test_tracker_windows.py --frame RawScreen.png`; capture-frame load and minimap crop succeeded, localization returned the expected processed-image blocker.
- Ran `python -m tracker_core.tracker_loop --once`; loop caught the local macOS capture failure and printed a JSON error instead of crashing.
- Added `tools/extract_kongying_textures.py`.
- Added `UnityPy` dependency for safe UnityFS parsing.
- Extracted `621` processed map PNGs from `53` imported map bundles with `0` extraction errors.
- Generated `data/kongying/processed_manifest.json`.
- Updated loader/matcher to use processed map PNGs and skip `outline`/`overlay` assets by default.
- Reran `tools/test_tracker_windows.py --frame RawScreen.png`; matcher returned a real candidate position and matched PNG asset.
- Added parsed map asset metadata with region and tile-coordinate extraction.
- Added circular minimap masking and center-marker exclusion.
- Added multi-scale matching.
- Added confidence and ambiguity rejection.
- Added richer debug outputs, including candidate contact sheets and JSON match diagnostics.
- Added `tools/smoke_test_localization.py`; deterministic smoke test passes with exact `0.0 px` local-coordinate error.

## Current Limitations

- First-pass template matching confidence is low and not yet reliable for live play.
- X/Y estimates are image-pixel coordinates, not calibrated game-world coordinates.
- Rotation/direction detection is planned but not implemented.
- The live marker renderer exists, but there is no Windows overlay/UI yet.
- The default minimap crop is an estimate and needs tuning per resolution/HUD scale.
- Full multi-scale search across all map candidates is slow; add prefiltering/caching before using this as a tight live loop.

## Next Bugs And Tasks

1. Add map candidate prefiltering and/or a cached matcher for live-loop speed.
2. Calibrate KongYing tile pixels to game-world/map-world coordinates.
3. Tune minimap crop defaults for 1920x1080, 2560x1440, and common UI scale settings.
4. Improve real screenshot matching with minimap border/icon cleanup and rotation handling.
5. Detect player heading from minimap arrow/compass pixels.
6. Render live marker on a debug map image, then build the Windows overlay/UI.
7. Add unit tests for manifest loading, crop box clipping, extractor behavior, and matcher behavior with fixture images.
8. Decide whether large raw/processed assets should stay local-only, move to Git LFS, or be generated during setup.
