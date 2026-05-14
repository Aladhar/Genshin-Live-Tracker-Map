# Windows Tracker Guide

This is the clean Python tracker path for Windows. It uses KongYing map assets as data and does not depend on `cvAutoTrack`.

## 1. What Map Data We Imported

The safe importer copied `74` files from `KongYingMap-RC1.0.1` into `data/kongying/raw/`:

- `53` map-oriented UnityFS bundles.
- `14` icon/sprite/atlas-oriented UnityFS bundles.
- `7` metadata files, including the KongYing package manifest.

The generated manifest is `data/kongying/manifest.json`. It records original path, repo path, filename, extension, size, SHA256 hash, category guess, and import reason for each imported file.

The package manifest exposes `471` virtual asset references, mostly PNG and sprite atlas paths under `Assets/AssetRaw/UIRaw/...`.

## 2. What Unsafe Files Were Excluded

The tracker excludes KongYing runtime binaries and unrelated runtime assets from the runtime pipeline:

- `.exe`, `.dll`, `.bat`, `.cmd`, `.ps1`, `.msi`, `.scr`, `.sys`, `.pyd`, `.so`, `.dylib`
- Unity runtime blobs such as `.unity3d`, `.resource`, most `.dat`, and non-map/media bundles.
- OS junk such as `.DS_Store`.

The excluded PE files are statically inventoried in `data/kongying/binary_inventory.json`. That inventory reads metadata only; it does not execute or load them.

## 3. How The Windows Tracker Pipeline Works

The first working loop is intentionally small:

1. Load `config/tracker_windows.json`.
2. Capture the screen with `tracker_core/capture/windows_capture.py`.
3. Crop the top-left minimap with `tracker_core/minimap/crop.py`.
4. Load KongYing manifest data with `tracker_core/map_data/kongying_loader.py`.
5. Try localization with `tracker_core/localization/template_matcher.py`.
6. Print a JSON location estimate.
7. Save debug images in `debug_output/`.

Run one loop iteration:

```powershell
.\.venv\Scripts\python.exe -m tracker_core.tracker_loop --once
```

Run continuously:

```powershell
.\.venv\Scripts\python.exe -m tracker_core.tracker_loop
```

## 4. How Screen Capture Works

`windows_capture.py` tries `mss` first and falls back to Pillow `ImageGrab`.

It captures pixels from the desktop only. It does not require admin, does not hook or inject into the game, and does not read game memory.

Debug capture output:

```text
debug_output/latest_capture.png
```

## 5. How Minimap Crop Works

The crop is configured in `config/tracker_windows.json`:

```json
{
  "minimap_crop_x": 24,
  "minimap_crop_y": 32,
  "minimap_crop_width": 260,
  "minimap_crop_height": 260
}
```

The default assumes the Genshin minimap is near the top-left of a 16:9 screen. Adjust these values after checking `debug_output/latest_capture.png`.

Debug crop output:

```text
debug_output/latest_minimap.png
```

## 6. How Matching Against KongYing Map Assets Works

The current matcher uses OpenCV template matching against directly loadable processed PNG assets.

Run the extractor first:

```powershell
.\.venv\Scripts\python.exe tools\extract_kongying_textures.py --overwrite
```

This writes decoded map images into `data/kongying/processed/` and writes `data/kongying/processed_manifest.json`.

The loader automatically includes processed images. By default, the matcher excludes paths containing `outline` or `overlay` so the first pass prefers background map tiles.

The matcher now does four important things:

- Applies a circular minimap mask and ignores the center player-arrow area.
- Searches several minimap scales from `config/tracker_windows.json`.
- Parses tile coordinates from names such as `UI_MapBack_-1_0.png`.
- Rejects low-confidence or ambiguous matches instead of returning fake live coordinates.

## 7. How X/Y Position Is Estimated

For accepted matches, `x` and `y` are global tile-pixel coordinates when the tile name can be parsed:

```text
local_x = match_top_left_x + scaled_template_width / 2
local_y = match_top_left_y + scaled_template_height / 2
global_x = tile_x * tile_image_width + local_x
global_y = tile_y * tile_image_height + local_y
```

If tile coordinates cannot be parsed, the matcher still reports candidate local image pixels in the debug fields. These are not calibrated Genshin world coordinates yet. A later calibration step must map KongYing tile pixels to game/map world coordinates.

Rejected matches set `x` and `y` to `null`, but still include `candidate_x`, `candidate_y`, `top_candidates`, and `rejection_reason` for debugging.

## 8. How Rotation/Direction Is Estimated

Rotation is not estimated yet.

Planned first pass:

1. Detect the player arrow/compass marker inside the minimap crop.
2. Estimate its angle from mask or contour orientation.
3. Smooth rotation over time.
4. Pass the angle into the live marker renderer.

## 9. How The Live Marker Is Rendered

`tracker_core/rendering/live_marker.py` can draw a simple circular marker and optional heading arrow onto a debug map image.

The tracker loop does not render a full overlay yet. For now it prints location JSON and saves debug images. The renderer is ready for the next UI/overlay step once processed map images and coordinates exist.

## 10. How To Run, Debug, And Test On Windows

Create a venv and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Import KongYing assets:

```powershell
.\.venv\Scripts\python.exe tools\import_kongying_assets.py
.\.venv\Scripts\python.exe tools\inspect_kongying_binaries.py
```

Run one test pass with live capture:

```powershell
.\.venv\Scripts\python.exe tools\test_tracker_windows.py
```

Run one test pass with an existing screenshot:

```powershell
.\.venv\Scripts\python.exe tools\test_tracker_windows.py --frame RawScreen.png
```

Run the deterministic localization smoke test:

```powershell
.\.venv\Scripts\python.exe tools\smoke_test_localization.py
```

Expected smoke-test result: `passed: true`, exact local/global pixel match, and `0.0` local-pixel error.

Expected current screenshot result after extraction: capture/crop should work. If the confidence is not high enough, localization should reject the match and return `x: null`, `y: null`, plus the best candidate and debug fields.

Debug outputs:

```text
debug_output/latest_capture.png
debug_output/latest_minimap.png
debug_output/latest_match.png
debug_output/latest_match_candidates.png
debug_output/latest_match_mask.png
debug_output/latest_match_template.png
debug_output/latest_match.json
debug_output/smoke_synthetic_minimap.png
```

The first-pass confidence can still be low on real screenshots. The current matcher still needs better minimap crop calibration, rotation handling, and tile/world calibration before it is reliable enough for live play.
