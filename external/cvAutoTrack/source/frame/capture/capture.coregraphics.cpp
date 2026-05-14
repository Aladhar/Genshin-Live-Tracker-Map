#include "capture.coregraphics.h"
#include "capture.macos_bridge.h"

namespace tianli::frame::capture
{
    capture_core_graphics::capture_core_graphics(std::shared_ptr<global::logger> logger) : capture_source(logger)
    {
        this->type = source_type::window_graphics;
    }

    capture_core_graphics::~capture_core_graphics()
    {
        uninitialized();
    }

    bool capture_core_graphics::initialization()
    {
#ifdef __APPLE__
        this->is_initialized = true;
        return true;
#else
        return false;
#endif
    }

    bool capture_core_graphics::uninitialized()
    {
        this->source_frame.release();
        this->is_initialized = false;
        return true;
    }

    bool capture_core_graphics::set_capture_handle(HWND handle)
    {
        this->source_handle = handle;
        this->is_callback = false;
        return initialization();
    }

    bool capture_core_graphics::set_source_handle_callback(std::function<HWND()> callback)
    {
        if (callback == nullptr)
            return false;
        this->source_handle_callback = callback;
        this->is_callback = true;
        return initialization();
    }

    bool capture_core_graphics::set_frame_rect_callback(std::function<cv::Rect(cv::Rect)> callback)
    {
        if (callback == nullptr)
            return false;
        this->frame_rect_callback = callback;
        this->has_frame_rect_callback = true;
        return true;
    }

    bool capture_core_graphics::get_frame(cv::Mat& frame)
    {
        if (!this->is_initialized && !initialization())
            return false;
        return capture_frame_internal(frame);
    }

	bool capture_core_graphics::capture_frame_internal(cv::Mat& frame)
	{
#ifdef __APPLE__
        if (this->is_callback)
            set_capture_handle(this->source_handle_callback());

        const auto window_id = static_cast<uint32_t>(reinterpret_cast<uintptr_t>(this->source_handle));
        bool captured = false;
        if (window_id != 0)
            captured = macos::capture_window(window_id, this->source_frame);
        else
            captured = macos::capture_main_display(this->source_frame);

        if (!captured || this->source_frame.empty())
            return false;

        if (this->has_frame_rect_callback)
        {
            cv::Rect rect = this->frame_rect_callback(cv::Rect(0, 0, this->source_frame.cols, this->source_frame.rows));
            rect &= cv::Rect(0, 0, this->source_frame.cols, this->source_frame.rows);
            if (rect.empty())
                return false;
            frame = this->source_frame(rect).clone();
        }
        else
        {
            frame = this->source_frame.clone();
        }
        return true;
#else
        (void)frame;
        return false;
#endif
    }
} // namespace tianli::frame::capture
