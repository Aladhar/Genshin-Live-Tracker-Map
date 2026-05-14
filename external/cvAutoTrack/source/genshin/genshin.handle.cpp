#include "pch.h"
#include "genshin.handle.h"
#include "genshin.include.h"
#include <cwctype>
#ifdef _WIN32
    #include <TlHelp32.h>
#elif defined(__APPLE__)
    #include "frame/capture/capture.macos_bridge.h"
    #include <cstdint>
#endif

namespace TianLi::Genshin
{
#ifdef _WIN32
    namespace
    {
        std::wstring lower_copy(std::wstring text)
        {
            std::transform(text.begin(), text.end(), text.begin(), [](wchar_t ch) { return static_cast<wchar_t>(std::towlower(ch)); });
            return text;
        }

        std::wstring base_name(std::wstring path)
        {
            const auto index = path.find_last_of(L"\\/");
            if (index != std::wstring::npos)
                path.erase(0, index + 1);
            return lower_copy(path);
        }

        bool is_genshin_process_name(const std::wstring& exe_name)
        {
            const auto name = base_name(exe_name);
            return name == L"genshinimpact.exe" || name == L"yuanshen.exe" || name == L"yuanshengame.exe";
        }

        std::vector<DWORD> get_genshin_process_ids()
        {
            std::vector<DWORD> process_ids;
            HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
            if (snapshot == INVALID_HANDLE_VALUE)
                return process_ids;

            PROCESSENTRY32W process_entry{};
            process_entry.dwSize = sizeof(process_entry);
            if (Process32FirstW(snapshot, &process_entry))
            {
                do
                {
                    if (is_genshin_process_name(process_entry.szExeFile))
                        process_ids.push_back(process_entry.th32ProcessID);
                } while (Process32NextW(snapshot, &process_entry));
            }
            CloseHandle(snapshot);
            return process_ids;
        }

        struct window_search_context
        {
            const std::vector<DWORD>* process_ids = nullptr;
            HWND window = nullptr;
        };

        HWND find_genshin_window_by_process()
        {
            auto process_ids = get_genshin_process_ids();
            if (process_ids.empty())
                return nullptr;

            window_search_context context{ &process_ids, nullptr };
            EnumWindows(
                [](HWND hwnd, LPARAM lParam) -> BOOL {
                    auto context = reinterpret_cast<window_search_context*>(lParam);
                    if (context == nullptr || context->process_ids == nullptr)
                        return TRUE;

                    DWORD process_id = 0;
                    GetWindowThreadProcessId(hwnd, &process_id);
                    if (std::find(context->process_ids->begin(), context->process_ids->end(), process_id) == context->process_ids->end())
                        return TRUE;

                    wchar_t class_name[256]{};
                    GetClassNameW(hwnd, class_name, static_cast<int>(sizeof(class_name) / sizeof(class_name[0])));
                    if (std::wstring(class_name) != L"UnityWndClass")
                        return TRUE;

                    if (!IsWindowVisible(hwnd))
                        return TRUE;

                    context->window = hwnd;
                    return FALSE;
                },
                reinterpret_cast<LPARAM>(&context));
            return context.window;
        }

        cv::Rect make_relative_rect(const cv::Size& size, double left, double top, double width, double height)
        {
            return {
                static_cast<int>(size.width * left),
                static_cast<int>(size.height * top),
                static_cast<int>(size.width * width),
                static_cast<int>(size.height * height),
            };
        }
    } // namespace

    tianli::global::GenshinHandle func_get_handle(HWND& in)
    {
        static tianli::global::GenshinHandle out;
        if (in == 0)
        {
            get_genshin_handle(out);
        }
        else
        {
            update_genshin_handle(in, out);
        }
        return out;
    }

    HWND get_cloud_window()
    {
        HWND cloud_window = NULL;
        EnumWindows(
            [](HWND hwnd, LPARAM lParam) -> BOOL {
                auto cloud_window = reinterpret_cast<HWND*>(lParam);
                wchar_t buffer[1024];
                auto style = GetWindowLongPtr(hwnd, GWL_STYLE);
                GetWindowTextW(hwnd, buffer, 1024);
                if (std::wstring(buffer) == L"云·原神" && (style & WS_EX_LAYERED))
                {
                    *cloud_window = hwnd;
                    return FALSE;
                }
                return TRUE;
            },
            reinterpret_cast<LPARAM>(&cloud_window));
        return cloud_window;
    }

    void get_genshin_handle(tianli::global::GenshinHandle& genshin_handle)
    {
        if (genshin_handle.config.is_auto_find_genshin)
        {
            auto& giHandle = genshin_handle.handle;

            auto now_class = tianli::global::GenshinWindowClass::Unity;
            for (auto& [genshin_window_name, genshin_window_class] : genshin_handle.config.genshin_window_name_list)
            {
                if (genshin_window_class == tianli::global::GenshinWindowClass::Unity)
                {
                    giHandle = FindWindowW(L"UnityWndClass", genshin_window_name.c_str());
                }
                else
                {
                    giHandle = FindWindowW(nullptr, genshin_window_name.c_str());
                }
                if (genshin_window_name == L"云·原神" && giHandle == NULL)
                {
                    giHandle = get_cloud_window();
                }

                if (giHandle)
                {
                    now_class = genshin_window_class;
                    break;
                }
            }

            if (giHandle == nullptr)
            {
                giHandle = find_genshin_window_by_process();
                if (giHandle != nullptr)
                    now_class = tianli::global::GenshinWindowClass::Unity;
            }

            if (now_class == tianli::global::GenshinWindowClass::None)
            {
                genshin_handle.config.is_force_used_no_alpha = true;
            }
            else
            {
                genshin_handle.config.is_force_used_no_alpha = false;
            }
        }
        else
        {
            genshin_handle.handle = genshin_handle.config.genshin_handle;
        }
        if (genshin_handle.handle != 0)
        {
            genshin_handle.is_exist = true;
        }
        else
        {
            genshin_handle.is_exist = false;
            return;
        }
        // 判断窗口是否存在标题栏
        if (GetWindowLong(genshin_handle.handle, GWL_STYLE) & WS_CAPTION)
        {
            genshin_handle.is_exist_title_bar = true;
        }
        else
        {
            genshin_handle.is_exist_title_bar = false;
        }
        // 获取窗口大小
        GetWindowRect(genshin_handle.handle, &genshin_handle.rect);
        // 获取除标题栏区域大小
        GetClientRect(genshin_handle.handle, &genshin_handle.rect_client);
        // 获取缩放比例
        HMONITOR hMonitor = MonitorFromWindow(genshin_handle.handle, MONITOR_DEFAULTTONEAREST);
        UINT dpiX, dpiY;
        GetDpiForMonitor(hMonitor, MDT_EFFECTIVE_DPI, &dpiX, &dpiY);
        genshin_handle.scale = dpiX / 96.0;

        GetUiRects(genshin_handle);
    }

    // TODO: 需要将获取UI布局的方法分离出来
    void GetUiRects(tianli::global::GenshinHandle& genshin_handle)
    {
        int x = genshin_handle.rect_client.right - genshin_handle.rect_client.left;
        int y = genshin_handle.rect_client.bottom - genshin_handle.rect_client.top;

        double f = 1, fx = 1, fy = 1;

        if (static_cast<double>(x) / static_cast<double>(y) == 16.0 / 9.0)
        {
            genshin_handle.size_frame = cv::Size(1920, 1080);
        }
        else if (static_cast<double>(x) / static_cast<double>(y) > 16.0 / 9.0)
        {

            // 高型，以宽为比例

            // x = (y * 16) / 9;
            f = y / 1080.0;
            // 将giFrame缩放到1920*1080的比例
            fx = x / f;
            // 将图片缩放
            genshin_handle.size_frame = cv::Size(static_cast<int>(fx), 1080);
        }
        else if (static_cast<double>(x) / static_cast<double>(y) < 16.0 / 9.0)
        {

            // 宽型，以高为比例

            // x = (y * 16) / 9;
            f = x / 1920.0;
            // 将giFrame缩放到1920*1080的比例
            fy = y / f;
            // 将图片缩放
            genshin_handle.size_frame = cv::Size(1920, static_cast<int>(fy));
        }
        x = genshin_handle.size_frame.width;
        y = genshin_handle.size_frame.height;
        const cv::Size frame_size(x, y);
        genshin_handle.rect_paimon_maybe = make_relative_rect(frame_size, 0.00, 0.00, 0.10, 0.10);
        genshin_handle.rect_minimap_cailb_maybe = make_relative_rect(frame_size, 0.08, 0.00, 0.10, 0.10);
        genshin_handle.rect_minimap_maybe = make_relative_rect(frame_size, 0.00, 0.00, 0.18, 0.22);
        genshin_handle.rect_uid_maybe = make_relative_rect(frame_size, 0.88, 0.97, 0.12, 0.03);

        int UID_Rect_x = cvCeil(x - x * (1.0 - 0.865));
        int UID_Rect_y = cvCeil(y - 1080.0 * (1.0 - 0.9755));
        int UID_Rect_w = cvCeil(1920 * 0.11);
        int UID_Rect_h = cvCeil(1920 * 0.0938 * 0.11);
        genshin_handle.rect_uid = cv::Rect(UID_Rect_x, UID_Rect_y, UID_Rect_w, UID_Rect_h);
        genshin_handle.rect_left_give_items_maybe = make_relative_rect(frame_size, 0.570, 0.250, 0.225, 0.500);
        genshin_handle.rect_left_give_items = genshin_handle.rect_left_give_items_maybe;
        genshin_handle.rect_right_pick_items_maybe = make_relative_rect(frame_size, 0.050, 0.460, 0.160, 0.480);
        genshin_handle.rect_right_pick_items = genshin_handle.rect_right_pick_items_maybe;
    }

    void update_genshin_handle(const HWND& old_handle, tianli::global::GenshinHandle& out_genshin_handle)
    {
        static unsigned char tick_count = 0;
        if (IsWindowVisible(old_handle))
        {
            if (tick_count < 30)
            {
                tick_count++;
            }
            else
            {
                tick_count = 0;
                get_genshin_handle(out_genshin_handle);
            }
        }
        else
        {
            get_genshin_handle(out_genshin_handle);
        }
        return;
    }

#elif defined(__APPLE__)
    namespace
    {
        cv::Rect make_relative_rect_macos(const cv::Size& size, double left, double top, double width, double height)
        {
            return {
                static_cast<int>(size.width * left),
                static_cast<int>(size.height * top),
                static_cast<int>(size.width * width),
                static_cast<int>(size.height * height),
            };
        }

        uint32_t window_id_from_handle(HWND handle)
        {
            return static_cast<uint32_t>(reinterpret_cast<uintptr_t>(handle));
        }

        HWND handle_from_window_id(uint32_t window_id)
        {
            return reinterpret_cast<HWND>(static_cast<uintptr_t>(window_id));
        }

        void apply_window_info(const tianli::frame::capture::macos::window_info& window, tianli::global::GenshinHandle& genshin_handle)
        {
            genshin_handle.handle = handle_from_window_id(window.window_id);
            genshin_handle.is_exist = window.window_id != 0;
            genshin_handle.scale = window.scale;
            genshin_handle.is_exist_title_bar = false;
            genshin_handle.config.is_force_used_no_alpha = true;

            genshin_handle.rect = {
                window.bounds.x,
                window.bounds.y,
                window.bounds.x + window.bounds.width,
                window.bounds.y + window.bounds.height,
            };
            genshin_handle.rect_client = {
                0,
                0,
                window.bounds.width,
                window.bounds.height,
            };

            GetUiRects(genshin_handle);
        }
    } // namespace

    tianli::global::GenshinHandle func_get_handle(HWND& in)
    {
        static tianli::global::GenshinHandle out;
        if (in == nullptr)
            get_genshin_handle(out);
        else
            update_genshin_handle(in, out);
        return out;
    }

    HWND get_cloud_window()
    {
        return nullptr;
    }

    void get_genshin_handle(tianli::global::GenshinHandle& genshin_handle)
    {
        tianli::frame::capture::macos::window_info window;
        if (genshin_handle.config.is_auto_find_genshin)
        {
            if (!tianli::frame::capture::macos::find_genshin_window(window))
            {
                genshin_handle.handle = nullptr;
                genshin_handle.is_exist = false;
                return;
            }
        }
        else
        {
            HWND configured_handle = genshin_handle.config.genshin_handle != nullptr ? genshin_handle.config.genshin_handle : genshin_handle.handle;
            if (configured_handle == nullptr || !tianli::frame::capture::macos::query_window(window_id_from_handle(configured_handle), window))
            {
                genshin_handle.handle = nullptr;
                genshin_handle.is_exist = false;
                return;
            }
        }

        apply_window_info(window, genshin_handle);
    }

    void GetUiRects(tianli::global::GenshinHandle& genshin_handle)
    {
        int x = genshin_handle.rect_client.right - genshin_handle.rect_client.left;
        int y = genshin_handle.rect_client.bottom - genshin_handle.rect_client.top;
        if (x <= 0 || y <= 0)
        {
            x = 1920;
            y = 1080;
        }

        double f = 1, fx = 1, fy = 1;
        if (static_cast<double>(x) / static_cast<double>(y) == 16.0 / 9.0)
        {
            genshin_handle.size_frame = cv::Size(1920, 1080);
        }
        else if (static_cast<double>(x) / static_cast<double>(y) > 16.0 / 9.0)
        {
            f = y / 1080.0;
            fx = x / f;
            genshin_handle.size_frame = cv::Size(static_cast<int>(fx), 1080);
        }
        else
        {
            f = x / 1920.0;
            fy = y / f;
            genshin_handle.size_frame = cv::Size(1920, static_cast<int>(fy));
        }

        x = genshin_handle.size_frame.width;
        y = genshin_handle.size_frame.height;
        const cv::Size frame_size(x, y);
        genshin_handle.rect_paimon_maybe = make_relative_rect_macos(frame_size, 0.00, 0.00, 0.10, 0.10);
        genshin_handle.rect_minimap_cailb_maybe = make_relative_rect_macos(frame_size, 0.08, 0.00, 0.10, 0.10);
        genshin_handle.rect_minimap_maybe = make_relative_rect_macos(frame_size, 0.00, 0.00, 0.18, 0.22);
        genshin_handle.rect_uid_maybe = make_relative_rect_macos(frame_size, 0.88, 0.97, 0.12, 0.03);

        int UID_Rect_x = cvCeil(x - x * (1.0 - 0.865));
        int UID_Rect_y = cvCeil(y - 1080.0 * (1.0 - 0.9755));
        int UID_Rect_w = cvCeil(1920 * 0.11);
        int UID_Rect_h = cvCeil(1920 * 0.0938 * 0.11);
        genshin_handle.rect_uid = cv::Rect(UID_Rect_x, UID_Rect_y, UID_Rect_w, UID_Rect_h);
        genshin_handle.rect_left_give_items_maybe = make_relative_rect_macos(frame_size, 0.570, 0.250, 0.225, 0.500);
        genshin_handle.rect_left_give_items = genshin_handle.rect_left_give_items_maybe;
        genshin_handle.rect_right_pick_items_maybe = make_relative_rect_macos(frame_size, 0.050, 0.460, 0.160, 0.480);
        genshin_handle.rect_right_pick_items = genshin_handle.rect_right_pick_items_maybe;
    }

    void update_genshin_handle(const HWND& old_handle, tianli::global::GenshinHandle& out_genshin_handle)
    {
        tianli::frame::capture::macos::window_info window;
        if (old_handle != nullptr && tianli::frame::capture::macos::query_window(window_id_from_handle(old_handle), window))
            apply_window_info(window, out_genshin_handle);
        else
            get_genshin_handle(out_genshin_handle);
    }

#else
    tianli::global::GenshinHandle func_get_handle(HWND& in)
    {
        static tianli::global::GenshinHandle out;
        (void)in;
        get_genshin_handle(out);
        return out;
    }

    HWND get_cloud_window()
    {
        return nullptr;
    }

    void get_genshin_handle(tianli::global::GenshinHandle& genshin_handle)
    {
        genshin_handle.handle = nullptr;
        genshin_handle.is_exist = false;
        genshin_handle.scale = 1.0;
        genshin_handle.rect = { 0, 0, 0, 0 };
        genshin_handle.rect_client = { 0, 0, 0, 0 };
    }

    void GetUiRects(tianli::global::GenshinHandle& genshin_handle)
    {
        genshin_handle.size_frame = cv::Size(1920, 1080);
    }

    void update_genshin_handle(const HWND& old_handle, tianli::global::GenshinHandle& out_genshin_handle)
    {
        (void)old_handle;
        get_genshin_handle(out_genshin_handle);
    }
#endif

} // namespace TianLi::Genshin
