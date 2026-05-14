# Genshin Live Tracker & Map

## Build Instructions

### Windows Build

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

### macOS Build

#### System Requirements

- macOS 12.0 or later
- Xcode Command Line Tools: `xcode-select --install`
- Homebrew: [https://brew.sh](https://brew.sh)

#### Installation

Install dependencies:

```bash
brew install cmake ninja opencv
```

Build with the provided script:

```bash
# For native architecture (auto-detected)
bash build-macos.sh --install-vcpkg --run-smoke-test

# For specific architecture (x64 or arm64)
bash build-macos.sh --architecture arm64 --install-vcpkg --run-smoke-test
bash build-macos.sh --architecture x64 --install-vcpkg --run-smoke-test
```

The build creates:

- Library: `external/cvAutoTrack/build-macos/lib/libcvAutoTrack.dylib`
- Test executable: `external/cvAutoTrack/build-macos/bin/test_impl_cpp`

Run the test:

```bash
./external/cvAutoTrack/build-macos/bin/test_impl_cpp
```

#### Build Options

- `--architecture`: Specify target architecture (x64, arm64, or native)
- `--install-vcpkg`: Automatically install vcpkg if not found
- `--run-smoke-test`: Run tests after building
- `--build-dir`: Custom build directory
- `--configuration`: Debug or Release (default: Release)

#### macOS Architecture Support

- **Intel Macs (x86_64)**: `bash build-macos.sh --architecture x64`
- **Apple Silicon (arm64)**: `bash build-macos.sh --architecture arm64`

#### Permissions

On first run, macOS may prompt for screen recording permissions. Grant permission when requested for the screenshot capture to function correctly.

#### Troubleshooting

**OpenCV not found:**

```bash
brew install opencv
```

**vcpkg bootstrap fails:**

```bash
rm -rf external/vcpkg
bash build-macos.sh --install-vcpkg
```

**Architecture mismatch errors:**

- Ensure you're building for the correct architecture
- Use `uname -m` to check your system architecture (arm64 or x86_64)
