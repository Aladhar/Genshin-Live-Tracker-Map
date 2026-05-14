#pragma once

#include <cstdint>
#include <string>
#include <vector>

#include <opencv2/core.hpp>

namespace tianli::frame::capture::macos
{
    struct window_info
    {
        uint32_t window_id = 0;
        int owner_pid = 0;
        std::string owner_name;
        std::string title;
        cv::Rect bounds;
        double scale = 1.0;
        bool on_screen = false;
    };

    std::vector<window_info> list_windows();
    bool find_genshin_window(window_info& window);
    bool query_window(uint32_t window_id, window_info& window);

    bool has_screen_capture_permission();
    bool request_screen_capture_permission();

    bool capture_window(uint32_t window_id, cv::Mat& frame);
    bool capture_main_display(cv::Mat& frame);
} // namespace tianli::frame::capture::macos
