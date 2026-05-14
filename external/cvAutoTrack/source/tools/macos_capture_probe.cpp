#include "frame/capture/capture.macos_bridge.h"

#include <iostream>
#include <string>

#include <opencv2/imgcodecs.hpp>

namespace
{
    bool has_arg(int argc, char* argv[], const std::string& name)
    {
        for (int i = 1; i < argc; ++i)
        {
            if (argv[i] == name)
                return true;
        }
        return false;
    }

    std::string value_after_arg(int argc, char* argv[], const std::string& name, const std::string& fallback)
    {
        for (int i = 1; i + 1 < argc; ++i)
        {
            if (argv[i] == name)
                return argv[i + 1];
        }
        return fallback;
    }

    void print_window(const tianli::frame::capture::macos::window_info& window)
    {
        std::cout
            << window.window_id << " | "
            << window.owner_name << " | "
            << window.title << " | "
            << window.bounds.x << "," << window.bounds.y << " "
            << window.bounds.width << "x" << window.bounds.height << "\n";
    }
}

int main(int argc, char* argv[])
{
    using namespace tianli::frame::capture::macos;

    if (has_arg(argc, argv, "--request-permission"))
    {
        std::cout << "Requesting Screen Recording permission...\n";
        std::cout << (request_screen_capture_permission() ? "Permission already granted or approved.\n" : "Permission not granted yet.\n");
    }

    if (has_arg(argc, argv, "--list"))
    {
        for (const auto& window : list_windows())
            print_window(window);
        return 0;
    }

    window_info window;
    if (!find_genshin_window(window))
    {
        std::cerr << "No Genshin window found. Start Genshin, keep its window visible, then rerun this probe.\n";
        return 2;
    }

    std::cout << "Found Genshin candidate:\n";
    print_window(window);

    if (!has_screen_capture_permission())
    {
        std::cerr << "Screen Recording permission is not granted for this terminal/app.\n";
        std::cerr << "Run again with --request-permission or enable it in System Settings > Privacy & Security > Screen & System Audio Recording.\n";
        return 3;
    }

    cv::Mat frame;
    if (!capture_window(window.window_id, frame) || frame.empty())
    {
        std::cerr << "Failed to capture the Genshin window.\n";
        return 4;
    }

    const auto output_path = value_after_arg(argc, argv, "--output", "Capture-macos.png");
    if (!cv::imwrite(output_path, frame))
    {
        std::cerr << "Failed to write " << output_path << "\n";
        return 5;
    }

    std::cout << "Captured " << frame.cols << "x" << frame.rows << " to " << output_path << "\n";
    return 0;
}
