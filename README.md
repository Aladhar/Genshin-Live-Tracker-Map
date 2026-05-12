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
