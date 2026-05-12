cmake_minimum_required(VERSION 3.15)

#=======================================================================================================================
# Configure vcpkg.
include(cmake/vcpkg_env.cmake)
#=======================================================================================================================
project(cvAutoTrack)
#=======================================================================================================================
# Configure vcpkg package search paths.
list(APPEND CMAKE_PREFIX_PATH "${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}")
#=======================================================================================================================
# Configure output directories.
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/install)
#=======================================================================================================================
# Configure project directories.
set(DependentPatryDir ${CMAKE_SOURCE_DIR}/dependent_party)
set(ThridPatryDir ${CMAKE_SOURCE_DIR}/third_party)
set(IncludeDir ${CMAKE_SOURCE_DIR}/include)
set(SourceDir ${CMAKE_SOURCE_DIR}/source)
#=======================================================================================================================
include(cmake/auto_subdirectory.cmake)
include(cmake/add_pch_configure.cmake)
#=======================================================================================================================
include(cmake/parse_version.cmake)
auto_increment_version_file("source/resource/version_hash.hash" "source/resource/version.ver")
parse_version_file("source/resource/version.ver")
get_commit_hash(PROJECT_VERSION_HASH)
get_git_branch(PROJECT_VERSION_BRANCH)
#=======================================================================================================================
set(BUILD_DYANMIC_LINK_DEPS OFF CACHE BOOL "Dynamically link dependency libraries")
set(BUILD_CVAUTOTRACK_TESTS OFF CACHE BOOL "Build tests")
set(BUILD_DOC OFF CACHE BOOL "Build documentation")

#=======================================================================================================================
set(BUILD_CAPTURE_DXGI ON CACHE BOOL "Build DXGI capture support")
set(BUILD_SUPPORT_WINRT ON CACHE BOOL "Support WinRT APIs")
set(BUILD_SUPPORT_WINDUMP ON CACHE BOOL "Support Windows dump files")
set(BUILD_CVAUTOTRACK_TESTS ON)

include_directories(${IncludeDir})
include_directories(${ThridPatryDir})
include_directories(${DependentPatryDir})

#=======================================================================================================================
# Configure compiler options.
set(CMAKE_CXX_STANDARD 17)
if(MSVC)
    add_compile_options(/std:c++17)
    add_definitions(-DUNICODE -D_UNICODE -DNOMINMAX)
endif()
add_compile_options(/utf-8)
#=======================================================================================================================
set_property(GLOBAL PROPERTY USE_FOLDERS ON)
set_property(GLOBAL PROPERTY PREDEFINED_TARGETS_FOLDER "cmake_targets")
#=======================================================================================================================
# Include subprojects.
add_subdirectory(source)
if(BUILD_CVAUTOTRACK_TESTS)
    message(STATUS "Build targets: cvAutoTrack, tests")
    add_subdirectory(tests)
else()
    message(STATUS "Build targets: cvAutoTrack only")
    message(STATUS "   Set BUILD_CVAUTOTRACK_TESTS=ON to build tests.")
endif()
#=======================================================================================================================
message(STATUS "==============================================================")
message(STATUS "Config:")
message(STATUS "    Version                    : ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}")
message(STATUS "    Product name               : ${PROJECT_NAME}")
message(STATUS "    Dynamic dependency linking : ${BUILD_DYANMIC_LINK_DEPS}")
message(STATUS "    Build tests                : ${BUILD_CVAUTOTRACK_TESTS}")
message(STATUS "Resource:")
message(STATUS "    Map count                  : ${model_rec_file}")
message(STATUS "Include:")
message(STATUS "    include_dir                : ${IncludeDir}")
message(STATUS "Install:")
message(STATUS "    CMAKE_INSTALL_PREFIX       : ${CMAKE_INSTALL_PREFIX}")
message(STATUS "==============================================================\n")
