add_library(tianli_frame STATIC)
add_library(tianli::frame ALIAS tianli_frame)

target_sources(tianli_frame
    PUBLIC
        frame.include.h
    PRIVATE
        frame.include.cpp
        capture/capture.include.h

        local/local.include.h
        local/local.picture.h
        local/local.video.h
        
        )

if(WIN32)
    target_sources(tianli_frame
        PRIVATE
            capture/capture.bitblt.h
            capture/capture.window_graphics.h
            capture/capture.window_graphics.cpp
    )
elseif(APPLE)
    target_sources(tianli_frame
        PRIVATE
            capture/capture.coregraphics.h
            capture/capture.coregraphics.cpp
            capture/capture.macos_bridge.h
            capture/capture.macos_bridge.mm
    )
    set_source_files_properties(capture/capture.macos_bridge.mm PROPERTIES COMPILE_FLAGS "-fobjc-arc")
endif()

set_target_properties(tianli_frame PROPERTIES FOLDER "cvAutoTrack/modules")

find_package(OpenCV REQUIRED)
target_link_libraries(tianli_frame
    PUBLIC
        ${OpenCV_LIBS})
if(WIN32)
    target_link_libraries(tianli_frame
        PUBLIC
            d3d11.lib
            d3dcompiler.lib
            dxgi.lib)
elseif(APPLE)
    target_link_libraries(tianli_frame
        PUBLIC
            "-framework CoreGraphics"
            "-framework CoreFoundation"
            "-framework ApplicationServices"
            "-framework Foundation"
            "-framework AppKit"
            "-framework ScreenCaptureKit"
            "-framework CoreMedia"
            "-framework CoreVideo")
endif()
target_include_directories(tianli_frame
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:include>
        ${OpenCV_INCLUDE_DIRS}
)
