# macOS vcpkg Configuration Guide

## vcpkg Triplets for macOS

When building for macOS, vcpkg uses different triplets depending on the target architecture:

### Available Triplets

- **x64-osx**: Intel Mac (x86_64 architecture)
- **arm64-osx**: Apple Silicon Mac (ARM64 architecture)

## Auto-Detection

The CMake build system automatically detects the correct triplet based on:

1. **Explicit setting**: `-DVCPKG_TARGET_TRIPLET=arm64-osx` at configure time
2. **Build script parameter**: `bash build-macos.sh --architecture arm64`
3. **System detection**: Checks `CMAKE_SYSTEM_PROCESSOR` and native architecture
4. **File setting**: `.vcpkg-target-triplet` file in the project root

## Building for Specific Architectures

### Intel Mac (x64)

```bash
bash build-macos.sh --architecture x64 --install-vcpkg
```

This will:
- Set `VCPKG_TARGET_TRIPLET=x64-osx`
- Build OpenCV and dependencies for x86_64
- Create `libcvAutoTrack.dylib` (x86_64 version)

### Apple Silicon Mac (arm64)

```bash
bash build-macos.sh --architecture arm64 --install-vcpkg
```

This will:
- Set `VCPKG_TARGET_TRIPLET=arm64-osx`
- Build OpenCV and dependencies for ARM64
- Create `libcvAutoTrack.dylib` (arm64 version)

### Native Architecture (Default)

```bash
bash build-macos.sh --install-vcpkg
```

The system will automatically detect and use the native architecture.

## Dependencies with macOS Support

All dependencies in `vcpkg.json` support macOS builds:

- **fmt**: Header-only formatting library
- **cereal**: Serialization library
- **glad**: OpenGL loader (uses system OpenGL on macOS)
- **glfw3**: Window creation library
- **imgui**: UI library with OpenGL3 binding
- **opencv**: Computer vision library (crucial for screenshot processing)
- **tracy**: Profiling library

## OpenCV on macOS

OpenCV is the most critical dependency. Key points:

1. **Installation**: Installs both Intel and ARM64 variants on macOS 12+
2. **Features enabled**: contrib, nonfree, opengl, tbb, ipp
3. **Version**: 4.10.0#1 (from vcpkg.json overrides)
4. **System OpenGL**: macOS provides OpenGL natively

## Troubleshooting vcpkg on macOS

### vcpkg not found

Set the VCPKG_ROOT environment variable:

```bash
export VCPKG_ROOT="/path/to/vcpkg"
bash build-macos.sh
```

### Triplet mismatch errors

If you get architecture mismatch errors, explicitly specify the triplet:

```bash
bash build-macos.sh --architecture arm64
```

### Dependency not available for triplet

Some packages may not have prebuilt binaries for your triplet. They will be built from source, which takes longer.

### Clear vcpkg cache

If you encounter persistent build issues:

```bash
rm -rf external/vcpkg/installed
rm -rf external/vcpkg/buildtrees
bash build-macos.sh --install-vcpkg
```

## Future Enhancements

- [ ] Universal binary support (both Intel and ARM64 in single .dylib)
- [ ] Pre-built vcpkg binary cache for faster builds
- [ ] macOS package (DMG) distribution
