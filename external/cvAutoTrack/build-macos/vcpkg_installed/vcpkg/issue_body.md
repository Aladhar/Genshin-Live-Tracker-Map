Package: opencv4[calib3d,contrib,core,default-features,dnn,fs,gapi,highgui,intrinsics,jpeg,nonfree,opengl,png,quirc,thread,tiff,webp]:arm64-osx@4.10.0#1

**Host Environment**

- Host: arm64-osx
- Compiler: AppleClang 17.0.0.17000604
- CMake Version: 4.3.2
-    vcpkg-tool version: 2026-04-08-e0612b42ce44e55a0e630f2ee9d3c533a63d8bc1
    vcpkg-scripts version: 495848814a 2026-05-14 (10 hours ago)

**To Reproduce**

`vcpkg install `

**Failure logs**

```
-- Using cached opencv-opencv-4.10.0.tar.gz
-- Cleaning sources at /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/src/4.10.0-e5bca385b2.clean. Use --editable to skip cleaning for the packages you specify.
-- Extracting source /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/downloads/opencv-opencv-4.10.0.tar.gz
-- Applying patch 0001-disable-downloading.patch
-- Applying patch 0002-install-options.patch
-- Applying patch 0003-force-package-requirements.patch
-- Applying patch 0004-fix-eigen.patch
-- Applying patch 0005-fix-policy-CMP0057.patch
-- Applying patch 0006-fix-uwp.patch
-- Applying patch 0008-devendor-quirc.patch
-- Applying patch 0009-fix-protobuf.patch
-- Applying patch 0010-fix-uwp-tiff-imgcodecs.patch
-- Applying patch 0011-remove-python2.patch
-- Applying patch 0012-fix-zlib.patch
-- Applying patch 0014-fix-cmake-in-list.patch
-- Applying patch 0015-fix-freetype.patch
-- Applying patch 0017-fix-flatbuffers.patch
-- Applying patch 0019-opencl-kernel.patch
-- Applying patch 0020-miss-openexr.patch
-- Using source at /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/src/4.10.0-e5bca385b2.clean
-- Using cached opencv-cache/tiny_dnn/adb1c512e09ca2c7a6faef36f9c53e59-v1.0.0a3.tar.gz
-- Using cached opencv-opencv_contrib-4.10.0.tar.gz
-- Cleaning sources at /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/src/4.10.0-64012148a7.clean. Use --editable to skip cleaning for the packages you specify.
-- Extracting source /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/downloads/opencv-opencv_contrib-4.10.0.tar.gz
-- Applying patch 0007-contrib-fix-hdf5.patch
-- Applying patch 0013-contrib-fix-ogre.patch
-- Applying patch 0016-contrib-fix-freetype.patch
-- Applying patch 0018-contrib-fix-tesseract.patch
-- Using source at /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/src/4.10.0-64012148a7.clean
-- Using cached opencv-cache/wechat_qrcode/238e2b2d6f3c18d6c3a30de0c31e23cf-detect.caffemodel
-- Using cached opencv-cache/wechat_qrcode/cbfcd60361a73beb8c583eea7e8e6664-sr.caffemodel
-- Using cached opencv-cache/wechat_qrcode/6fb4976b32695f9f5c6305c19f12537d-detect.prototxt
-- Using cached opencv-cache/wechat_qrcode/69db99927a70df953b471daaba03fbef-sr.prototxt
-- Using cached opencv-cache/xfeatures2d/boostdesc/0ea90e7a8f3f7876d450e4149c97c74f-boostdesc_bgm.i
-- Using cached opencv-cache/xfeatures2d/boostdesc/232c966b13651bd0e46a1497b0852191-boostdesc_bgm_bi.i
-- Using cached opencv-cache/xfeatures2d/boostdesc/324426a24fa56ad9c5b8e3e0b3e5303e-boostdesc_bgm_hd.i
-- Using cached opencv-cache/xfeatures2d/boostdesc/202e1b3e9fec871b04da31f7f016679f-boostdesc_binboost_064.i
-- Using cached opencv-cache/xfeatures2d/boostdesc/98ea99d399965c03d555cef3ea502a0b-boostdesc_binboost_128.i
-- Using cached opencv-cache/xfeatures2d/boostdesc/e6dcfa9f647779eb1ce446a8d759b6ea-boostdesc_binboost_256.i
-- Using cached opencv-cache/xfeatures2d/boostdesc/0ae0675534aa318d9668f2a179c2a052-boostdesc_lbgm.i
-- Using cached opencv-cache/xfeatures2d/vgg/e8d0dcd54d1bcfdc29203d011a797179-vgg_generated_48.i
-- Using cached opencv-cache/xfeatures2d/vgg/7126a5d9a8884ebca5aea5d63d677225-vgg_generated_64.i
-- Using cached opencv-cache/xfeatures2d/vgg/7cd47228edec52b6d82f46511af325c5-vgg_generated_80.i
-- Using cached opencv-cache/xfeatures2d/vgg/151805e03568c9f490a5e3a872777b75-vgg_generated_120.i
-- Using cached opencv-cache/data/7505c44ca4eb54b4ab1e4777cb96ac05-face_landmark_model.dat
-- Configuring arm64-osx
CMake Error at scripts/cmake/vcpkg_execute_required_process.cmake:127 (message):
    Command failed: /opt/homebrew/bin/ninja -v
    Working Directory: /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/vcpkg-parallel-configure
    Error code: 1
    See logs for more information:
      /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/config-arm64-osx-dbg-CMakeCache.txt.log
      /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/config-arm64-osx-rel-CMakeCache.txt.log
      /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/config-arm64-osx-dbg-CMakeConfigureLog.yaml.log
      /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/config-arm64-osx-rel-CMakeConfigureLog.yaml.log
      /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/config-arm64-osx-out.log

Call Stack (most recent call first):
  /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed/arm64-osx/share/vcpkg-cmake/vcpkg_cmake_configure.cmake:269 (vcpkg_execute_required_process)
  /Users/amritladhar/.cache/vcpkg/registries/git-trees/6ba67264448ce7a60b8e109db62270331e657e38/portfile.cmake:332 (vcpkg_cmake_configure)
  scripts/ports.cmake:206 (include)



```

<details><summary>/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/config-arm64-osx-out.log</summary>

```
[1/2] "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/downloads/tools/cmake-4.3.2-osx/cmake-4.3.2-macos-universal/CMake.app/Contents/bin/cmake" -E chdir "../../arm64-osx-dbg" "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/downloads/tools/cmake-4.3.2-osx/cmake-4.3.2-macos-universal/CMake.app/Contents/bin/cmake" "/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/src/4.10.0-e5bca385b2.clean" "-G" "Ninja" "-DCMAKE_BUILD_TYPE=Debug" "-DCMAKE_INSTALL_PREFIX=/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/packages/opencv4_arm64-osx/debug" "-DFETCHCONTENT_FULLY_DISCONNECTED=ON" "-DENABLE_CONFIG_VERIFICATION=ON" "-DOPENCV_SKIP_SYSTEM_PROCESSOR_DETECTION=TRUE" "-DAARCH64=1" "-DX86_64=" "-DX86=" "-DARM=" "-DCMAKE_CXX_STANDARD=17" "-DINSTALL_TO_MANGLED_PATHS=OFF" "-DOpenCV_INSTALL_BINARIES_PREFIX=" "-DOPENCV_BIN_INSTALL_PATH=bin" "-DOPENCV_INCLUDE_INSTALL_PATH=include/opencv4" "-DOPENCV_LIB_INSTALL_PATH=lib" "-DOPENCV_3P_LIB_INSTALL_PATH=lib/manual-link/opencv4_thirdparty" "-DOPENCV_CONFIG_INSTALL_PATH=share/opencv4" "-DOPENCV_FFMPEG_USE_FIND_PACKAGE=FFMPEG" "-DOPENCV_FFMPEG_SKIP_BUILD_CHECK=TRUE" "-DCMAKE_DEBUG_POSTFIX=d" "-DOPENCV_DLLVERSION=4" "-DOPENCV_DEBUG_POSTFIX=d" "-DOPENCV_GENERATE_SETUPVARS=OFF" "-DOPENCV_GENERATE_PKGCONFIG=ON" "-DBUILD_DOCS=OFF" "-DBUILD_EXAMPLES=OFF" "-DBUILD_PERF_TESTS=OFF" "-DBUILD_TESTS=OFF" "-Dade_DIR=/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed/arm64-osx/share/ade" "-DBUILD_IPP_IW=OFF" "-DBUILD_ITT=OFF" "-DBUILD_JASPER=OFF" "-DBUILD_JPEG=OFF" "-DBUILD_OPENEXR=OFF" "-DBUILD_OPENJPEG=OFF" "-DBUILD_PNG=OFF" "-DBUILD_PROTOBUF=OFF" "-DBUILD_TBB=OFF" "-DBUILD_TIFF=OFF" "-DBUILD_WEBP=OFF" "-DBUILD_ZLIB=OFF" "-DBUILD_opencv_apps=OFF" "-DBUILD_opencv_java=OFF" "-DBUILD_opencv_js=OFF" "-DBUILD_JAVA=OFF" "-DBUILD_ANDROID_PROJECT=OFF" "-DBUILD_ANDROID_EXAMPLES=OFF" "-DBUILD_PACKAGE=OFF" "-DBUILD_WITH_DEBUG_INFO=ON" "-DBUILD_WITH_STATIC_CRT=0" "-DCURRENT_INSTALLED_DIR=/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed/arm64-osx" "-DENABLE_PYLINT=OFF" "-DENABLE_FLAKE8=OFF" "-DCMAKE_DISABLE_FIND_PACKAGE_Git=ON" "-DCMAKE_DISABLE_FIND_PACKAGE_JNI=ON" "-DENABLE_CXX11=ON" "-DOPENCV_DOWNLOAD_PATH=/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/downloads/opencv-cache" "-DOPENCV_EXTRA_MODULES_PATH=/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/src/4.10.0-64012148a7.clean/modules" "-DOPENCV_OTHER_INSTALL_PATH=share/opencv4" "-DWITH_ADE=OFF" "-DBUILD_opencv_calib3d=ON" "-DWITH_CONTRIB=ON" "-DWITH_CUBLAS=OFF" "-DWITH_CUDA=OFF" "-DENABLE_CUDA_FIRST_CLASS_LANGUAGE=OFF" "-DWITH_CUDNN=OFF" "-DWITH_1394=OFF" "-DBUILD_opencv_dnn=ON" "-DPROTOBUF_UPDATE_FILES=ON" "-DUPDATE_PROTO_FILES=ON" "-DWITH_PROTOBUF=ON" "-DOPENCV_DNN_CUDA=OFF" "-DWITH_DSHOW=OFF" "-DWITH_EIGEN=OFF" "-DWITH_FFMPEG=OFF" "-DWITH_FREETYPE=OFF" "-DBUILD_opencv_gapi=ON" "-DWITH_GDCM=OFF" "-DWITH_GSTREAMER=OFF" "-DWITH_GTK=OFF" "-DWITH_HALIDE=OFF" "-DWITH_IPP=OFF" "-DBUILD_IPP_IW=OFF" "-DBUILD_opencv_highgui=ON" "-DCV_ENABLE_INTRINSICS=ON" "-DWITH_JASPER=OFF" "-DWITH_OPENJPEG=OFF" "-DWITH_OPENMP=OFF" "-DWITH_JPEG=ON" "-DWITH_LAPACK=OFF" "-DDOPENCV_LAPACK_FIND_PACKAGE_ONLY=OFF" "-DWITH_MSMF=OFF" "-DOPENCV_ENABLE_NONFREE=ON" "-DOPENCV_ENABLE_FILESYSTEM_SUPPORT=ON" "-DOPENCV_ENABLE_THREAD_SUPPORT=ON" "-DWITH_OPENCL=OFF" "-DWITH_OPENVINO=OFF" "-DWITH_OPENEXR=OFF" "-DWITH_OPENGL=ON" "-DCMAKE_REQUIRE_FIND_PACKAGE_OGRE=OFF" "-DBUILD_opencv_ovis=OFF" "-DWITH_PNG=ON" "-DBUILD_opencv_python3=OFF" "-DWITH_PYTHON=OFF" "-DBUILD_opencv_quality=OFF" "-DWITH_QUIRC=ON" "-DBUILD_opencv_rgbd=OFF" "-DBUILD_opencv_sfm=OFF" "-DWITH_TBB=OFF" "-DWITH_TIFF=ON" "-DWITH_VTK=OFF" "-DWITH_VULKAN=OFF" "-
...
Skipped 2079 lines
...
-- 
--   Media I/O: 
--     ZLib:                        optimized /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed/arm64-osx/lib/libz.a debug /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed/arm64-osx/debug/lib/libz.a (ver 1.3.1)
--     JPEG:                        optimized /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed/arm64-osx/lib/libjpeg.a debug /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed/arm64-osx/debug/lib/libjpeg.a (ver 62)
--     WEBP:                        (ver 1.4.0)
--     PNG:                         optimized /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed/arm64-osx/lib/libpng16.a debug /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed/arm64-osx/debug/lib/libpng16d.a (ver 1.6.44)
--     TIFF:                        optimized /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed/arm64-osx/lib/libtiff.a debug /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed/arm64-osx/debug/lib/libtiffd.a (ver 42 / 4.7.0)
--     HDR:                         YES
--     SUNRASTER:                   YES
--     PXM:                         YES
--     PFM:                         YES
-- 
--   Video I/O:
--     AVFoundation:                YES
-- 
--   Parallel framework:            GCD
-- 
--   Trace:                         YES (built-in)
-- 
--   Other third-party libraries:
--     Custom HAL:                  YES (carotene (ver 0.0.1, Auto detected))
--     Protobuf:                    optimized /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed/arm64-osx/lib/libprotobuf.a debug /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed/arm64-osx/debug/lib/libprotobufd.a   version (29.1.0)
--     Flatbuffers:                 23.5.26
-- 
--   Python (for build):            NO
-- 
--   Install to:                    /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/packages/opencv4_arm64-osx
-- -----------------------------------------------------------------
-- 
-- Verifying WITH_1394=OFF => 'HAVE_DC1394_2'=FALSE
-- Verifying WITH_AVFOUNDATION=ON => 'HAVE_AVFOUNDATION'=TRUE
-- Verifying WITH_AVIF=OFF => 'HAVE_AVIF'=FALSE
-- Verifying WITH_CAP_IOS= => 'HAVE_CAP_IOS'=FALSE
-- Verifying WITH_CPUFEATURES=OFF => 'HAVE_CPUFEATURES'=FALSE
-- Verifying WITH_VTK=OFF => 'HAVE_VTK'=FALSE
-- Verifying WITH_CUDA=OFF => 'HAVE_CUDA'=FALSE
-- Verifying WITH_CUFFT= => 'HAVE_CUFFT'=FALSE
-- Verifying WITH_CUBLAS=OFF => 'HAVE_CUBLAS'=FALSE
-- Verifying WITH_CUDNN=OFF => 'HAVE_CUDNN'=FALSE
-- Verifying WITH_NVCUVID=OFF => 'HAVE_NVCUVID'=FALSE
-- Verifying WITH_NVCUVENC=OFF => 'HAVE_NVCUVENC'=FALSE
-- Verifying WITH_EIGEN=OFF => 'HAVE_EIGEN'=FALSE
-- Verifying WITH_FFMPEG=OFF => 'HAVE_FFMPEG'=FALSE
-- Verifying WITH_GSTREAMER=OFF => 'HAVE_GSTREAMER;AND;GSTREAMER_VERSION;VERSION_GREATER;0.99'=FALSE
-- Verifying WITH_GTK=OFF => 'HAVE_GTK'=FALSE
-- Verifying WITH_GTK_2_X= => 'HAVE_GTK;AND;NOT;HAVE_GTK3'=FALSE
-- Verifying WITH_WAYLAND= => 'HAVE_WAYLAND'=FALSE
-- Verifying WITH_IPP=OFF => 'HAVE_IPP'=FALSE
-- Verifying WITH_HALIDE=OFF => 'HAVE_HALIDE'=FALSE
-- Verifying WITH_VULKAN=OFF => 'HAVE_VULKAN'=FALSE
-- Verifying WITH_OPENVINO=OFF => 'TARGET;ocv.3rdparty.openvino'=FALSE
-- Verifying WITH_WEBNN=OFF => 'HAVE_WEBNN'=FALSE
-- Verifying WITH_JASPER=OFF => 'HAVE_JASPER'=FALSE
-- Verifying WITH_OPENJPEG=OFF => 'HAVE_OPENJPEG'=FALSE
-- Verifying WITH_JPEG=ON => 'HAVE_JPEG'=TRUE
-- Verifying WITH_WEBP=ON => 'HAVE_WEBP'=TRUE
-- Verifying WITH_OPENEXR=OFF => 'HAVE_OPENEXR'=FALSE
-- Verifying WITH_OPENGL=ON => 'HAVE_OPENGL'=FALSE
CMake Warning at cmake/OpenCVUtils.cmake:785 (message):
  Option WITH_OPENGL is enabled but corresponding dependency have not been
  found: "HAVE_OPENGL" is FALSE
Call Stack (most recent call first):
  CMakeLists.txt:1974 (ocv_verify_config)


-- Verifying WITH_OPENVX=OFF => 'HAVE_OPENVX'=FALSE
-- Verifying WITH_OPENNI=OFF => 'HAVE_OPENNI'=FALSE
-- Verifying WITH_OPENNI2=OFF => 'HAVE_OPENNI2'=FALSE
-- Verifying WITH_PNG=ON => 'HAVE_PNG'=TRUE
-- Verifying WITH_SPNG=OFF => 'HAVE_SPNG'=FALSE
-- Verifying WITH_GDCM=OFF => 'HAVE_GDCM'=FALSE
-- Verifying WITH_PVAPI=OFF => 'HAVE_PVAPI'=FALSE
-- Verifying WITH_ARAVIS=OFF => 'HAVE_ARAVIS_API'=FALSE
-- Verifying WITH_QT=OFF => 'HAVE_QT'=FALSE
-- Verifying WITH_WIN32UI=OFF => 'HAVE_WIN32UI'=FALSE
-- Verifying WITH_TBB=OFF => 'HAVE_TBB'=FALSE
-- Verifying WITH_HPX=OFF => 'HAVE_HPX'=FALSE
-- Verifying WITH_OPENMP=OFF => 'HAVE_OPENMP'=FALSE
-- Verifying WITH_PTHREADS_PF=ON => 'HAVE_PTHREADS_PF'=TRUE
-- Verifying WITH_TIFF=ON => 'HAVE_TIFF'=TRUE
-- Verifying WITH_V4L= => 'HAVE_CAMV4L;OR;HAVE_CAMV4L2;OR;HAVE_VIDEOIO'=FALSE
-- Verifying WITH_DSHOW=OFF => 'HAVE_DSHOW'=FALSE
-- Verifying WITH_MSMF=OFF => 'HAVE_MSMF'=FALSE
-- Verifying WITH_MSMF_DXVA= => 'HAVE_MSMF_DXVA'=FALSE
-- Verifying WITH_XIMEA=OFF => 'HAVE_XIMEA'=FALSE
-- Verifying WITH_UEYE= => 'HAVE_UEYE'=FALSE
-- Verifying WITH_XINE= => 'HAVE_XINE'=FALSE
-- Verifying WITH_CLP=OFF => 'HAVE_CLP'=FALSE
-- Verifying WITH_OPENCL=OFF => 'HAVE_OPENCL'=FALSE
-- Verifying WITH_OPENCL_SVM=OFF => 'HAVE_OPENCL_SVM'=FALSE
-- Verifying WITH_OPENCLAMDFFT=OFF => 'HAVE_CLAMDFFT'=FALSE
-- Verifying WITH_OPENCLAMDBLAS=OFF => 'HAVE_CLAMDBLAS'=FALSE
-- Verifying WITH_DIRECTX= => 'HAVE_DIRECTX'=FALSE
-- Verifying WITH_DIRECTML= => 'HAVE_DIRECTML'=FALSE
-- Verifying WITH_OPENCL_D3D11_NV=OFF => 'HAVE_OPENCL_D3D11_NV'=FALSE
-- Verifying WITH_LIBREALSENSE=OFF => 'HAVE_LIBREALSENSE'=FALSE
-- Verifying WITH_VA=OFF => 'HAVE_VA'=FALSE
-- Verifying WITH_VA_INTEL=OFF => 'HAVE_VA_INTEL'=FALSE
-- Verifying WITH_MFX=OFF => 'HAVE_MFX'=FALSE
-- Verifying WITH_GDAL=OFF => 'HAVE_GDAL'=FALSE
-- Verifying WITH_GPHOTO2=OFF => 'HAVE_GPHOTO2'=FALSE
-- Verifying WITH_LAPACK=OFF => 'HAVE_LAPACK'=FALSE
-- Verifying WITH_ITT=OFF => 'HAVE_ITT'=FALSE
-- Verifying WITH_PROTOBUF=ON => 'HAVE_PROTOBUF'=TRUE
-- Verifying WITH_IMGCODEC_HDR=ON => 'HAVE_IMGCODEC_HDR'=TRUE
-- Verifying WITH_IMGCODEC_SUNRASTER=ON => 'HAVE_IMGCODEC_SUNRASTER'=TRUE
-- Verifying WITH_IMGCODEC_PXM=ON => 'HAVE_IMGCODEC_PXM'=TRUE
-- Verifying WITH_IMGCODEC_PFM=ON => 'HAVE_IMGCODEC_PFM'=TRUE
-- Verifying WITH_QUIRC=ON => 'HAVE_QUIRC'=TRUE
-- Verifying WITH_ANDROID_MEDIANDK= => 'HAVE_ANDROID_MEDIANDK'=FALSE
-- Verifying WITH_ANDROID_NATIVE_CAMERA= => 'HAVE_ANDROID_NATIVE_CAMERA'=FALSE
-- Verifying WITH_ONNX=OFF => 'HAVE_ONNX'=FALSE
-- Verifying WITH_TIMVX=OFF => 'HAVE_TIMVX'=FALSE
-- Verifying WITH_OBSENSOR=OFF => 'HAVE_OBSENSOR'=FALSE
-- Verifying WITH_CANN=OFF => 'HAVE_CANN'=FALSE
-- Verifying WITH_FLATBUFFERS=ON => 'HAVE_FLATBUFFERS'=TRUE
-- Verifying WITH_ZLIB_NG=OFF => 'HAVE_ZLIB_NG'=FALSE
-- Verifying ENABLE_CUDA_FIRST_CLASS_LANGUAGE=OFF => 'HAVE_CUDA'=FALSE
-- Verifying WITH_TESSERACT=ON => 'HAVE_TESSERACT'=TRUE
CMake Error at cmake/OpenCVUtils.cmake:797 (message):
  Some dependencies have not been found or have been forced, unset
  ENABLE_CONFIG_VERIFICATION option to ignore these failures or change
  following options:

  WITH_OPENGL
Call Stack (most recent call first):
  CMakeLists.txt:1974 (ocv_verify_config)


-- Configuring incomplete, errors occurred!
CMake Warning:
  Value of OPENCV_BUILD_INFO_STR contained a newline; truncating


ninja: build stopped: subcommand failed.
```
</details>

<details><summary>/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/config-arm64-osx-rel-CMakeCache.txt.log</summary>

```
# This is the CMakeCache file.
# For build in directory: /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel
# It was generated by CMake: /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/downloads/tools/cmake-4.3.2-osx/cmake-4.3.2-macos-universal/CMake.app/Contents/bin/cmake
# You can edit this file to change values found and used by cmake.
# If you do not want to change any of the values, simply exit the editor.
# If you do want to change a value, simply edit, save, and exit the editor.
# The syntax for the file is as follows:
# KEY:TYPE=VALUE
# KEY is the name of a variable in the cache.
# TYPE is a hint to GUIs for the type of VALUE, DO NOT EDIT TYPE!.
# VALUE is the current value for the KEY.

########################
# EXTERNAL cache entries
########################

//No help, variable specified on the command line.
AARCH64:UNINITIALIZED=1

//No help, variable specified on the command line.
ARM:UNINITIALIZED=

//Path to a library.
BLAS_Accelerate_LIBRARY:FILEPATH=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/System/Library/Frameworks/Accelerate.framework

//Path to a library.
BLAS_acml_LIBRARY:FILEPATH=BLAS_acml_LIBRARY-NOTFOUND

//Path to a library.
BLAS_acml_mp_LIBRARY:FILEPATH=BLAS_acml_mp_LIBRARY-NOTFOUND

//Path to a library.
BLAS_armpl_lp64_LIBRARY:FILEPATH=BLAS_armpl_lp64_LIBRARY-NOTFOUND

//Path to a library.
BLAS_blas_LIBRARY:FILEPATH=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/lib/libblas.tbd

//Path to a library.
BLAS_blis_LIBRARY:FILEPATH=BLAS_blis_LIBRARY-NOTFOUND

//Path to a library.
BLAS_complib_sgimath_LIBRARY:FILEPATH=BLAS_complib_sgimath_LIBRARY-NOTFOUND

//Path to a library.
BLAS_cxml_LIBRARY:FILEPATH=BLAS_cxml_LIBRARY-NOTFOUND

//Path to a library.
BLAS_dxml_LIBRARY:FILEPATH=BLAS_dxml_LIBRARY-NOTFOUND

//Path to a library.
BLAS_essl_LIBRARY:FILEPATH=BLAS_essl_LIBRARY-NOTFOUND

//Path to a library.
BLAS_f77blas_LIBRARY:FILEPATH=BLAS_f77blas_LIBRARY-NOTFOUND

//Path to a library.
BLAS_flexiblas_LIBRARY:FILEPATH=BLAS_flexiblas_LIBRARY-NOTFOUND

//Path to a library.
BLAS_goto2_LIBRARY:FILEPATH=BLAS_goto2_LIBRARY-NOTFOUND

//Path to a library.
BLAS_mkl_LIBRARY:FILEPATH=BLAS_mkl_LIBRARY-NOTFOUND

//Path to a library.
BLAS_mkl_em64t_LIBRARY:FILEPATH=BLAS_mkl_em64t_LIBRARY-NOTFOUND

//Path to a library.
BLAS_mkl_ia32_LIBRARY:FILEPATH=BLAS_mkl_ia32_LIBRARY-NOTFOUND

//Path to a library.
BLAS_mkl_intel_LIBRARY:FILEPATH=BLAS_mkl_intel_LIBRARY-NOTFOUND

//Path to a library.
BLAS_mkl_intel_lp64_LIBRARY:FILEPATH=BLAS_mkl_intel_lp64_LIBRARY-NOTFOUND

//Path to a library.
BLAS_mkl_rt_LIBRARY:FILEPATH=BLAS_mkl_rt_LIBRARY-NOTFOUND

//Path to a library.
BLAS_openblas_LIBRARY:FILEPATH=BLAS_openblas_LIBRARY-NOTFOUND

//Path to a library.
BLAS_scs_LIBRARY:FILEPATH=BLAS_scs_LIBRARY-NOTFOUND

//Path to a library.
BLAS_sgemm_LIBRARY:FILEPATH=BLAS_sgemm_LIBRARY-NOTFOUND

//Path to a library.
BLAS_sunperf_LIBRARY:FILEPATH=BLAS_sunperf_LIBRARY-NOTFOUND

//No help, variable specified on the command line.
BUILD_ANDROID_EXAMPLES:UNINITIALIZED=OFF

//No help, variable specified on the command line.
BUILD_ANDROID_PROJECT:UNINITIALIZED=OFF

//Build CUDA modules stubs when no CUDA SDK
BUILD_CUDA_STUBS:BOOL=OFF

//Create build rules for OpenCV Documentation
BUILD_DOCS:BOOL=OFF

//Build all examples
BUILD_EXAMPLES:BOOL=OFF

//Create Java wrapper exporting all functions of OpenCV library
// (requires static build of OpenCV modules)
BUILD_FAT_JAVA_LIB:BOOL=OFF

//No help, variable specified on the command line.
BUILD_IPP_IW:UNINITIALIZED=OFF

//Build Intel ITT from source
BUILD_ITT:BOOL=OFF

//Build libjasper from source
BUILD_JASPER:BOOL=OFF

//Enable Java support
BUILD_JAVA:BOOL=OFF

//Build libjpeg from source
BUILD_JPEG:BOOL=OFF

...
Skipped 4677 lines
...
//List of wrappers supporting module opencv_xphoto
OPENCV_MODULE_opencv_xphoto_WRAPPERS:INTERNAL=python;java;objc
OPENCV_OBJC_BINDINGS_DIR:INTERNAL=/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/modules/objc_bindings_generator
OPENCV_PYTHON_BINDINGS_DIR:INTERNAL=/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/modules/python_bindings_generator
OPENCV_PYTHON_SIGNATURES_FILE:INTERNAL=/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/modules/python_bindings_generator/pyopencv_signatures.json
OPENCV_PYTHON_TESTS_CONFIG_FILE:INTERNAL=/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/opencv_python_tests.cfg
OPENCV_PYTHON_TESTS_CONFIG_FILE_DIR:INTERNAL=/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel
//List of OpenCV modules included into the world
OPENCV_WORLD_MODULES:INTERNAL=
//List of OpenCVModules targets
OpenCVModules_TARGETS:INTERNAL=tegra_hal;opencv_core;opencv_flann;opencv_hdf;opencv_imgproc;opencv_intensity_transform;opencv_ml;opencv_phase_unwrapping;opencv_photo;opencv_plot;opencv_reg;opencv_signal;opencv_surface_matching;opencv_xphoto;opencv_dnn;opencv_dnn_superres;opencv_features2d;opencv_fuzzy;opencv_hfs;opencv_img_hash;opencv_imgcodecs;opencv_line_descriptor;opencv_saliency;opencv_text;opencv_videoio;opencv_calib3d;opencv_datasets;opencv_highgui;opencv_mcc;opencv_objdetect;opencv_rapid;opencv_shape;opencv_structured_light;opencv_video;opencv_videostab;opencv_wechat_qrcode;opencv_xfeatures2d;opencv_ximgproc;opencv_xobjdetect;opencv_aruco;opencv_bgsegm;opencv_bioinspired;opencv_ccalib;opencv_dnn_objdetect;opencv_dpm;opencv_face;opencv_optflow;opencv_stitching;opencv_superres;opencv_tracking;opencv_stereo
//ADVANCED property for variable: PKG_CONFIG_ARGN
PKG_CONFIG_ARGN-ADVANCED:INTERNAL=1
//ADVANCED property for variable: PKG_CONFIG_EXECUTABLE
PKG_CONFIG_EXECUTABLE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: PNG_LIBRARY_DEBUG
PNG_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: PNG_LIBRARY_RELEASE
PNG_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: PNG_PNG_INCLUDE_DIR
PNG_PNG_INCLUDE_DIR-ADVANCED:INTERNAL=1
SFM_GLOG_GFLAGS_TEST:INTERNAL=TRUE
SFM_GLOG_GFLAGS_TEST_CACHE_KEY:INTERNAL= ~ /opt/homebrew/include ~ glog::glog ~ gflags_shared
//ADVANCED property for variable: SuiteSparse_AMD_INCLUDE_DIR
SuiteSparse_AMD_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_AMD_LIBRARY
SuiteSparse_AMD_LIBRARY-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_CAMD_INCLUDE_DIR
SuiteSparse_CAMD_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_CAMD_LIBRARY
SuiteSparse_CAMD_LIBRARY-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_CCOLAMD_INCLUDE_DIR
SuiteSparse_CCOLAMD_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_CCOLAMD_LIBRARY
SuiteSparse_CCOLAMD_LIBRARY-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_CHOLMOD_INCLUDE_DIR
SuiteSparse_CHOLMOD_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_CHOLMOD_LIBRARY
SuiteSparse_CHOLMOD_LIBRARY-ADVANCED:INTERNAL=1
//Have symbol cholmod_metis
SuiteSparse_CHOLMOD_USES_METIS:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_COLAMD_INCLUDE_DIR
SuiteSparse_COLAMD_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_COLAMD_LIBRARY
SuiteSparse_COLAMD_LIBRARY-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_Config_INCLUDE_DIR
SuiteSparse_Config_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_Config_LIBRARY
SuiteSparse_Config_LIBRARY-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_SPQR_INCLUDE_DIR
SuiteSparse_SPQR_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_SPQR_LIBRARY
SuiteSparse_SPQR_LIBRARY-ADVANCED:INTERNAL=1
//ADVANCED property for variable: TIFF_INCLUDE_DIR
TIFF_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: TIFF_LIBRARY_DEBUG
TIFF_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: TIFF_LIBRARY_RELEASE
TIFF_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//Install the dependencies listed in your manifest:
//\n    If this is off, you will have to manually install your dependencies.
//\n    See https://github.com/microsoft/vcpkg/tree/master/docs/specifications/manifests.md
// for more info.
//\n
VCPKG_MANIFEST_INSTALL:INTERNAL=OFF
//ADVANCED property for variable: VCPKG_VERBOSE
VCPKG_VERBOSE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: VIDEOIO_ENABLE_PLUGINS
VIDEOIO_ENABLE_PLUGINS-ADVANCED:INTERNAL=1
//ADVANCED property for variable: VIDEOIO_PLUGIN_LIST
VIDEOIO_PLUGIN_LIST-ADVANCED:INTERNAL=1
//ADVANCED property for variable: ZLIB_INCLUDE_DIR
ZLIB_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: ZLIB_LIBRARY_DEBUG
ZLIB_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: ZLIB_LIBRARY_RELEASE
ZLIB_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//Making sure VCPKG_MANIFEST_MODE doesn't change
Z_VCPKG_CHECK_MANIFEST_MODE:INTERNAL=OFF
//Vcpkg root directory
Z_VCPKG_ROOT_DIR:INTERNAL=/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg
//CMAKE_INSTALL_PREFIX during last run
_GNUInstallDirs_LAST_CMAKE_INSTALL_PREFIX:INTERNAL=/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/packages/opencv4_arm64-osx
__OPENCV_CMAKE_HOOKS_INIT_MODULE_SOURCES_opencv_dnn:INTERNAL=/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/src/4.10.0-e5bca385b2.clean/modules/dnn/cmake/hooks/INIT_MODULE_SOURCES_opencv_dnn.cmake
__OPENCV_EXPORTED_EXTERNAL_TARGETS:INTERNAL=ocv.3rdparty.flatbuffers;ocv.3rdparty.avfoundation
//ADVANCED property for variable: _vcpkg_sharpyuv_LIBRARY_DEBUG
_vcpkg_sharpyuv_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_sharpyuv_LIBRARY_RELEASE
_vcpkg_sharpyuv_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webp_LIBRARY_DEBUG
_vcpkg_webp_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webp_LIBRARY_RELEASE
_vcpkg_webp_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webpdecoder_LIBRARY_DEBUG
_vcpkg_webpdecoder_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webpdecoder_LIBRARY_RELEASE
_vcpkg_webpdecoder_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webpdemux_LIBRARY_DEBUG
_vcpkg_webpdemux_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webpdemux_LIBRARY_RELEASE
_vcpkg_webpdemux_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webpmux_LIBRARY_DEBUG
_vcpkg_webpmux_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webpmux_LIBRARY_RELEASE
_vcpkg_webpmux_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: protobuf_VERBOSE
protobuf_VERBOSE-ADVANCED:INTERNAL=1
```
</details>

<details><summary>/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/config-arm64-osx-dbg-CMakeCache.txt.log</summary>

```
# This is the CMakeCache file.
# For build in directory: /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg
# It was generated by CMake: /Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/downloads/tools/cmake-4.3.2-osx/cmake-4.3.2-macos-universal/CMake.app/Contents/bin/cmake
# You can edit this file to change values found and used by cmake.
# If you do not want to change any of the values, simply exit the editor.
# If you do want to change a value, simply edit, save, and exit the editor.
# The syntax for the file is as follows:
# KEY:TYPE=VALUE
# KEY is the name of a variable in the cache.
# TYPE is a hint to GUIs for the type of VALUE, DO NOT EDIT TYPE!.
# VALUE is the current value for the KEY.

########################
# EXTERNAL cache entries
########################

//No help, variable specified on the command line.
AARCH64:UNINITIALIZED=1

//No help, variable specified on the command line.
ARM:UNINITIALIZED=

//Path to a library.
BLAS_Accelerate_LIBRARY:FILEPATH=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/System/Library/Frameworks/Accelerate.framework

//Path to a library.
BLAS_acml_LIBRARY:FILEPATH=BLAS_acml_LIBRARY-NOTFOUND

//Path to a library.
BLAS_acml_mp_LIBRARY:FILEPATH=BLAS_acml_mp_LIBRARY-NOTFOUND

//Path to a library.
BLAS_armpl_lp64_LIBRARY:FILEPATH=BLAS_armpl_lp64_LIBRARY-NOTFOUND

//Path to a library.
BLAS_blas_LIBRARY:FILEPATH=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/lib/libblas.tbd

//Path to a library.
BLAS_blis_LIBRARY:FILEPATH=BLAS_blis_LIBRARY-NOTFOUND

//Path to a library.
BLAS_complib_sgimath_LIBRARY:FILEPATH=BLAS_complib_sgimath_LIBRARY-NOTFOUND

//Path to a library.
BLAS_cxml_LIBRARY:FILEPATH=BLAS_cxml_LIBRARY-NOTFOUND

//Path to a library.
BLAS_dxml_LIBRARY:FILEPATH=BLAS_dxml_LIBRARY-NOTFOUND

//Path to a library.
BLAS_essl_LIBRARY:FILEPATH=BLAS_essl_LIBRARY-NOTFOUND

//Path to a library.
BLAS_f77blas_LIBRARY:FILEPATH=BLAS_f77blas_LIBRARY-NOTFOUND

//Path to a library.
BLAS_flexiblas_LIBRARY:FILEPATH=BLAS_flexiblas_LIBRARY-NOTFOUND

//Path to a library.
BLAS_goto2_LIBRARY:FILEPATH=BLAS_goto2_LIBRARY-NOTFOUND

//Path to a library.
BLAS_mkl_LIBRARY:FILEPATH=BLAS_mkl_LIBRARY-NOTFOUND

//Path to a library.
BLAS_mkl_em64t_LIBRARY:FILEPATH=BLAS_mkl_em64t_LIBRARY-NOTFOUND

//Path to a library.
BLAS_mkl_ia32_LIBRARY:FILEPATH=BLAS_mkl_ia32_LIBRARY-NOTFOUND

//Path to a library.
BLAS_mkl_intel_LIBRARY:FILEPATH=BLAS_mkl_intel_LIBRARY-NOTFOUND

//Path to a library.
BLAS_mkl_intel_lp64_LIBRARY:FILEPATH=BLAS_mkl_intel_lp64_LIBRARY-NOTFOUND

//Path to a library.
BLAS_mkl_rt_LIBRARY:FILEPATH=BLAS_mkl_rt_LIBRARY-NOTFOUND

//Path to a library.
BLAS_openblas_LIBRARY:FILEPATH=BLAS_openblas_LIBRARY-NOTFOUND

//Path to a library.
BLAS_scs_LIBRARY:FILEPATH=BLAS_scs_LIBRARY-NOTFOUND

//Path to a library.
BLAS_sgemm_LIBRARY:FILEPATH=BLAS_sgemm_LIBRARY-NOTFOUND

//Path to a library.
BLAS_sunperf_LIBRARY:FILEPATH=BLAS_sunperf_LIBRARY-NOTFOUND

//No help, variable specified on the command line.
BUILD_ANDROID_EXAMPLES:UNINITIALIZED=OFF

//No help, variable specified on the command line.
BUILD_ANDROID_PROJECT:UNINITIALIZED=OFF

//Build CUDA modules stubs when no CUDA SDK
BUILD_CUDA_STUBS:BOOL=OFF

//Create build rules for OpenCV Documentation
BUILD_DOCS:BOOL=OFF

//Build all examples
BUILD_EXAMPLES:BOOL=OFF

//Create Java wrapper exporting all functions of OpenCV library
// (requires static build of OpenCV modules)
BUILD_FAT_JAVA_LIB:BOOL=OFF

//No help, variable specified on the command line.
BUILD_IPP_IW:UNINITIALIZED=OFF

//Build Intel ITT from source
BUILD_ITT:BOOL=OFF

//Build libjasper from source
BUILD_JASPER:BOOL=OFF

//Enable Java support
BUILD_JAVA:BOOL=OFF

//Build libjpeg from source
BUILD_JPEG:BOOL=OFF

//Build only listed modules (comma-separated, e.g. 'videoio,dnn,ts')
BUILD_LIST:STRING=

//Build openexr from source
BUILD_OPENEXR:BOOL=OFF

//Build OpenJPEG from source
BUILD_OPENJPEG:BOOL=OFF

//Enables 'make package_source' command
BUILD_PACKAGE:BOOL=OFF

...
Skipped 4665 lines
...
//List of wrappers supporting module opencv_xphoto
OPENCV_MODULE_opencv_xphoto_WRAPPERS:INTERNAL=python;java;objc
OPENCV_OBJC_BINDINGS_DIR:INTERNAL=/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg/modules/objc_bindings_generator
OPENCV_PYTHON_BINDINGS_DIR:INTERNAL=/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg/modules/python_bindings_generator
OPENCV_PYTHON_SIGNATURES_FILE:INTERNAL=/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg/modules/python_bindings_generator/pyopencv_signatures.json
OPENCV_PYTHON_TESTS_CONFIG_FILE:INTERNAL=/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg/opencv_python_tests.cfg
OPENCV_PYTHON_TESTS_CONFIG_FILE_DIR:INTERNAL=/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg
//List of OpenCV modules included into the world
OPENCV_WORLD_MODULES:INTERNAL=
//List of OpenCVModules targets
OpenCVModules_TARGETS:INTERNAL=tegra_hal;opencv_core;opencv_flann;opencv_hdf;opencv_imgproc;opencv_intensity_transform;opencv_ml;opencv_phase_unwrapping;opencv_photo;opencv_plot;opencv_reg;opencv_signal;opencv_surface_matching;opencv_xphoto;opencv_dnn;opencv_dnn_superres;opencv_features2d;opencv_fuzzy;opencv_hfs;opencv_img_hash;opencv_imgcodecs;opencv_line_descriptor;opencv_saliency;opencv_text;opencv_videoio;opencv_calib3d;opencv_datasets;opencv_highgui;opencv_mcc;opencv_objdetect;opencv_rapid;opencv_shape;opencv_structured_light;opencv_video;opencv_videostab;opencv_wechat_qrcode;opencv_xfeatures2d;opencv_ximgproc;opencv_xobjdetect;opencv_aruco;opencv_bgsegm;opencv_bioinspired;opencv_ccalib;opencv_dnn_objdetect;opencv_dpm;opencv_face;opencv_optflow;opencv_stitching;opencv_superres;opencv_tracking;opencv_stereo
//ADVANCED property for variable: PKG_CONFIG_ARGN
PKG_CONFIG_ARGN-ADVANCED:INTERNAL=1
//ADVANCED property for variable: PKG_CONFIG_EXECUTABLE
PKG_CONFIG_EXECUTABLE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: PNG_LIBRARY_DEBUG
PNG_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: PNG_LIBRARY_RELEASE
PNG_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: PNG_PNG_INCLUDE_DIR
PNG_PNG_INCLUDE_DIR-ADVANCED:INTERNAL=1
SFM_GLOG_GFLAGS_TEST:INTERNAL=TRUE
SFM_GLOG_GFLAGS_TEST_CACHE_KEY:INTERNAL= ~ /opt/homebrew/include ~ glog::glog ~ gflags_shared
//ADVANCED property for variable: SuiteSparse_AMD_INCLUDE_DIR
SuiteSparse_AMD_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_AMD_LIBRARY
SuiteSparse_AMD_LIBRARY-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_CAMD_INCLUDE_DIR
SuiteSparse_CAMD_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_CAMD_LIBRARY
SuiteSparse_CAMD_LIBRARY-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_CCOLAMD_INCLUDE_DIR
SuiteSparse_CCOLAMD_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_CCOLAMD_LIBRARY
SuiteSparse_CCOLAMD_LIBRARY-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_CHOLMOD_INCLUDE_DIR
SuiteSparse_CHOLMOD_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_CHOLMOD_LIBRARY
SuiteSparse_CHOLMOD_LIBRARY-ADVANCED:INTERNAL=1
//Have symbol cholmod_metis
SuiteSparse_CHOLMOD_USES_METIS:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_COLAMD_INCLUDE_DIR
SuiteSparse_COLAMD_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_COLAMD_LIBRARY
SuiteSparse_COLAMD_LIBRARY-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_Config_INCLUDE_DIR
SuiteSparse_Config_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_Config_LIBRARY
SuiteSparse_Config_LIBRARY-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_SPQR_INCLUDE_DIR
SuiteSparse_SPQR_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: SuiteSparse_SPQR_LIBRARY
SuiteSparse_SPQR_LIBRARY-ADVANCED:INTERNAL=1
//ADVANCED property for variable: TIFF_INCLUDE_DIR
TIFF_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: TIFF_LIBRARY_DEBUG
TIFF_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: TIFF_LIBRARY_RELEASE
TIFF_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//Install the dependencies listed in your manifest:
//\n    If this is off, you will have to manually install your dependencies.
//\n    See https://github.com/microsoft/vcpkg/tree/master/docs/specifications/manifests.md
// for more info.
//\n
VCPKG_MANIFEST_INSTALL:INTERNAL=OFF
//ADVANCED property for variable: VCPKG_VERBOSE
VCPKG_VERBOSE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: VIDEOIO_ENABLE_PLUGINS
VIDEOIO_ENABLE_PLUGINS-ADVANCED:INTERNAL=1
//ADVANCED property for variable: VIDEOIO_PLUGIN_LIST
VIDEOIO_PLUGIN_LIST-ADVANCED:INTERNAL=1
//ADVANCED property for variable: ZLIB_INCLUDE_DIR
ZLIB_INCLUDE_DIR-ADVANCED:INTERNAL=1
//ADVANCED property for variable: ZLIB_LIBRARY_DEBUG
ZLIB_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: ZLIB_LIBRARY_RELEASE
ZLIB_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//Making sure VCPKG_MANIFEST_MODE doesn't change
Z_VCPKG_CHECK_MANIFEST_MODE:INTERNAL=OFF
//Vcpkg root directory
Z_VCPKG_ROOT_DIR:INTERNAL=/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg
//CMAKE_INSTALL_PREFIX during last run
_GNUInstallDirs_LAST_CMAKE_INSTALL_PREFIX:INTERNAL=/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/packages/opencv4_arm64-osx/debug
__OPENCV_CMAKE_HOOKS_INIT_MODULE_SOURCES_opencv_dnn:INTERNAL=/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/src/4.10.0-e5bca385b2.clean/modules/dnn/cmake/hooks/INIT_MODULE_SOURCES_opencv_dnn.cmake
__OPENCV_EXPORTED_EXTERNAL_TARGETS:INTERNAL=ocv.3rdparty.flatbuffers;ocv.3rdparty.avfoundation
//ADVANCED property for variable: _vcpkg_sharpyuv_LIBRARY_DEBUG
_vcpkg_sharpyuv_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_sharpyuv_LIBRARY_RELEASE
_vcpkg_sharpyuv_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webp_LIBRARY_DEBUG
_vcpkg_webp_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webp_LIBRARY_RELEASE
_vcpkg_webp_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webpdecoder_LIBRARY_DEBUG
_vcpkg_webpdecoder_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webpdecoder_LIBRARY_RELEASE
_vcpkg_webpdecoder_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webpdemux_LIBRARY_DEBUG
_vcpkg_webpdemux_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webpdemux_LIBRARY_RELEASE
_vcpkg_webpdemux_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webpmux_LIBRARY_DEBUG
_vcpkg_webpmux_LIBRARY_DEBUG-ADVANCED:INTERNAL=1
//ADVANCED property for variable: _vcpkg_webpmux_LIBRARY_RELEASE
_vcpkg_webpmux_LIBRARY_RELEASE-ADVANCED:INTERNAL=1
//ADVANCED property for variable: protobuf_VERBOSE
protobuf_VERBOSE-ADVANCED:INTERNAL=1
```
</details>

<details><summary>/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/config-arm64-osx-rel-CMakeConfigureLog.yaml.log</summary>

```

---
events:
  -
    kind: "find-v1"
    backtrace:
      - "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/downloads/tools/cmake-4.3.2-osx/cmake-4.3.2-macos-universal/CMake.app/Contents/share/cmake-4.3/Modules/CMakeDetermineSystem.cmake:12 (find_program)"
      - "CMakeLists.txt:127 (enable_language)"
    mode: "program"
    variable: "CMAKE_UNAME"
    description: "Path to a program."
    settings:
      SearchFramework: "FIRST"
      SearchAppBundle: "FIRST"
      CMAKE_FIND_USE_CMAKE_PATH: true
      CMAKE_FIND_USE_CMAKE_ENVIRONMENT_PATH: true
      CMAKE_FIND_USE_SYSTEM_ENVIRONMENT_PATH: true
      CMAKE_FIND_USE_CMAKE_SYSTEM_PATH: true
      CMAKE_FIND_USE_INSTALL_PREFIX: true
    names:
      - "uname"
    candidate_directories:
      - "/Users/amritladhar/.local/bin/"
      - "/opt/homebrew/opt/node@22/bin/"
      - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/debugCommand/"
      - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/copilotCli/"
      - "/usr/local/bin/"
      - "/System/Cryptexes/App/usr/bin/"
      - "/usr/bin/"
      - "/bin/"
      - "/usr/sbin/"
      - "/sbin/"
      - "/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin/"
      - "/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin/"
      - "/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin/"
      - "/opt/pmk/env/global/bin/"
      - "/Library/Apple/usr/bin/"
      - "/usr/local/share/dotnet/"
      - "/Users/amritladhar/.dotnet/tools/"
      - "/opt/homebrew/bin/"
      - "/Users/amritladhar/.vscode/extensions/ms-python.debugpy-2026.6.0-darwin-arm64/bundled/scripts/noConfigScripts/"
    searched_directories:
      - "/Users/amritladhar/.local/bin/uname"
      - "/opt/homebrew/opt/node@22/bin/uname"
      - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/debugCommand/uname"
      - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/copilotCli/uname"
      - "/usr/local/bin/uname"
      - "/System/Cryptexes/App/usr/bin/uname"
    found: "/usr/bin/uname"
    search_context:
      ENV{PATH}:
        - "/Users/amritladhar/.local/bin"
        - "/opt/homebrew/opt/node@22/bin"
        - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/debugCommand"
        - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/copilotCli"
        - "/opt/homebrew/opt/node@22/bin"
        - "/usr/local/bin"
        - "/System/Cryptexes/App/usr/bin"
        - "/usr/bin"
        - "/bin"
        - "/usr/sbin"
        - "/sbin"
        - "/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin"
        - "/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin"
        - "/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin"
        - "/opt/pmk/env/global/bin"
        - "/Library/Apple/usr/bin"
        - "/usr/local/share/dotnet"
        - "~/.dotnet/tools"
        - "/opt/homebrew/bin"
        - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/debugCommand"
        - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/copilotCli"
        - "/Users/amritladhar/.local/bin"
        - "/opt/homebrew/opt/node@22/bin"
        - "/Users/amritladhar/.vscode/extensions/ms-python.debugpy-2026.6.0-darwin-arm64/bundled/scripts/noConfigScripts"
        - "/opt/homebrew/bin"
      CMAKE_INSTALL_PREFIX: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/packages/opencv4_arm64-osx"
  -
    kind: "message-v1"
    backtrace:
      - "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/downloads/tools/cmake-4.3.2-osx/cmake-4.3.2-macos-universal/CMake.app/Contents/share/cmake-4.3/Modules/CMakeDetermineSystem.cmake:212 (message)"
      - "CMakeLists.txt:127 (enable_language)"
    message: |
      The system is: Darwin - 25.2.0 - arm64
  -
    kind: "find-v1"
    backtrace:
...
Skipped 39226 lines
...
    directories:
      source: "/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/CMakeFiles/CMakeTmp"
      binary: "/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/CMakeFiles/CMakeTmp"
    cmakeVariables:
      CMAKE_CXX_FLAGS: "-fPIC   -fsigned-char -W -Wall -Wreturn-type -Wnon-virtual-dtor -Waddress -Wsequence-point -Wformat -Wformat-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Wno-delete-non-virtual-dtor -Wno-unnamed-type-template-args -Wno-comment -fdiagnostics-show-option -Qunused-arguments -Wno-semicolon-before-method-body -ffunction-sections -fdata-sections    -fvisibility=hidden -fvisibility-inlines-hidden"
      CMAKE_CXX_FLAGS_RELEASE: "-O3 -DNDEBUG  -DNDEBUG -g1"
      CMAKE_CXX_STDLIB_MODULES_JSON: ""
      CMAKE_EXE_LINKER_FLAGS: "  -Wl,-dead_strip"
      CMAKE_OSX_ARCHITECTURES: "arm64"
      CMAKE_OSX_DEPLOYMENT_TARGET: ""
      CMAKE_OSX_SYSROOT: ""
      CMAKE_POSITION_INDEPENDENT_CODE: "ON"
      VCPKG_CHAINLOAD_TOOLCHAIN_FILE: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/scripts/toolchains/osx.cmake"
      VCPKG_CRT_LINKAGE: "dynamic"
      VCPKG_CXX_FLAGS: ""
      VCPKG_CXX_FLAGS_DEBUG: ""
      VCPKG_CXX_FLAGS_RELEASE: ""
      VCPKG_C_FLAGS: ""
      VCPKG_C_FLAGS_DEBUG: ""
      VCPKG_C_FLAGS_RELEASE: ""
      VCPKG_INSTALLED_DIR: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed"
      VCPKG_LINKER_FLAGS: ""
      VCPKG_LINKER_FLAGS_DEBUG: ""
      VCPKG_LINKER_FLAGS_RELEASE: ""
      VCPKG_PREFER_SYSTEM_LIBS: "OFF"
      VCPKG_TARGET_ARCHITECTURE: "arm64"
      VCPKG_TARGET_TRIPLET: "arm64-osx"
      Z_VCPKG_ROOT_DIR: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg"
    buildResult:
      variable: "HAVE_CXX_WNO_OVERLOADED_VIRTUAL"
      cached: true
      stdout: |
        Change Dir: '/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/CMakeFiles/CMakeTmp'
        
        Run Build Command(s): /opt/homebrew/bin/ninja -v cmTC_029da
        [1/2] /usr/bin/c++   -fPIC   -fsigned-char -W -Wall -Wreturn-type -Wnon-virtual-dtor -Waddress -Wsequence-point -Wformat -Wformat-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Wno-delete-non-virtual-dtor -Wno-unnamed-type-template-args -Wno-comment -fdiagnostics-show-option -Qunused-arguments -Wno-semicolon-before-method-body -ffunction-sections -fdata-sections    -fvisibility=hidden -fvisibility-inlines-hidden  -O3 -DNDEBUG  -DNDEBUG -g1 -std=c++17 -arch arm64 -fPIE    -Wno-overloaded-virtual -MD -MT CMakeFiles/cmTC_029da.dir/src.cxx.o -MF CMakeFiles/cmTC_029da.dir/src.cxx.o.d -o CMakeFiles/cmTC_029da.dir/src.cxx.o -c /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/CMakeFiles/CMakeTmp/src.cxx
        /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/CMakeFiles/CMakeTmp/src.cxx:1:8: warning: unknown pragma ignored [-Wunknown-pragmas]
            1 | #pragma
              |        ^
        1 warning generated.
        [2/2] : && /usr/bin/c++ -fPIC   -fsigned-char -W -Wall -Wreturn-type -Wnon-virtual-dtor -Waddress -Wsequence-point -Wformat -Wformat-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Wno-delete-non-virtual-dtor -Wno-unnamed-type-template-args -Wno-comment -fdiagnostics-show-option -Qunused-arguments -Wno-semicolon-before-method-body -ffunction-sections -fdata-sections    -fvisibility=hidden -fvisibility-inlines-hidden  -O3 -DNDEBUG  -DNDEBUG -g1 -arch arm64 -Wl,-search_paths_first -Wl,-headerpad_max_install_names -Wl,-dead_strip CMakeFiles/cmTC_029da.dir/src.cxx.o -o cmTC_029da   && :
        
      exitCode: 0
  -
    kind: "try_compile-v1"
    backtrace:
      - "cmake/OpenCVUtils.cmake:509 (TRY_COMPILE)"
      - "cmake/OpenCVUtils.cmake:581 (ocv_check_compiler_flag)"
      - "cmake/OpenCVUtils.cmake:654 (ocv_check_flag_support)"
      - "/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/src/4.10.0-64012148a7.clean/modules/datasets/CMakeLists.txt:12 (ocv_warnings_disable)"
    directories:
      source: "/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/CMakeFiles/CMakeTmp"
      binary: "/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/CMakeFiles/CMakeTmp"
    cmakeVariables:
      CMAKE_CXX_FLAGS: "-fPIC   -fsigned-char -W -Wall -Wreturn-type -Wnon-virtual-dtor -Waddress -Wsequence-point -Wformat -Wformat-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Wno-delete-non-virtual-dtor -Wno-unnamed-type-template-args -Wno-comment -fdiagnostics-show-option -Qunused-arguments -Wno-semicolon-before-method-body -ffunction-sections -fdata-sections    -fvisibility=hidden -fvisibility-inlines-hidden"
      CMAKE_CXX_FLAGS_RELEASE: "-O3 -DNDEBUG  -DNDEBUG -g1"
      CMAKE_CXX_STDLIB_MODULES_JSON: ""
      CMAKE_EXE_LINKER_FLAGS: "  -Wl,-dead_strip"
      CMAKE_OSX_ARCHITECTURES: "arm64"
      CMAKE_OSX_DEPLOYMENT_TARGET: ""
      CMAKE_OSX_SYSROOT: ""
      CMAKE_POSITION_INDEPENDENT_CODE: "ON"
      VCPKG_CHAINLOAD_TOOLCHAIN_FILE: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/scripts/toolchains/osx.cmake"
      VCPKG_CRT_LINKAGE: "dynamic"
      VCPKG_CXX_FLAGS: ""
      VCPKG_CXX_FLAGS_DEBUG: ""
      VCPKG_CXX_FLAGS_RELEASE: ""
      VCPKG_C_FLAGS: ""
      VCPKG_C_FLAGS_DEBUG: ""
      VCPKG_C_FLAGS_RELEASE: ""
      VCPKG_INSTALLED_DIR: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed"
      VCPKG_LINKER_FLAGS: ""
      VCPKG_LINKER_FLAGS_DEBUG: ""
      VCPKG_LINKER_FLAGS_RELEASE: ""
      VCPKG_PREFER_SYSTEM_LIBS: "OFF"
      VCPKG_TARGET_ARCHITECTURE: "arm64"
      VCPKG_TARGET_TRIPLET: "arm64-osx"
      Z_VCPKG_ROOT_DIR: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg"
    buildResult:
      variable: "HAVE_CXX_WNO_IMPLICIT_FALLTHROUGH"
      cached: true
      stdout: |
        Change Dir: '/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/CMakeFiles/CMakeTmp'
        
        Run Build Command(s): /opt/homebrew/bin/ninja -v cmTC_9e8b8
        [1/2] /usr/bin/c++   -fPIC   -fsigned-char -W -Wall -Wreturn-type -Wnon-virtual-dtor -Waddress -Wsequence-point -Wformat -Wformat-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Wno-delete-non-virtual-dtor -Wno-unnamed-type-template-args -Wno-comment -fdiagnostics-show-option -Qunused-arguments -Wno-semicolon-before-method-body -ffunction-sections -fdata-sections    -fvisibility=hidden -fvisibility-inlines-hidden  -O3 -DNDEBUG  -DNDEBUG -g1 -std=c++17 -arch arm64 -fPIE    -Wno-implicit-fallthrough -MD -MT CMakeFiles/cmTC_9e8b8.dir/src.cxx.o -MF CMakeFiles/cmTC_9e8b8.dir/src.cxx.o.d -o CMakeFiles/cmTC_9e8b8.dir/src.cxx.o -c /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/CMakeFiles/CMakeTmp/src.cxx
        /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-rel/CMakeFiles/CMakeTmp/src.cxx:1:8: warning: unknown pragma ignored [-Wunknown-pragmas]
            1 | #pragma
              |        ^
        1 warning generated.
        [2/2] : && /usr/bin/c++ -fPIC   -fsigned-char -W -Wall -Wreturn-type -Wnon-virtual-dtor -Waddress -Wsequence-point -Wformat -Wformat-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Wno-delete-non-virtual-dtor -Wno-unnamed-type-template-args -Wno-comment -fdiagnostics-show-option -Qunused-arguments -Wno-semicolon-before-method-body -ffunction-sections -fdata-sections    -fvisibility=hidden -fvisibility-inlines-hidden  -O3 -DNDEBUG  -DNDEBUG -g1 -arch arm64 -Wl,-search_paths_first -Wl,-headerpad_max_install_names -Wl,-dead_strip CMakeFiles/cmTC_9e8b8.dir/src.cxx.o -o cmTC_9e8b8   && :
        
      exitCode: 0
...
```
</details>

<details><summary>/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/config-arm64-osx-dbg-CMakeConfigureLog.yaml.log</summary>

```

---
events:
  -
    kind: "find-v1"
    backtrace:
      - "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/downloads/tools/cmake-4.3.2-osx/cmake-4.3.2-macos-universal/CMake.app/Contents/share/cmake-4.3/Modules/CMakeDetermineSystem.cmake:12 (find_program)"
      - "CMakeLists.txt:127 (enable_language)"
    mode: "program"
    variable: "CMAKE_UNAME"
    description: "Path to a program."
    settings:
      SearchFramework: "FIRST"
      SearchAppBundle: "FIRST"
      CMAKE_FIND_USE_CMAKE_PATH: true
      CMAKE_FIND_USE_CMAKE_ENVIRONMENT_PATH: true
      CMAKE_FIND_USE_SYSTEM_ENVIRONMENT_PATH: true
      CMAKE_FIND_USE_CMAKE_SYSTEM_PATH: true
      CMAKE_FIND_USE_INSTALL_PREFIX: true
    names:
      - "uname"
    candidate_directories:
      - "/Users/amritladhar/.local/bin/"
      - "/opt/homebrew/opt/node@22/bin/"
      - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/debugCommand/"
      - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/copilotCli/"
      - "/usr/local/bin/"
      - "/System/Cryptexes/App/usr/bin/"
      - "/usr/bin/"
      - "/bin/"
      - "/usr/sbin/"
      - "/sbin/"
      - "/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin/"
      - "/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin/"
      - "/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin/"
      - "/opt/pmk/env/global/bin/"
      - "/Library/Apple/usr/bin/"
      - "/usr/local/share/dotnet/"
      - "/Users/amritladhar/.dotnet/tools/"
      - "/opt/homebrew/bin/"
      - "/Users/amritladhar/.vscode/extensions/ms-python.debugpy-2026.6.0-darwin-arm64/bundled/scripts/noConfigScripts/"
    searched_directories:
      - "/Users/amritladhar/.local/bin/uname"
      - "/opt/homebrew/opt/node@22/bin/uname"
      - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/debugCommand/uname"
      - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/copilotCli/uname"
      - "/usr/local/bin/uname"
      - "/System/Cryptexes/App/usr/bin/uname"
    found: "/usr/bin/uname"
    search_context:
      ENV{PATH}:
        - "/Users/amritladhar/.local/bin"
        - "/opt/homebrew/opt/node@22/bin"
        - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/debugCommand"
        - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/copilotCli"
        - "/opt/homebrew/opt/node@22/bin"
        - "/usr/local/bin"
        - "/System/Cryptexes/App/usr/bin"
        - "/usr/bin"
        - "/bin"
        - "/usr/sbin"
        - "/sbin"
        - "/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin"
        - "/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin"
        - "/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin"
        - "/opt/pmk/env/global/bin"
        - "/Library/Apple/usr/bin"
        - "/usr/local/share/dotnet"
        - "~/.dotnet/tools"
        - "/opt/homebrew/bin"
        - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/debugCommand"
        - "/Users/amritladhar/Library/Application Support/Code/User/globalStorage/github.copilot-chat/copilotCli"
        - "/Users/amritladhar/.local/bin"
        - "/opt/homebrew/opt/node@22/bin"
        - "/Users/amritladhar/.vscode/extensions/ms-python.debugpy-2026.6.0-darwin-arm64/bundled/scripts/noConfigScripts"
        - "/opt/homebrew/bin"
      CMAKE_INSTALL_PREFIX: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/packages/opencv4_arm64-osx/debug"
  -
    kind: "message-v1"
    backtrace:
...
Skipped 41067 lines
...
      CMAKE_CXX_FLAGS_DEBUG: "-g  -O0 -DDEBUG -D_DEBUG"
      CMAKE_CXX_STDLIB_MODULES_JSON: ""
      CMAKE_EXE_LINKER_FLAGS: "  -Wl,-dead_strip"
      CMAKE_OSX_ARCHITECTURES: "arm64"
      CMAKE_OSX_DEPLOYMENT_TARGET: ""
      CMAKE_OSX_SYSROOT: ""
      CMAKE_POSITION_INDEPENDENT_CODE: "ON"
      VCPKG_CHAINLOAD_TOOLCHAIN_FILE: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/scripts/toolchains/osx.cmake"
      VCPKG_CRT_LINKAGE: "dynamic"
      VCPKG_CXX_FLAGS: ""
      VCPKG_CXX_FLAGS_DEBUG: ""
      VCPKG_CXX_FLAGS_RELEASE: ""
      VCPKG_C_FLAGS: ""
      VCPKG_C_FLAGS_DEBUG: ""
      VCPKG_C_FLAGS_RELEASE: ""
      VCPKG_INSTALLED_DIR: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed"
      VCPKG_LINKER_FLAGS: ""
      VCPKG_LINKER_FLAGS_DEBUG: ""
      VCPKG_LINKER_FLAGS_RELEASE: ""
      VCPKG_PREFER_SYSTEM_LIBS: "OFF"
      VCPKG_TARGET_ARCHITECTURE: "arm64"
      VCPKG_TARGET_TRIPLET: "arm64-osx"
      Z_VCPKG_ROOT_DIR: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg"
    buildResult:
      variable: "HAVE_CXX_WNO_OVERLOADED_VIRTUAL"
      cached: true
      stdout: |
        Change Dir: '/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg/CMakeFiles/CMakeTmp'
        
        Run Build Command(s): /opt/homebrew/bin/ninja -v cmTC_76971
        [1/2] /usr/bin/c++   -fPIC   -fsigned-char -W -Wall -Wreturn-type -Wnon-virtual-dtor -Waddress -Wsequence-point -Wformat -Wformat-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Wno-delete-non-virtual-dtor -Wno-unnamed-type-template-args -Wno-comment -fdiagnostics-show-option -Qunused-arguments -Wno-semicolon-before-method-body -ffunction-sections -fdata-sections    -fvisibility=hidden -fvisibility-inlines-hidden  -g  -O0 -DDEBUG -D_DEBUG -std=c++17 -arch arm64 -fPIE    -Wno-overloaded-virtual -MD -MT CMakeFiles/cmTC_76971.dir/src.cxx.o -MF CMakeFiles/cmTC_76971.dir/src.cxx.o.d -o CMakeFiles/cmTC_76971.dir/src.cxx.o -c /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg/CMakeFiles/CMakeTmp/src.cxx
        /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg/CMakeFiles/CMakeTmp/src.cxx:1:8: warning: unknown pragma ignored [-Wunknown-pragmas]
            1 | #pragma
              |        ^
        1 warning generated.
        [2/2] : && /usr/bin/c++ -fPIC   -fsigned-char -W -Wall -Wreturn-type -Wnon-virtual-dtor -Waddress -Wsequence-point -Wformat -Wformat-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Wno-delete-non-virtual-dtor -Wno-unnamed-type-template-args -Wno-comment -fdiagnostics-show-option -Qunused-arguments -Wno-semicolon-before-method-body -ffunction-sections -fdata-sections    -fvisibility=hidden -fvisibility-inlines-hidden  -g  -O0 -DDEBUG -D_DEBUG -arch arm64 -Wl,-search_paths_first -Wl,-headerpad_max_install_names -Wl,-dead_strip CMakeFiles/cmTC_76971.dir/src.cxx.o -o cmTC_76971   && :
        
      exitCode: 0
  -
    kind: "try_compile-v1"
    backtrace:
      - "cmake/OpenCVUtils.cmake:509 (TRY_COMPILE)"
      - "cmake/OpenCVUtils.cmake:581 (ocv_check_compiler_flag)"
      - "cmake/OpenCVUtils.cmake:654 (ocv_check_flag_support)"
      - "/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/src/4.10.0-64012148a7.clean/modules/datasets/CMakeLists.txt:12 (ocv_warnings_disable)"
    directories:
      source: "/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg/CMakeFiles/CMakeTmp"
      binary: "/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg/CMakeFiles/CMakeTmp"
    cmakeVariables:
      CMAKE_CXX_FLAGS: "-fPIC   -fsigned-char -W -Wall -Wreturn-type -Wnon-virtual-dtor -Waddress -Wsequence-point -Wformat -Wformat-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Wno-delete-non-virtual-dtor -Wno-unnamed-type-template-args -Wno-comment -fdiagnostics-show-option -Qunused-arguments -Wno-semicolon-before-method-body -ffunction-sections -fdata-sections    -fvisibility=hidden -fvisibility-inlines-hidden"
      CMAKE_CXX_FLAGS_DEBUG: "-g  -O0 -DDEBUG -D_DEBUG"
      CMAKE_CXX_STDLIB_MODULES_JSON: ""
      CMAKE_EXE_LINKER_FLAGS: "  -Wl,-dead_strip"
      CMAKE_OSX_ARCHITECTURES: "arm64"
      CMAKE_OSX_DEPLOYMENT_TARGET: ""
      CMAKE_OSX_SYSROOT: ""
      CMAKE_POSITION_INDEPENDENT_CODE: "ON"
      VCPKG_CHAINLOAD_TOOLCHAIN_FILE: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg/scripts/toolchains/osx.cmake"
      VCPKG_CRT_LINKAGE: "dynamic"
      VCPKG_CXX_FLAGS: ""
      VCPKG_CXX_FLAGS_DEBUG: ""
      VCPKG_CXX_FLAGS_RELEASE: ""
      VCPKG_C_FLAGS: ""
      VCPKG_C_FLAGS_DEBUG: ""
      VCPKG_C_FLAGS_RELEASE: ""
      VCPKG_INSTALLED_DIR: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/cvAutoTrack/build-macos/vcpkg_installed"
      VCPKG_LINKER_FLAGS: ""
      VCPKG_LINKER_FLAGS_DEBUG: ""
      VCPKG_LINKER_FLAGS_RELEASE: ""
      VCPKG_PREFER_SYSTEM_LIBS: "OFF"
      VCPKG_TARGET_ARCHITECTURE: "arm64"
      VCPKG_TARGET_TRIPLET: "arm64-osx"
      Z_VCPKG_ROOT_DIR: "/Users/amritladhar/Documents/GitHub/Genshin Live Tracker & Map/external/vcpkg"
    buildResult:
      variable: "HAVE_CXX_WNO_IMPLICIT_FALLTHROUGH"
      cached: true
      stdout: |
        Change Dir: '/private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg/CMakeFiles/CMakeTmp'
        
        Run Build Command(s): /opt/homebrew/bin/ninja -v cmTC_898fe
        [1/2] /usr/bin/c++   -fPIC   -fsigned-char -W -Wall -Wreturn-type -Wnon-virtual-dtor -Waddress -Wsequence-point -Wformat -Wformat-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Wno-delete-non-virtual-dtor -Wno-unnamed-type-template-args -Wno-comment -fdiagnostics-show-option -Qunused-arguments -Wno-semicolon-before-method-body -ffunction-sections -fdata-sections    -fvisibility=hidden -fvisibility-inlines-hidden  -g  -O0 -DDEBUG -D_DEBUG -std=c++17 -arch arm64 -fPIE    -Wno-implicit-fallthrough -MD -MT CMakeFiles/cmTC_898fe.dir/src.cxx.o -MF CMakeFiles/cmTC_898fe.dir/src.cxx.o.d -o CMakeFiles/cmTC_898fe.dir/src.cxx.o -c /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg/CMakeFiles/CMakeTmp/src.cxx
        /private/tmp/genshin-live-tracker-vcpkg/arm64-osx/buildtrees/opencv4/arm64-osx-dbg/CMakeFiles/CMakeTmp/src.cxx:1:8: warning: unknown pragma ignored [-Wunknown-pragmas]
            1 | #pragma
              |        ^
        1 warning generated.
        [2/2] : && /usr/bin/c++ -fPIC   -fsigned-char -W -Wall -Wreturn-type -Wnon-virtual-dtor -Waddress -Wsequence-point -Wformat -Wformat-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Wno-delete-non-virtual-dtor -Wno-unnamed-type-template-args -Wno-comment -fdiagnostics-show-option -Qunused-arguments -Wno-semicolon-before-method-body -ffunction-sections -fdata-sections    -fvisibility=hidden -fvisibility-inlines-hidden  -g  -O0 -DDEBUG -D_DEBUG -arch arm64 -Wl,-search_paths_first -Wl,-headerpad_max_install_names -Wl,-dead_strip CMakeFiles/cmTC_898fe.dir/src.cxx.o -o cmTC_898fe   && :
        
      exitCode: 0
...
```
</details>

**Additional context**

<details><summary>vcpkg.json</summary>

```
{
  "name": "cvautotrack",
  "version": "0.0.1",
  "dependencies": [
    "fmt",
    "cereal",
    "glad",
    "glfw3",
    {
      "name": "imgui",
      "features": [
        "docking-experimental",
        "opengl3-binding"
      ]
    },
    {
      "name": "opencv",
      "features": [
        "contrib",
        "nonfree",
        "opengl"
      ]
    },
    "tracy"
  ],
  "overrides": [
    {
      "name": "fmt",
      "version": "11.0.2#1"
    },
    {
      "name": "glew",
      "version": "2.2.0"
    },
    {
      "name": "glfw3",
      "version": "3.3.8"
    },
    {
      "name": "spdlog",
      "version": "1.15.2"
    },
    {
      "name": "opencv",
      "version": "4.10.0#1"
    },
    {
      "name": "opencv4",
      "version": "4.10.0#1"
    },
    {
      "name": "tbb",
      "version": "2022.1.0#0"
    }
  ],
  "builtin-baseline": "b12aa38a44a29bd8461404f2514e4c7cf00e1fc5"
}

```
</details>
