#!/usr/bin/env bash

# macOS Smoke Tests for Genshin Live Tracker & Map
# This script validates that all platform components work correctly

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

print_header() {
    echo ""
    echo -e "${GREEN}=== $1 ===${NC}"
    echo ""
}

print_test() {
    echo -n "Testing $1... "
}

test_pass() {
    echo -e "${GREEN}✓${NC}"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}✗${NC}"
    echo -e "${RED}  Error: $1${NC}"
    ((TESTS_FAILED++))
}

# ============================================================================
# SYSTEM REQUIREMENTS CHECKS
# ============================================================================

print_header "System Requirements"

print_test "macOS version"
MACOS_VERSION=$(sw_vers -productVersion)
MACOS_MAJOR=$(echo $MACOS_VERSION | cut -d. -f1)
if [[ $MACOS_MAJOR -ge 12 ]]; then
    test_pass
else
    test_fail "macOS 12.0 or later required (found $MACOS_VERSION)"
fi

print_test "Xcode Command Line Tools"
if command -v clang &> /dev/null; then
    test_pass
else
    test_fail "Xcode Command Line Tools not installed"
fi

print_test "CMake"
if command -v cmake &> /dev/null; then
    CMAKE_VERSION=$(cmake --version | head -n1)
    test_pass
    echo "    Found: $CMAKE_VERSION"
else
    test_fail "CMake not installed"
fi

print_test "Python 3"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    test_pass
    echo "    Found: $PYTHON_VERSION"
else
    test_fail "Python 3 not installed"
fi

# ============================================================================
# REPOSITORY STRUCTURE
# ============================================================================

print_header "Repository Structure"

print_test "cvAutoTrack project exists"
if [[ -d "external/cvAutoTrack" ]]; then
    test_pass
else
    test_fail "cvAutoTrack directory not found"
fi

print_test "Build script exists"
if [[ -f "build-macos.sh" ]]; then
    test_pass
else
    test_fail "build-macos.sh not found"
fi

print_test "macOS-specific files exist"
if [[ -f "external/cvAutoTrack/source/frame/capture/capture.coregraphics.h" ]] && \
   [[ -f "external/cvAutoTrack/source/frame/capture/capture.coregraphics.cpp" ]]; then
    test_pass
else
    test_fail "macOS Core Graphics capture files missing"
fi

print_test "GitHub Actions workflow exists"
if [[ -f ".github/workflows/macos-build.yml" ]]; then
    test_pass
else
    test_fail "macOS GitHub Actions workflow missing"
fi

# ============================================================================
# PYTHON TOOLS CHECKS
# ============================================================================

print_header "Python Tools"

print_test "chest_detector requirements"
if [[ -f "tools/chest_detector/requirements.txt" ]]; then
    test_pass
else
    test_fail "chest_detector requirements.txt not found"
fi

print_test "Python dependencies installable"
if python3 -m pip list &> /dev/null; then
    test_pass
else
    test_fail "pip not available"
fi

# ============================================================================
# C++ BUILD PREREQUISITES
# ============================================================================

print_header "C++ Build Prerequisites"

print_test "Architecture detection"
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]] || [[ "$ARCH" == "x86_64" ]]; then
    test_pass
    echo "    Detected: $ARCH"
else
    test_fail "Unknown architecture: $ARCH"
fi

print_test "vcpkg repository structure"
VCPKG_JSON="external/cvAutoTrack/vcpkg.json"
if [[ -f "$VCPKG_JSON" ]]; then
    if grep -q "opencv" "$VCPKG_JSON"; then
        test_pass
    else
        test_fail "OpenCV not in vcpkg.json"
    fi
else
    test_fail "vcpkg.json not found"
fi

print_test "CMakeLists.txt platform support"
CMAKE_FILE="external/cvAutoTrack/CMakeLists.txt"
if grep -q "BUILD_CAPTURE_COREGRAPHICS\|APPLE" "$CMAKE_FILE"; then
    test_pass
else
    test_fail "macOS configuration not found in CMakeLists.txt"
fi

# ============================================================================
# DOCUMENTATION
# ============================================================================

print_header "Documentation"

print_test "README has macOS instructions"
if grep -q "macOS\|macos\|Mac" "README.md"; then
    test_pass
else
    test_fail "macOS documentation missing from README"
fi

print_test "MACOS_SUPPORT_CHECKLIST exists"
if [[ -f "MACOS_SUPPORT_CHECKLIST.md" ]]; then
    test_pass
else
    test_fail "Checklist file missing"
fi

print_test "vcpkg macOS guide exists"
if [[ -f "external/cvAutoTrack/MACOS_VCPKG_GUIDE.md" ]]; then
    test_pass
else
    test_fail "vcpkg guide missing"
fi

# ============================================================================
# WEB APPLICATIONS
# ============================================================================

print_header "Web Applications"

print_test "map_front_v3 package.json"
if [[ -f "external/map_front_v3/package.json" ]]; then
    test_pass
else
    test_fail "map_front_v3 package.json not found"
fi

print_test "map_register_v3 package.json"
if [[ -f "external/map_register_v3/package.json" ]]; then
    test_pass
else
    test_fail "map_register_v3 package.json not found"
fi

print_test "VitePress docs package.json"
if [[ -f "external/docs/package.json" ]]; then
    test_pass
else
    test_fail "docs package.json not found"
fi

# ============================================================================
# PERMISSIONS & SECURITY
# ============================================================================

print_header "Permissions & Security"

print_test "build-macos.sh is executable"
if [[ -x "build-macos.sh" ]]; then
    test_pass
else
    # Make it executable if it exists
    if [[ -f "build-macos.sh" ]]; then
        chmod +x build-macos.sh
        test_pass
        echo "    Made executable"
    else
        test_fail "build-macos.sh not found"
    fi
fi

# ============================================================================
# SUMMARY
# ============================================================================

print_header "Test Summary"

TOTAL=$((TESTS_PASSED + TESTS_FAILED))
echo "Total Tests: $TOTAL"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}✓ All smoke tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run: bash build-macos.sh --install-vcpkg --run-smoke-test"
    echo "2. This will build the cvAutoTrack library for your architecture"
    echo "3. Build time depends on whether OpenCV needs compilation (~15-45 min)"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}✗ Some tests failed. Please review the errors above.${NC}"
    echo ""
    exit 1
fi
