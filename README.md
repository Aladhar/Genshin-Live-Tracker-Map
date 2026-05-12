# Genshin Live Tracker & Map

## Screenshot-only reward detector

The prototype Primogem/reward detector lives in `tools/reward_detector`.
It captures/analyzes screenshots only, checks the center/right reward popup
region with scalable templates, combines detections with the current map
position, and writes a local nearest-pin suggestion.

Run the offline smoke tests:

```bash
python3 -m tools.reward_detector.scripts.generate_synthetic_assets
python3 -m pytest tools/reward_detector/smoke_tests -q
```

## Kongying live map sync

The official public Kongying map/layer snapshot and update report live in
`tools/kongying_sync`.

```bash
python3 -m tools.kongying_sync.sync_live_map
python3 -m pytest tools/kongying_sync/smoke_tests -q
```

The sync uses Kongying official docs, release notes, hot-update logs, and
`https://assets.yuanshen.site/webapp.json` as source of truth. GitHub is kept
as source/dev reference only. Full chest/oculus/item/pin parity still needs an
official authenticated export or local client cache because the live marker and
item APIs return authorization errors without a bearer token.

## Windows exe build

The native Windows project is `external/cvAutoTrack`. It builds a DLL named
`cvAutoTrack.dll` plus a runnable test/client executable named
`test_impl_cpp.exe`.

From PowerShell:

```powershell
.\build-windows-exe.ps1 -InstallVcpkg -RunSmokeTest
```

After the build finishes, run:

```powershell
.\external\cvAutoTrack\build-windows\bin\Release\test_impl_cpp.exe
```

The first build installs vcpkg into `external\vcpkg` and may take a while
because OpenCV and the other C++ dependencies are installed through vcpkg.
