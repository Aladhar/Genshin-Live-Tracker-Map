# Genshin Live Tracker & Map

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

