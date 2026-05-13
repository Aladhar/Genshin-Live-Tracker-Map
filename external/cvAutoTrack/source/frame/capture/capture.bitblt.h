#pragma once
#include "capture.include.h"
#include "utils/utils.window_scale.h"
#include "global/global.include.h"

namespace tianli::frame::capture
{
    class capture_bitblt : public capture_source
    {
    public:
        capture_bitblt(std::shared_ptr<global::logger> logger = nullptr) : capture_source(logger) { this->type = source_type::bitblt; }
        ~capture_bitblt() override = default;

    public:
        bool initialization() override
        {
            if (this->is_callback)
                this->source_handle = this->source_handle_callback();
            if (IsWindow(this->source_handle) == false)
                return false;
            return true;
        }
        bool uninitialized() override { return true; }
        bool set_capture_handle(HWND handle = 0) override
        {
            if (handle == nullptr)
                return false;
            if (handle == this->source_handle)
                return true;
            if (uninitialized() == false)
                return false;
            this->source_handle = handle;
            if (initialization() == false)
                return false;
            this->is_callback = false;
            return true;
        }
        bool set_source_handle_callback(std::function<HWND()> callback) override
        {
            if (callback == nullptr)
                return false;
            if (uninitialized() == false)
                return false;
            this->source_handle_callback = callback;
            if (initialization() == false)
                return false;
            this->is_callback = true;
            return true;
        }
        bool get_frame(cv::Mat& frame) override
        {
            auto handle = this->source_handle;
            if (this->is_callback)
                handle = this->source_handle_callback();
            if (handle == nullptr)
                return false;
            if (IsWindow(handle) == false)
                return false;
            RECT client_rect = { 0, 0, 0, 0 };
            if (GetClientRect(handle, &client_rect) == false)
                return false;

            POINT client_origin = { 0, 0 };
            if (ClientToScreen(handle, &client_origin) == false)
                return false;

            const int client_width = client_rect.right - client_rect.left;
            const int client_height = client_rect.bottom - client_rect.top;
            if (client_width < 480 || client_height < 360)
                return false;

            HDC hdc = GetDC(nullptr);
            if (hdc == nullptr)
                return false;

            HDC hmemdc = CreateCompatibleDC(hdc);
            if (hmemdc == nullptr)
            {
                ReleaseDC(nullptr, hdc);
                return false;
            }

            HBITMAP hbitmap = CreateCompatibleBitmap(hdc, client_width, client_height);
            if (hbitmap == nullptr)
            {
                DeleteDC(hmemdc);
                ReleaseDC(nullptr, hdc);
                return false;
            }

            HGDIOBJ old_bitmap = SelectObject(hmemdc, hbitmap);
            const BOOL copied = BitBlt(hmemdc, 0, 0, client_width, client_height, hdc, client_origin.x, client_origin.y, SRCCOPY | CAPTUREBLT);
            SelectObject(hmemdc, old_bitmap);
            if (!copied)
            {
                DeleteObject(hbitmap);
                DeleteDC(hmemdc);
                ReleaseDC(nullptr, hdc);
                return false;
            }

            BITMAPINFO bitmap_info{};
            bitmap_info.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
            bitmap_info.bmiHeader.biWidth = client_width;
            bitmap_info.bmiHeader.biHeight = -client_height;
            bitmap_info.bmiHeader.biPlanes = 1;
            bitmap_info.bmiHeader.biBitCount = 32;
            bitmap_info.bmiHeader.biCompression = BI_RGB;

            this->source_frame.create(client_height, client_width, CV_8UC4);
            const int scan_lines = GetDIBits(hdc, hbitmap, 0, client_height, this->source_frame.data, &bitmap_info, DIB_RGB_COLORS);

            DeleteObject(hbitmap);
            DeleteDC(hmemdc);
            ReleaseDC(nullptr, hdc);

            if (scan_lines != client_height || this->source_frame.empty())
                return false;

            frame = this->source_frame;
            return true;
        }

    private:
        RECT source_rect = { 0, 0, 0, 0 };
        RECT source_client_rect = { 0, 0, 0, 0 };
        cv::Size source_client_size;
    };

} // namespace tianli::frame::capture
