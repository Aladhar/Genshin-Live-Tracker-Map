# Project Cleanup Notes

## Clean Layout

The clean tracker implementation should live in these repo-owned paths:

```text
config/
data/
docs/
tracker_core/
tools/
requirements.txt
```

Local generated data should stay ignored:

```text
.venv/
debug_output/
data/kongying/raw/
data/kongying/processed/
KongYingMap-RC1.0.1/
```

Tracked KongYing manifests are small and useful:

```text
data/kongying/manifest.json
data/kongying/binary_inventory.json
data/kongying/processed_manifest.json
```

## What Was Cleaned

Only generated/temp files should be removed automatically:

- root `debug_output/`
- `.pytest_cache/`
- `.DS_Store`

The following are intentionally kept unless you confirm deletion:

- `RawScreen.png` and `Capture.png`, because they are useful tracker test fixtures.
- `external/` source trees, because they are source references.
- `external/vcpkg/` and old build folders, because they may be local generated caches but are outside the clean Python tracker path.
- `data/kongying/raw/` and `data/kongying/processed/`, because they are needed to run the current tracker locally.

## What Is Not Yet One App

The Python tracker and map frontend are not integrated as one packaged Windows app yet.

Current pieces:

- Tracker core: functional Python modules and CLI scripts.
- Map data: imported and extracted KongYing map PNGs.
- Frontend map source: available under `external/map_front_v3`.
- App shell/overlay: not built yet.

Recommended next architecture:

```text
tracker_core/        Python capture/localization engine
data/kongying/       local map assets and manifests
map_app/             future English-first web map UI
desktop_app/         future Windows wrapper/overlay
```

Keep `external/` as reference/upstream material. Build the custom clean app in new repo-owned folders instead of modifying old cvAutoTrack runtime paths.

