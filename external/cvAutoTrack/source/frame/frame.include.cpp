#include "frame.include.h"
#ifdef _WIN32
    #include "capture/capture.bitblt.h"
    #include "capture/capture.window_graphics.h"
#elif defined(__APPLE__)
    #include "capture/capture.coregraphics.h"
#endif
#include "local/local.picture.h"
#include "local/local.video.h"

namespace tianli::frame
{
    std::shared_ptr<frame_source> frame_source:: create(source_type type, std::shared_ptr<global::logger> logger)
    {
        switch (type)
        {
        case source_type::bitblt:
#ifdef _WIN32
            return std::make_shared<capture::capture_bitblt>(logger);
#else
            return nullptr;
#endif
        case source_type::window_graphics:
#ifdef _WIN32
            return std::make_shared<capture::capture_window_graphics>(logger);
#elif defined(__APPLE__)
            return std::make_shared<capture::capture_core_graphics>(logger);
#else
            return nullptr;
#endif
        case source_type::video:
            return std::make_shared<local::local_video>(logger);
        case source_type::picture: 
            return std::make_shared<local::local_picture>(logger);
        default:
            return nullptr;
        }
    }
} // namespace tianli::frame
