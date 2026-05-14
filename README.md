# Genshin Live Tracker & Map

## Clean Windows tracker rebuild

The current implementation path is a clean Python tracker that uses
`KongYingMap-RC1.0.1` as a data source only. Start here:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tools\import_kongying_assets.py
.\.venv\Scripts\python.exe tools\extract_kongying_textures.py --overwrite
.\.venv\Scripts\python.exe tools\smoke_test_localization.py
.\.venv\Scripts\python.exe tools\test_tracker_windows.py
```

Docs:

- `docs/TRACKER_GUIDE_WINDOWS.md`
- `docs/KONGYING_IMPORT.md`
- `docs/TRACKER_TODO.md`
- `docs/WINDOWS_RUNBOOK.md`
- `docs/ENGLISH_LOCALIZATION.md`
- `docs/PROJECT_CLEANUP.md`

The clean tracker does not run KongYing executables, does not load KongYing
DLLs, and does not use the legacy `cvAutoTrack` runtime.

## Windows exe build

Legacy note: this section documents the older cvAutoTrack build path and is
not used by the clean tracker rebuild.

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


## RUN on windows
cd "C:\Users\Amrit\OneDrive\Documents\GitHub\Genshin-Live-Tracker-Map"
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Live Tracker
.\.venv\Scripts\python.exe -m tracker_core.tracker_loop --once
.\.venv\Scripts\python.exe -m tracker_core.tracker_loop

# Map Front End:
cd external\map_front_v3
corepack enable
pnpm install
pnpm dev

# Map Backend
cd external\map_front_v3
pnpm build
