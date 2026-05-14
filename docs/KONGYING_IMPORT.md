# KongYing Safe Import

This project uses `KongYingMap-RC1.0.1` as a data source only. The clean tracker does not run the KongYing app, does not load its runtime DLLs, and does not use the old `cvAutoTrack` executable/DLL path.

## Source Inspection

Source folder inspected: `KongYingMap-RC1.0.1`

Observed source size: about `459M`

Observed file count: `129`

Observed file types:

| Extension | Count | Notes |
| --- | ---: | --- |
| `.bundle` | 99 | UnityFS asset bundles; map/icon bundles are useful raw data containers. |
| `.dll` | 8 | Runtime PE binaries; excluded from tracker runtime. |
| `.exe` | 3 | Runtime PE binaries; excluded from tracker runtime. |
| `.dat` | 4 | Unity/IL2CPP metadata resources; excluded for now. |
| `.resource` | 2 | Unity runtime resources; excluded for now. |
| `.json` | 2 | Readable Unity metadata; imported. |
| `.bytes` | 1 | KongYing package manifest; imported and scanned for virtual asset paths. |
| `.config`, `.info`, `.hash`, `.version` | 1 each | Small metadata files; imported. |
| `[no_ext]`, `.DS_Store` | several | Runtime resources or OS junk; excluded. |

## Imported Data

The importer copied `74` safe files into `data/kongying/raw/` and generated `data/kongying/manifest.json`.

Imported total size: `341,593,704` bytes, about `326M`.

Imported categories:

| Category | Count |
| --- | ---: |
| `map_tile` | 53 |
| `icon` | 14 |
| `metadata` | 7 |

Imported extensions:

| Extension | Count |
| --- | ---: |
| `.bundle` | 67 |
| `.json` | 2 |
| `.bytes`, `.config`, `.hash`, `.info`, `.version` | 1 each |

The imported `.bundle` files are inert raw UnityFS asset containers selected by filename signals such as `mapimg`, `mainmap`, `overlay`, `outline`, `sprite`, `atlas`, and `poi`. They are copied as data, not executed.

The package manifest produced `471` virtual asset references, including map PNG paths such as:

```text
Assets/AssetRaw/UIRaw/MapIMG/DXKQMap/UI_MapBack_TheChasm_0_0.png
Assets/AssetRaw/UIRaw/MapIMG/MainMap/-1/UI_MapBack_-1_-1.png
Assets/AssetRaw/UIRaw/MapIMG/JRZHMap/UI_Map_LayeredMap_116000000.png
```

## Excluded Data

Excluded files are recorded in `data/kongying/manifest.json` under `excluded_files`.

Excluded reason counts:

| Reason | Count |
| --- | ---: |
| `unsafe_executable_extension` | 11 |
| `non_map_runtime_or_media_bundle` | 31 |
| `unsupported_or_runtime_binary` | 8 |
| `junk_os_metadata` | 4 |
| `unclassified_unity_bundle` | 1 |

Executable/runtime files excluded from tracker import:

```text
KongYingMap-RC1.0.1/GameAssembly.dll
KongYingMap-RC1.0.1/Map.exe
KongYingMap-RC1.0.1/Map_Data/Plugins/x86_64/lib_burst_generated.dll
KongYingMap-RC1.0.1/Map_Data/Plugins/x86_64/libsharpyuv.dll
KongYingMap-RC1.0.1/Map_Data/Plugins/x86_64/libwebp.dll
KongYingMap-RC1.0.1/Map_Data/Plugins/x86_64/libwebpdecoder.dll
KongYingMap-RC1.0.1/Map_Data/Plugins/x86_64/libwebpdemux.dll
KongYingMap-RC1.0.1/Map_Data/StreamingAssets/Plugins/x86_64/tips/tips.exe
KongYingMap-RC1.0.1/UnityCrashHandler64.exe
KongYingMap-RC1.0.1/UnityPlayer.dll
KongYingMap-RC1.0.1/baselib.dll
```

Per the latest safety direction, these binaries were statically inventoried in `data/kongying/binary_inventory.json` by reading hashes, PE headers, sections, and import-library names. They were not loaded, executed, imported into Python, or copied into the tracker runtime.

## Commands

From the repo root:

```powershell
python tools/import_kongying_assets.py
python tools/build_kongying_manifest.py
python tools/inspect_kongying_binaries.py
```

`data/kongying/raw/` and `data/kongying/processed/` are ignored local asset caches. Keep `data/kongying/manifest.json` and `data/kongying/binary_inventory.json` tracked because they document what was imported and excluded.

## Processed PNG Extraction

The actual map PNGs are inside UnityFS bundles. `tools/extract_kongying_textures.py` decodes selected imported bundles with the Python `UnityPy` parser and writes PNG files to `data/kongying/processed/`.

This extraction still does not run KongYing executables or load KongYing DLLs.

Command:

```powershell
python tools/extract_kongying_textures.py --overwrite
```

Processed extraction result:

| Output | Count / Size |
| --- | ---: |
| Source map bundles decoded | 53 |
| Processed PNG images | 621 |
| Extraction errors | 0 |
| Processed PNG folder size | about `276M` |

The extraction manifest is:

```text
data/kongying/processed_manifest.json
```

`data/kongying/processed/` is ignored as local generated asset output. Keep `data/kongying/processed_manifest.json` tracked so the extraction result is documented.

Optional icon extraction:

```powershell
python tools/extract_kongying_textures.py --include-icons --overwrite
```

The tracker currently matches against map tiles only and filters out `outline` and `overlay` assets by default to reduce false positives.
