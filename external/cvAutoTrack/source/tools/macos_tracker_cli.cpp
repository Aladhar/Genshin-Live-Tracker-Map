#include "cvAutoTrack.h"
#include "frame/capture/capture.macos_bridge.h"

#include <chrono>
#include <filesystem>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#ifdef __APPLE__
#include <mach-o/dyld.h>
#endif

#include <opencv2/imgcodecs.hpp>

namespace
{
    namespace fs = std::filesystem;

    struct options
    {
        bool help = false;
        bool list = false;
        bool status = false;
        bool request_permission = false;
        bool capture = false;
        bool once = false;
        bool run = false;
        uint32_t window_id = 0;
        int interval_ms = 1000;
        int iterations = 0;
        fs::path output_path = "Capture-macos.png";
        fs::path cache_path;
    };

    bool starts_with_dash(const std::string& value)
    {
        return !value.empty() && value[0] == '-';
    }

    bool parse_uint32(const std::string& value, uint32_t& result)
    {
        try
        {
            size_t consumed = 0;
            const auto parsed = std::stoul(value, &consumed, 10);
            if (consumed != value.size())
                return false;
            result = static_cast<uint32_t>(parsed);
            return true;
        }
        catch (...)
        {
            return false;
        }
    }

    bool parse_int(const std::string& value, int& result)
    {
        try
        {
            size_t consumed = 0;
            const auto parsed = std::stoi(value, &consumed, 10);
            if (consumed != value.size())
                return false;
            result = parsed;
            return true;
        }
        catch (...)
        {
            return false;
        }
    }

    void print_usage(const char* executable)
    {
        std::cout
            << "Genshin macOS tracker CLI\n\n"
            << "Usage:\n"
            << "  " << executable << " --status\n"
            << "  " << executable << " --list\n"
            << "  " << executable << " --request-permission\n"
            << "  " << executable << " --capture [path]\n"
            << "  " << executable << " --once --cache /path/to/cvAutoTrack_Cache.dat\n"
            << "  " << executable << " --run --cache /path/to/cvAutoTrack_Cache.dat\n\n"
            << "Options:\n"
            << "  --window-id <id>       Use a specific Core Graphics window id.\n"
            << "  --cache <path>         Use a specific cvAutoTrack_Cache.dat file.\n"
            << "  --output <path>        Output path for --capture.\n"
            << "  --interval-ms <ms>     Poll interval for --run. Default: 1000.\n"
            << "  --iterations <count>   Number of --run samples. Default: unlimited.\n";
    }

    bool parse_options(int argc, char* argv[], options& opts)
    {
        for (int i = 1; i < argc; ++i)
        {
            const std::string arg = argv[i];
            if (arg == "--help" || arg == "-h")
                opts.help = true;
            else if (arg == "--list")
                opts.list = true;
            else if (arg == "--status")
                opts.status = true;
            else if (arg == "--request-permission")
                opts.request_permission = true;
            else if (arg == "--capture")
            {
                opts.capture = true;
                if (i + 1 < argc && !starts_with_dash(argv[i + 1]))
                    opts.output_path = argv[++i];
            }
            else if (arg == "--once")
                opts.once = true;
            else if (arg == "--run")
                opts.run = true;
            else if (arg == "--window-id" && i + 1 < argc)
            {
                if (!parse_uint32(argv[++i], opts.window_id))
                    return false;
            }
            else if (arg == "--cache" && i + 1 < argc)
                opts.cache_path = argv[++i];
            else if (arg == "--output" && i + 1 < argc)
                opts.output_path = argv[++i];
            else if (arg == "--interval-ms" && i + 1 < argc)
            {
                if (!parse_int(argv[++i], opts.interval_ms) || opts.interval_ms < 100)
                    return false;
            }
            else if (arg == "--iterations" && i + 1 < argc)
            {
                if (!parse_int(argv[++i], opts.iterations) || opts.iterations < 0)
                    return false;
            }
            else
            {
                std::cerr << "Unknown or incomplete argument: " << arg << "\n";
                return false;
            }
        }

        if (!opts.help && !opts.list && !opts.status && !opts.request_permission && !opts.capture && !opts.once && !opts.run)
            opts.status = true;

        return true;
    }

    fs::path executable_dir(char* argv0)
    {
#ifdef __APPLE__
        uint32_t size = 0;
        _NSGetExecutablePath(nullptr, &size);
        std::string buffer(size, '\0');
        if (_NSGetExecutablePath(buffer.data(), &size) == 0)
            return fs::weakly_canonical(fs::path(buffer.c_str())).parent_path();
#endif
        return fs::weakly_canonical(fs::path(argv0)).parent_path();
    }

    std::optional<fs::path> find_cache_path(const options& opts, const fs::path& exe_dir)
    {
        if (!opts.cache_path.empty())
            return opts.cache_path;

        const std::vector<fs::path> candidates = {
            fs::current_path() / "cvAutoTrack_Cache.dat",
            exe_dir / "cvAutoTrack_Cache.dat",
            exe_dir / "resource" / "cvAutoTrack_Cache.dat",
            exe_dir.parent_path() / "resource" / "cvAutoTrack_Cache.dat",
        };

        for (const auto& candidate : candidates)
        {
            if (fs::exists(candidate))
                return candidate;
        }
        return std::nullopt;
    }

    std::string last_error_json()
    {
        char buffer[4096] = {};
        if (GetLastErrJson(buffer, static_cast<int>(sizeof(buffer))))
            return buffer;
        return "{\"code\":0,\"msg\":\"No tracker error message available\"}";
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

    bool select_window(const options& opts, tianli::frame::capture::macos::window_info& window)
    {
        using namespace tianli::frame::capture::macos;

        if (opts.window_id != 0)
        {
            if (query_window(opts.window_id, window))
                return true;
            window.window_id = opts.window_id;
            return true;
        }

        return find_genshin_window(window);
    }

    int run_capture(const options& opts)
    {
        using namespace tianli::frame::capture::macos;

        window_info window;
        if (!select_window(opts, window))
        {
            std::cerr << "No Genshin window found. Start Genshin and keep the game window visible.\n";
            return 2;
        }

        if (!has_screen_capture_permission())
        {
            std::cerr << "Screen Recording permission is missing for this terminal/app.\n";
            std::cerr << "Run with --request-permission, then enable it in System Settings and restart the terminal/app.\n";
            return 3;
        }

        cv::Mat frame;
        if (!capture_window(window.window_id, frame) || frame.empty())
        {
            std::cerr << "Failed to capture window " << window.window_id << ".\n";
            return 4;
        }

        if (!cv::imwrite(opts.output_path.string(), frame))
        {
            std::cerr << "Failed to write " << opts.output_path << ".\n";
            return 5;
        }

        std::cout << "Captured " << frame.cols << "x" << frame.rows << " to " << opts.output_path << "\n";
        return 0;
    }

    bool prepare_tracker(const options& opts, const fs::path& exe_dir, tianli::frame::capture::macos::window_info& window)
    {
        using namespace tianli::frame::capture::macos;

        if (!select_window(opts, window))
        {
            std::cerr << "No Genshin window found. Start Genshin and keep the game window visible.\n";
            return false;
        }

        if (!has_screen_capture_permission())
        {
            std::cerr << "Screen Recording permission is missing for this terminal/app.\n";
            std::cerr << "Run with --request-permission, then enable it in System Settings and restart the terminal/app.\n";
            return false;
        }

        const auto cache_path = find_cache_path(opts, exe_dir);
        if (!cache_path || !fs::exists(*cache_path))
        {
            std::cerr << "Missing cvAutoTrack_Cache.dat. Pass it with --cache /path/to/cvAutoTrack_Cache.dat.\n";
            return false;
        }

        SetCoreCachePath(cache_path->string().c_str());

        if (!InitResource())
        {
            std::cerr << "InitResource failed: " << last_error_json() << "\n";
            return false;
        }

        if (!SetUseGraphicsCaptureMode())
        {
            std::cerr << "Could not enable macOS graphics capture mode: " << last_error_json() << "\n";
            return false;
        }

        if (!SetCaptureHandle(static_cast<long long>(window.window_id)))
        {
            std::cerr << "Could not select window " << window.window_id << ": " << last_error_json() << "\n";
            return false;
        }

        std::cout << "Tracking window: ";
        print_window(window);
        std::cout << "Cache: " << *cache_path << "\n";
        return true;
    }

    int run_tracker(const options& opts, const fs::path& exe_dir)
    {
        tianli::frame::capture::macos::window_info window;
        if (!prepare_tracker(opts, exe_dir, window))
            return 6;

        int sample = 0;
        while (opts.once || opts.iterations == 0 || sample < opts.iterations)
        {
            double x = 0.0;
            double y = 0.0;
            int map_id = 0;
            double direction = 0.0;
            double rotation = 0.0;
            int uid = 0;

            if (GetAllInfo(x, y, map_id, direction, rotation, uid))
            {
                std::cout
                    << "{\"ok\":true,"
                    << "\"x\":" << x << ","
                    << "\"y\":" << y << ","
                    << "\"mapId\":" << map_id << ","
                    << "\"direction\":" << direction << ","
                    << "\"rotation\":" << rotation << ","
                    << "\"uid\":" << uid << "}\n";
            }
            else
            {
                std::cerr << "{\"ok\":false,\"error\":" << last_error_json() << "}\n";
                if (opts.once)
                    break;
            }

            ++sample;
            if (opts.once)
                break;
            std::this_thread::sleep_for(std::chrono::milliseconds(opts.interval_ms));
        }

        UnInitResource();
        return 0;
    }

    int print_status(const options& opts, const fs::path& exe_dir)
    {
        using namespace tianli::frame::capture::macos;

        char version[128] = {};
        char build_time[128] = {};
        GetCompileVersion(version, static_cast<int>(sizeof(version)));
        GetCompileTime(build_time, static_cast<int>(sizeof(build_time)));

        std::cout << "Executable dir: " << exe_dir << "\n";
        std::cout << "cvAutoTrack version: " << version << "\n";
        std::cout << "cvAutoTrack build time: " << build_time << "\n";
        std::cout << "Screen Recording permission: " << (has_screen_capture_permission() ? "granted" : "missing") << "\n";

        const auto cache_path = find_cache_path(opts, exe_dir);
        if (cache_path && fs::exists(*cache_path))
            std::cout << "Tracker cache: " << *cache_path << "\n";
        else if (cache_path)
            std::cout << "Tracker cache: missing at " << *cache_path << "\n";
        else
            std::cout << "Tracker cache: missing, pass --cache /path/to/cvAutoTrack_Cache.dat\n";

        window_info window;
        if (select_window(opts, window))
        {
            std::cout << "Genshin window: ";
            print_window(window);
        }
        else
        {
            std::cout << "Genshin window: not found\n";
        }

        return 0;
    }
}

int main(int argc, char* argv[])
{
    options opts;
    if (!parse_options(argc, argv, opts))
    {
        print_usage(argv[0]);
        return 2;
    }

    if (opts.help)
    {
        print_usage(argv[0]);
        return 0;
    }

    const auto exe_dir = executable_dir(argv[0]);

    if (opts.request_permission)
    {
        std::cout << "Requesting Screen Recording permission...\n";
        const bool granted = tianli::frame::capture::macos::request_screen_capture_permission();
        std::cout << (granted ? "Permission already granted or approved.\n" : "Permission not granted yet. Enable it in System Settings, then restart this terminal/app.\n");
        if (!opts.list && !opts.status && !opts.capture && !opts.once && !opts.run)
            return granted ? 0 : 3;
    }

    if (opts.list)
    {
        for (const auto& window : tianli::frame::capture::macos::list_windows())
            print_window(window);
    }

    if (opts.status)
        return print_status(opts, exe_dir);

    if (opts.capture)
        return run_capture(opts);

    if (opts.once || opts.run)
        return run_tracker(opts, exe_dir);

    return 0;
}
