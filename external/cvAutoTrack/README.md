# Genshin Impact AutoTrack DLL

This project builds a Windows DLL that reads the character position from the
Genshin Impact client by using screenshot capture and image matching.

[![GitHub version](https://badge.fury.io/gh/GengGode%2FcvAutoTrack.svg)](https://badge.fury.io/gh/GengGode%2FcvAutoTrack)
[![dev-window-dynamic](https://github.com/GengGode/cvAutoTrack/actions/workflows/dev-window-dynamic.yml/badge.svg)](https://github.com/GengGode/cvAutoTrack/actions/workflows/dev-window-dynamic.yml)
![convention](https://img.shields.io/badge/convention-__stdcall-orange.svg)
![platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![cpu](https://img.shields.io/badge/cpu-AMD64-purple.svg)

## Notes

- The tracker uses screenshots of the game window and image processing. It does
  not read or write game memory.
- For best results, use these Genshin Impact settings:
  - Settings > Graphics > Anti-Aliasing: `SMAA`
  - Settings > Other > Minimap Lock: `Lock Direction`

## Build On Windows

From the repository root:

```powershell
.\build-windows-exe.ps1 -InstallVcpkg -RunSmokeTest
```

After the build finishes, run:

```powershell
.\external\cvAutoTrack\build-windows\bin\Release\test_impl_cpp.exe
```

Main outputs:

- `build-windows\bin\Release\cvAutoTrack.dll`
- `build-windows\bin\Release\test_impl_cpp.exe`

## How To Use

1. Load `cvAutoTrack.dll` from your application.
2. Call or wrap the exported functions from `include/cvAutoTrack.h`.
3. Use `test_impl_cpp.exe` as the C++ command-line example.
4. Coordinates are returned in the Tianli coordinate model, so convert them to
   your map coordinate system if needed.

## Developer Layout

- `source`: DLL source code.
- `include`: public headers.
- `tests`: C++ test and sample executables.
- `doc`: upstream documentation.

## Credits

- [OpenCV](https://opencv.org/)
- [Kongying Tavern Genshin Map](https://yuanshen.site/docs/)
