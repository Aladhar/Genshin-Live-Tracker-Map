#pragma once

#include "capture.include.h"

namespace tianli::frame::capture {

    /// @brief Captures frames from the macOS display using Core Graphics
    /// @note This is the macOS equivalent of DXGI capture on Windows
    class capture_core_graphics : public capture_source {
    public:
        capture_core_graphics(std::shared_ptr<global::logger> logger = nullptr);
        ~capture_core_graphics() override;

        bool initialization() override;
        bool uninitialized() override;
        bool get_frame(cv::Mat& frame) override;

        bool set_capture_handle(HWND handle = nullptr) override;
        bool set_source_handle_callback(std::function<HWND()> callback) override;
        bool set_frame_rect_callback(std::function<cv::Rect(cv::Rect)> callback) override;

    private:
        bool capture_frame_internal(cv::Mat& frame);
    };

} // namespace tianli::frame::capture
