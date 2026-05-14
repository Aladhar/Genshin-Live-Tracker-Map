#!/usr/bin/env bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
CONFIGURATION="Release"
BUILD_DIR=""
VCPKG_ROOT=""
INSTALL_VCPKG=false
RUN_SMOKE_TEST=false
ARCHITECTURE=""  # auto-detect by default

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--configuration)
            CONFIGURATION="$2"
            shift 2
            ;;
        -b|--build-dir)
            BUILD_DIR="$2"
            shift 2
            ;;
        -v|--vcpkg-root)
            VCPKG_ROOT="$2"
            shift 2
            ;;
        --install-vcpkg)
            INSTALL_VCPKG=true
            shift
            ;;
        --run-smoke-test)
            RUN_SMOKE_TEST=true
            shift
            ;;
        -a|--architecture)
            ARCHITECTURE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -c, --configuration CONFIG     Build configuration (Debug, Release) [default: Release]"
            echo "  -b, --build-dir DIR            Build directory [default: external/cvAutoTrack/build-macos]"
            echo "  -v, --vcpkg-root ROOT          vcpkg root directory"
            echo "  --install-vcpkg               Install vcpkg if not found"
            echo "  --run-smoke-test              Run smoke tests after build"
            echo "  -a, --architecture ARCH        Target architecture (x64, arm64, universal) [default: native]"
            echo "  -h, --help                     Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Determine repo root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${REPO_ROOT}/external/cvAutoTrack"

if [[ ! -d "$PROJECT_DIR" ]]; then
    echo -e "${RED}Error: cvAutoTrack project not found at $PROJECT_DIR${NC}"
    exit 1
fi

# Set default build directory
if [[ -z "$BUILD_DIR" ]]; then
    BUILD_DIR="${PROJECT_DIR}/build-macos"
fi

# Auto-detect architecture if not specified
if [[ -z "$ARCHITECTURE" ]]; then
    ARCH_NAME=$(uname -m)
    if [[ "$ARCH_NAME" == "arm64" ]]; then
        ARCHITECTURE="arm64"
    elif [[ "$ARCH_NAME" == "x86_64" ]]; then
        ARCHITECTURE="x64"
    else
        echo -e "${RED}Error: Unknown architecture: $ARCH_NAME${NC}"
        exit 1
    fi
fi

# Determine vcpkg triplet based on architecture
case "$ARCHITECTURE" in
    arm64)
        VCPKG_TRIPLET="arm64-osx"
        ;;
    x64|x86_64)
        VCPKG_TRIPLET="x64-osx"
        ;;
    universal)
        echo -e "${YELLOW}Warning: Universal binary support not yet fully implemented${NC}"
        VCPKG_TRIPLET="arm64-osx"  # Use ARM64 as primary
        ;;
    *)
        echo -e "${RED}Error: Unknown architecture: $ARCHITECTURE${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Genshin Live Tracker - macOS Build${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Repository root: $REPO_ROOT"
echo "Project dir:     $PROJECT_DIR"
echo "Build dir:       $BUILD_DIR"
echo "Configuration:   $CONFIGURATION"
echo "Architecture:    $ARCHITECTURE"
echo "vcpkg triplet:   $VCPKG_TRIPLET"
echo ""

# Find or install vcpkg
RESOLVED_VCPKG_ROOT=""

# Check provided vcpkg root
if [[ -n "$VCPKG_ROOT" && -d "$VCPKG_ROOT" ]]; then
    if [[ -f "$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" ]]; then
        RESOLVED_VCPKG_ROOT="$VCPKG_ROOT"
    fi
fi

# Check environment variable
if [[ -z "$RESOLVED_VCPKG_ROOT" && -n "$VCPKG_ROOT" ]]; then
    RESOLVED_VCPKG_ROOT="$VCPKG_ROOT"
fi

# Check repository-local vcpkg
if [[ -z "$RESOLVED_VCPKG_ROOT" && -d "${REPO_ROOT}/external/vcpkg" ]]; then
    if [[ -f "${REPO_ROOT}/external/vcpkg/scripts/buildsystems/vcpkg.cmake" ]]; then
        RESOLVED_VCPKG_ROOT="${REPO_ROOT}/external/vcpkg"
    fi
fi

# Check system-wide vcpkg locations
if [[ -z "$RESOLVED_VCPKG_ROOT" ]]; then
    for candidate in "/usr/local/vcpkg" "/opt/vcpkg" "$HOME/.vcpkg"; do
        if [[ -f "$candidate/scripts/buildsystems/vcpkg.cmake" ]]; then
            RESOLVED_VCPKG_ROOT="$candidate"
            break
        fi
    done
fi

# If still not found, offer to install
if [[ -z "$RESOLVED_VCPKG_ROOT" ]]; then
    LOCAL_VCPKG_ROOT="${REPO_ROOT}/external/vcpkg"
    if $INSTALL_VCPKG; then
        echo -e "${YELLOW}Installing vcpkg to $LOCAL_VCPKG_ROOT${NC}"
        if ! command -v git &> /dev/null; then
            echo -e "${RED}Error: git is required to install vcpkg automatically${NC}"
            exit 1
        fi
        git clone https://github.com/microsoft/vcpkg.git "$LOCAL_VCPKG_ROOT"
        chmod +x "$LOCAL_VCPKG_ROOT/bootstrap-vcpkg.sh"
        "$LOCAL_VCPKG_ROOT/bootstrap-vcpkg.sh" -disableMetrics
        RESOLVED_VCPKG_ROOT="$LOCAL_VCPKG_ROOT"
    else
        echo -e "${RED}Error: vcpkg not found. Re-run with --install-vcpkg to install, or set VCPKG_ROOT${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}Using vcpkg: $RESOLVED_VCPKG_ROOT${NC}"
export VCPKG_ROOT="$RESOLVED_VCPKG_ROOT"

# Some vcpkg ports generate shell commands for custom build steps. Those
# commands can break when the buildtrees path contains shell metacharacters
# such as '&' from this repository's default folder name.
VCPKG_WORK_ROOT="${VCPKG_WORK_ROOT:-/private/tmp/genshin-live-tracker-vcpkg/${VCPKG_TRIPLET}}"
VCPKG_BUILDTREES_ROOT="${VCPKG_WORK_ROOT}/buildtrees"
mkdir -p "$VCPKG_BUILDTREES_ROOT"

CMAKE_VCPKG_INSTALL_OPTIONS="${VCPKG_INSTALL_OPTIONS:-}"
if [[ "$CMAKE_VCPKG_INSTALL_OPTIONS" != *"--x-buildtrees-root"* ]]; then
    if [[ -n "$CMAKE_VCPKG_INSTALL_OPTIONS" ]]; then
        CMAKE_VCPKG_INSTALL_OPTIONS="--x-buildtrees-root=${VCPKG_BUILDTREES_ROOT};${CMAKE_VCPKG_INSTALL_OPTIONS}"
    else
        CMAKE_VCPKG_INSTALL_OPTIONS="--x-buildtrees-root=${VCPKG_BUILDTREES_ROOT}"
    fi
fi
echo "vcpkg work root: $VCPKG_WORK_ROOT"

# Ensure vcpkg is bootstrapped
if [[ ! -f "$RESOLVED_VCPKG_ROOT/vcpkg" ]]; then
    echo -e "${YELLOW}Bootstrapping vcpkg...${NC}"
    chmod +x "$RESOLVED_VCPKG_ROOT/bootstrap-vcpkg.sh"
    "$RESOLVED_VCPKG_ROOT/bootstrap-vcpkg.sh" -disableMetrics
fi

# Create build directory
mkdir -p "$BUILD_DIR"

# Check for required build tools
echo -e "${GREEN}Checking build tools...${NC}"
if ! command -v clang &> /dev/null; then
    echo -e "${RED}Error: clang compiler not found${NC}"
    echo "Please install Xcode Command Line Tools:"
    echo "  xcode-select --install"
    exit 1
fi

if ! command -v ninja &> /dev/null; then
    echo -e "${YELLOW}Ninja not found, installing via Homebrew...${NC}"
    if command -v brew &> /dev/null; then
        brew install ninja
    else
        echo -e "${RED}Error: Ninja build tool not found and Homebrew not available${NC}"
        echo "Please install: brew install ninja"
        exit 1
    fi
fi

# Configure with CMake
echo -e "${GREEN}Configuring cvAutoTrack...${NC}"
cmake -S "$PROJECT_DIR" \
    -B "$BUILD_DIR" \
    -DCMAKE_BUILD_TYPE="$CONFIGURATION" \
    -DVCPKG_TARGET_TRIPLET="$VCPKG_TRIPLET" \
    -DCMAKE_TOOLCHAIN_FILE="$RESOLVED_VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" \
    -DCMAKE_C_COMPILER="/usr/bin/clang" \
    -DCMAKE_CXX_COMPILER="/usr/bin/clang++" \
    -DCMAKE_MAKE_PROGRAM="$(command -v ninja)" \
    -DVCPKG_INSTALL_OPTIONS="$CMAKE_VCPKG_INSTALL_OPTIONS" \
    -G "Ninja" \
    -DBUILD_CVAUTOTRACK_TESTS=OFF \
    -DBUILD_CAPTURE_DXGI=OFF \
    -DBUILD_SUPPORT_WINRT=OFF \
    -DBUILD_SUPPORT_WINDUMP=OFF

# Build
echo -e "${GREEN}Building cvAutoTrack...${NC}"
cmake --build "$BUILD_DIR" --config "$CONFIGURATION" --target cvAutoTrack macos_capture_probe genshin_tracker_macos

BIN_DIR="${BUILD_DIR}/bin"
LIB_DIR="${BUILD_DIR}/lib"
CAPTURE_PROBE="${BIN_DIR}/macos_capture_probe"
TRACKER_CLI="${BIN_DIR}/genshin_tracker_macos"
LIB_FILE="${LIB_DIR}/libcvAutoTrack.dylib"

# Verify outputs
if [[ ! -f "$LIB_FILE" ]]; then
    echo -e "${RED}Error: Library not created at $LIB_FILE${NC}"
    exit 1
fi

if [[ ! -x "$CAPTURE_PROBE" ]]; then
    echo -e "${RED}Error: macOS capture probe not created at $CAPTURE_PROBE${NC}"
    exit 1
fi

if [[ ! -x "$TRACKER_CLI" ]]; then
    echo -e "${RED}Error: macOS tracker executable not created at $TRACKER_CLI${NC}"
    exit 1
fi

echo -e "${GREEN}Build completed successfully!${NC}"
echo "Library:     $LIB_FILE"
echo "Probe:       $CAPTURE_PROBE"
echo "Tracker CLI: $TRACKER_CLI"
echo ""

# Run smoke tests if requested
if $RUN_SMOKE_TEST; then
    echo -e "${GREEN}Running smoke tests...${NC}"
    file "$LIB_FILE"
    otool -L "$LIB_FILE"
    echo -e "${GREEN}Smoke tests passed!${NC}"
fi

echo -e "${GREEN}Done!${NC}"
