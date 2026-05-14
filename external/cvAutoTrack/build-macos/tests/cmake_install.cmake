# Install script for directory: /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/tests

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/install")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set path to fallback-tool for dependency-resolution.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/algorithms_direction/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/algorithms_feature_merge/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/algorithms_features_build/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/algorithms_features_erase/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/algorithms_match_surf/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/algorithms_rotation/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/api_GetCompileVersion/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/binary_image/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/capture_scale/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/container_treeset/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/curl_download_cache/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/example/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/frame_capture_bitblt/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/frame_capture_call/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/frame_capture_direct3d_surface/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/frame_capture_window_graphics/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/frame_local_picture/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/frame_local_video/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/impl_cpp/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/impl_csharp/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/impl_python/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/impl_runtime_load/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/logger_stdlog/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/perl_macth/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/v2_call_debugger/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/xfeatures_perl/cmake_install.cmake")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/tests/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
