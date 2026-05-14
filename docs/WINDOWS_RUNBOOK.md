# Windows Runbook

Use these commands from the repo root.

Repo path on Windows:

```powershell
cd "C:\Users\Amrit\OneDrive\Documents\GitHub\Genshin-Live-Tracker-Map"
```

## 1. Python Tracker Setup

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 2. Import And Extract KongYing Map Data

Place the KongYing source folder at:

```text
KongYingMap-RC1.0.1
```

Then run:

```powershell
.\.venv\Scripts\python.exe tools\import_kongying_assets.py
.\.venv\Scripts\python.exe tools\inspect_kongying_binaries.py
.\.venv\Scripts\python.exe tools\extract_kongying_textures.py --overwrite
```

Expected local generated folders:

```text
data\kongying\raw\
data\kongying\processed\
```

Expected tracked manifests:

```text
data\kongying\manifest.json
data\kongying\binary_inventory.json
data\kongying\processed_manifest.json
```

## 3. Smoke Test The Matcher

This verifies known map-pixel math with a synthetic crop from an extracted PNG:

```powershell
.\.venv\Scripts\python.exe tools\smoke_test_localization.py
```

Expected: `passed` is `true`, with `0.0` local-pixel error.

## 4. Test With A Screenshot

```powershell
.\.venv\Scripts\python.exe tools\test_tracker_windows.py --frame RawScreen.png
```

Current expected behavior: the script crops the minimap and returns either an accepted location or a rejected best candidate with debug details. Rejection is good when confidence is low or candidates are ambiguous.

## 5. Run The Live Tracker Loop

One capture/localization pass:

```powershell
.\.venv\Scripts\python.exe -m tracker_core.tracker_loop --once
```

Continuous loop:

```powershell
.\.venv\Scripts\python.exe -m tracker_core.tracker_loop
```

The tracker prints JSON. It does not inject into Genshin, does not read game memory, and does not need admin.

## 6. Debug Output

Debug images and match details are generated in:

```text
debug_output\
```

Key files:

```text
latest_capture.png
latest_minimap.png
latest_match.png
latest_match_candidates.png
latest_match_mask.png
latest_match_template.png
latest_match.json
```

## 7. Map Frontend

The currently available frontend source is:

```text
external\map_front_v3
```

Run it separately:

```powershell
cd external\map_front_v3
corepack enable
pnpm install
pnpm dev
```

Build it:

```powershell
cd external\map_front_v3
pnpm build
```

Important: this is still the imported KongYing-style frontend. It is not yet integrated into the Python tracker loop as one app.

## 8. Clean Generated Files

Safe cleanup:

```powershell
Remove-Item -Recurse -Force debug_output, .pytest_cache -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Force -Filter .DS_Store | Remove-Item -Force
```

Optional local-cache cleanup if you want to reclaim space and are okay regenerating assets:

```powershell
Remove-Item -Recurse -Force data\kongying\raw, data\kongying\processed -ErrorAction SilentlyContinue
```

After optional cleanup, rerun import/extraction before testing the tracker.

## 9. Legacy cvAutoTrack

Do not use the old cvAutoTrack EXE/DLL path for the clean tracker. The clean Windows tracker path is the Python path above.

