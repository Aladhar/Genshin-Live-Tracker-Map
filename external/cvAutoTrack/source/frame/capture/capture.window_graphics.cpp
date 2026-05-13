#include "capture.window_graphics.h"

namespace tianli::frame::capture
{
    namespace
    {
        bool has_visible_content(const cv::Mat& frame)
        {
            if (frame.empty())
                return false;

            const int channels = frame.channels();
            if (channels <= 0)
                return false;

            const int step_y = std::max(1, frame.rows / 240);
            const int step_x = std::max(1, frame.cols / 240);
            int visible_samples = 0;
            int total_samples = 0;

            for (int y = 0; y < frame.rows; y += step_y)
            {
                const auto row = frame.ptr<uchar>(y);
                for (int x = 0; x < frame.cols; x += step_x)
                {
                    const auto pixel = row + (x * channels);
                    const int brightness = channels >= 3 ? pixel[0] + pixel[1] + pixel[2] : pixel[0] * 3;
                    if (brightness > 12)
                        ++visible_samples;
                    ++total_samples;
                }
            }

            return total_samples > 0 && visible_samples > total_samples / 100;
        }

        bool copy_desktop_client_frame(HWND hwnd, cv::Mat& frame)
        {
            frame.release();

            if (hwnd == nullptr || !IsWindow(hwnd))
                return false;

            RECT client_rect{};
            POINT client_origin{};
            if (!GetClientRect(hwnd, &client_rect) || !ClientToScreen(hwnd, &client_origin))
                return false;

            const int client_width = client_rect.right - client_rect.left;
            const int client_height = client_rect.bottom - client_rect.top;
            if (client_width < 480 || client_height < 360)
                return false;

            HDC desktop_dc = GetDC(nullptr);
            if (desktop_dc == nullptr)
                return false;

            HDC memory_dc = CreateCompatibleDC(desktop_dc);
            if (memory_dc == nullptr)
            {
                ReleaseDC(nullptr, desktop_dc);
                return false;
            }

            HBITMAP bitmap = CreateCompatibleBitmap(desktop_dc, client_width, client_height);
            if (bitmap == nullptr)
            {
                DeleteDC(memory_dc);
                ReleaseDC(nullptr, desktop_dc);
                return false;
            }

            HGDIOBJ old_bitmap = SelectObject(memory_dc, bitmap);
            const BOOL copied = BitBlt(memory_dc, 0, 0, client_width, client_height, desktop_dc, client_origin.x, client_origin.y, SRCCOPY | CAPTUREBLT);
            SelectObject(memory_dc, old_bitmap);

            if (!copied)
            {
                DeleteObject(bitmap);
                DeleteDC(memory_dc);
                ReleaseDC(nullptr, desktop_dc);
                return false;
            }

            BITMAPINFO bitmap_info{};
            bitmap_info.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
            bitmap_info.bmiHeader.biWidth = client_width;
            bitmap_info.bmiHeader.biHeight = -client_height;
            bitmap_info.bmiHeader.biPlanes = 1;
            bitmap_info.bmiHeader.biBitCount = 32;
            bitmap_info.bmiHeader.biCompression = BI_RGB;

            frame.create(client_height, client_width, CV_8UC4);
            const int scan_lines = GetDIBits(desktop_dc, bitmap, 0, client_height, frame.data, &bitmap_info, DIB_RGB_COLORS);

            DeleteObject(bitmap);
            DeleteDC(memory_dc);
            ReleaseDC(nullptr, desktop_dc);

            if (scan_lines != client_height || frame.empty() || !has_visible_content(frame))
            {
                frame.release();
                return false;
            }

            return true;
        }

        bool get_client_box_on_monitor(HWND hwnd, uint32_t width, uint32_t height, D3D11_BOX* client_box)
        {
            if (client_box == nullptr)
                return false;

            HMONITOR monitor = MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST);
            MONITORINFOEXW monitor_info{};
            monitor_info.cbSize = sizeof(monitor_info);
            RECT client_rect{};
            POINT client_origin{};
            if (!GetMonitorInfoW(monitor, &monitor_info) || !GetClientRect(hwnd, &client_rect) || !ClientToScreen(hwnd, &client_origin))
                return false;

            const int client_width = client_rect.right - client_rect.left;
            const int client_height = client_rect.bottom - client_rect.top;
            if (client_width <= 0 || client_height <= 0)
                return false;

            const int left = client_origin.x - monitor_info.rcMonitor.left;
            const int top = client_origin.y - monitor_info.rcMonitor.top;
            if (left >= static_cast<int>(width) || top >= static_cast<int>(height))
                return false;

            const int right = std::min(static_cast<int>(width), left + client_width);
            const int bottom = std::min(static_cast<int>(height), top + client_height);
            if (right <= left || bottom <= top)
                return false;

            client_box->left = static_cast<UINT>(std::max(0, left));
            client_box->top = static_cast<UINT>(std::max(0, top));
            client_box->right = static_cast<UINT>(right);
            client_box->bottom = static_cast<UINT>(bottom);
            client_box->front = 0;
            client_box->back = 1;
            return true;
        }

        bool get_client_rect_on_monitor(HWND hwnd, const DXGI_OUTPUT_DESC& output_desc, const D3D11_TEXTURE2D_DESC& texture_desc, cv::Rect& rect)
        {
            RECT client_rect{};
            POINT client_origin{};
            if (!GetClientRect(hwnd, &client_rect) || !ClientToScreen(hwnd, &client_origin))
                return false;

            const auto left = client_origin.x - output_desc.DesktopCoordinates.left;
            const auto top = client_origin.y - output_desc.DesktopCoordinates.top;
            const auto width = client_rect.right - client_rect.left;
            const auto height = client_rect.bottom - client_rect.top;
            if (width <= 0 || height <= 0)
                return false;

            rect = cv::Rect(left, top, width, height) & cv::Rect(0, 0, static_cast<int>(texture_desc.Width), static_cast<int>(texture_desc.Height));
            return !rect.empty();
        }
    } // namespace

    bool capture_window_graphics::get_desktop_gdi_frame(cv::Mat& frame)
    {
        this->source_frame.release();
        if (!copy_desktop_client_frame(this->source_handle, this->source_frame))
        {
            frame.release();
            return false;
        }

        frame = this->source_frame;
        return true;
    }

    bool capture_window_graphics::get_desktop_duplication_frame(cv::Mat& frame)
    {
        frame.release();
        this->source_frame.release();

        if (this->source_handle == nullptr || !IsWindow(this->source_handle))
            return false;

        auto& d3d_device = utils::window_graphics::graphics_global::get_instance().d3d_device;
        if (d3d_device == nullptr)
            return false;

        if (m_d3dContext == nullptr)
            d3d_device->GetImmediateContext(m_d3dContext.put());
        if (m_d3dContext == nullptr)
            return false;

        HMONITOR monitor = MonitorFromWindow(this->source_handle, MONITOR_DEFAULTTONEAREST);

        auto dxgi_device = d3d_device.as<IDXGIDevice>();
        winrt::com_ptr<IDXGIAdapter> adapter;
        if (FAILED(dxgi_device->GetAdapter(adapter.put())))
            return false;

        winrt::com_ptr<IDXGIOutput> selected_output;
        DXGI_OUTPUT_DESC selected_output_desc{};
        for (UINT index = 0;; ++index)
        {
            winrt::com_ptr<IDXGIOutput> output;
            HRESULT enum_result = adapter->EnumOutputs(index, output.put());
            if (enum_result == DXGI_ERROR_NOT_FOUND)
                break;
            if (FAILED(enum_result))
                return false;

            DXGI_OUTPUT_DESC output_desc{};
            if (FAILED(output->GetDesc(&output_desc)))
                continue;

            if (output_desc.Monitor == monitor)
            {
                selected_output = output;
                selected_output_desc = output_desc;
                break;
            }
        }
        if (selected_output == nullptr)
            return false;

        winrt::com_ptr<IDXGIOutput1> output1 = selected_output.as<IDXGIOutput1>();
        winrt::com_ptr<IDXGIOutputDuplication> duplication;
        if (FAILED(output1->DuplicateOutput(d3d_device.get(), duplication.put())))
            return false;

        DXGI_OUTDUPL_FRAME_INFO frame_info{};
        winrt::com_ptr<IDXGIResource> desktop_resource;
        HRESULT acquire_result = duplication->AcquireNextFrame(500, &frame_info, desktop_resource.put());
        if (FAILED(acquire_result))
            return false;

        auto release_frame = [&]() {
            duplication->ReleaseFrame();
        };

        winrt::com_ptr<ID3D11Texture2D> desktop_texture = desktop_resource.as<ID3D11Texture2D>();
        D3D11_TEXTURE2D_DESC staging_desc{};
        desktop_texture->GetDesc(&staging_desc);
        staging_desc.Usage = D3D11_USAGE_STAGING;
        staging_desc.BindFlags = 0;
        staging_desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
        staging_desc.MiscFlags = 0;

        cv::Rect crop_rect;
        if (!get_client_rect_on_monitor(this->source_handle, selected_output_desc, staging_desc, crop_rect))
        {
            release_frame();
            return false;
        }

        winrt::com_ptr<ID3D11Texture2D> staging_texture;
        if (FAILED(d3d_device->CreateTexture2D(&staging_desc, nullptr, staging_texture.put())))
        {
            release_frame();
            return false;
        }

        m_d3dContext->CopyResource(staging_texture.get(), desktop_texture.get());

        D3D11_MAPPED_SUBRESOURCE mapped_tex{};
        if (FAILED(m_d3dContext->Map(staging_texture.get(), 0, D3D11_MAP_READ, 0, &mapped_tex)))
        {
            release_frame();
            return false;
        }

        if (mapped_tex.pData == nullptr)
        {
            m_d3dContext->Unmap(staging_texture.get(), 0);
            release_frame();
            return false;
        }

        cv::Mat mapped_frame(staging_desc.Height, staging_desc.Width, CV_8UC4, mapped_tex.pData, mapped_tex.RowPitch);
        mapped_frame(crop_rect).copyTo(this->source_frame);

        m_d3dContext->Unmap(staging_texture.get(), 0);
        release_frame();

        if (this->source_frame.empty() || this->source_frame.cols < 480 || this->source_frame.rows < 360 || !has_visible_content(this->source_frame))
            return false;

        frame = this->source_frame;
        return true;
    }

    bool capture_window_graphics::get_frame(cv::Mat& frame)
    {
        auto fail = [&]() {
            this->source_frame.release();
            return get_desktop_gdi_frame(frame);
        };
        auto get_latest_frame = [&]() {
            winrt::Windows::Graphics::Capture::Direct3D11CaptureFrame latest_frame{ nullptr };
            for (int attempt = 0; attempt < 30; ++attempt)
            {
                auto candidate = m_framePool.TryGetNextFrame();
                if (candidate != nullptr)
                {
                    latest_frame = candidate;
                    continue;
                }

                if (latest_frame != nullptr)
                    break;

                Sleep(10);
            }
            return latest_frame;
        };

        if (this->is_callback)
            set_capture_handle(this->source_handle_callback());

        if (get_desktop_duplication_frame(frame))
            return true;

        if (m_framePool == nullptr)
        {
            uninitialized();
            if (initialization() == false)
                return fail();
        }

        auto new_frame = get_latest_frame();
        if (new_frame == nullptr)
            return fail();

        auto frame_time = new_frame.SystemRelativeTime();
        if (m_hasLastFrameTime && frame_time <= m_lastFrameTime)
        {
            ++m_staleFrameCount;
            if (m_staleFrameCount >= 2)
            {
                uninitialized();
                Sleep(30);
                if (initialization() == false)
                    return fail();
                Sleep(100);

                new_frame = get_latest_frame();
                if (new_frame == nullptr)
                    return fail();

                frame_time = new_frame.SystemRelativeTime();
                if (m_hasLastFrameTime && frame_time <= m_lastFrameTime)
                    return fail();
            }
        }
        else
        {
            m_staleFrameCount = 0;
        }

        auto frame_size = new_frame.ContentSize();
        if (frame_size.Width != m_lastSize.Width || frame_size.Height != m_lastSize.Height)
        {
            m_framePool.Recreate(m_device.as<winrt::Windows::Graphics::DirectX::Direct3D11::IDirect3DDevice>(), winrt::Windows::Graphics::DirectX::DirectXPixelFormat::B8G8R8A8UIntNormalized, 2,
                                 frame_size);
            m_lastSize = frame_size;

            m_swapChain->ResizeBuffers(2, static_cast<uint32_t>(m_lastSize.Width), static_cast<uint32_t>(m_lastSize.Height),
                                       static_cast<DXGI_FORMAT>(winrt::Windows::Graphics::DirectX::DirectXPixelFormat::B8G8R8A8UIntNormalized), 0);
        }

        auto frameSurface = utils::window_graphics::GetDXGIInterfaceFromObject<ID3D11Texture2D>(new_frame.Surface());

        D3D11_TEXTURE2D_DESC staging_desc{};
        frameSurface->GetDesc(&staging_desc);
        staging_desc.Usage = D3D11_USAGE_STAGING;
        staging_desc.BindFlags = 0;
        staging_desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
        staging_desc.MiscFlags = 0;

        winrt::com_ptr<ID3D11Texture2D> staging_texture;
        if (FAILED(utils::window_graphics::graphics_global::get_instance().d3d_device->CreateTexture2D(&staging_desc, nullptr, staging_texture.put())))
            return fail();

        m_d3dContext->CopyResource(staging_texture.get(), frameSurface.get());

        D3D11_MAPPED_SUBRESOURCE mappedTex{};
        if (FAILED(m_d3dContext->Map(staging_texture.get(), 0, D3D11_MAP_READ, 0, &mappedTex)))
            return fail();

        if (mappedTex.pData == nullptr)
        {
            m_d3dContext->Unmap(staging_texture.get(), 0);
            return fail();
        }

        cv::Mat mapped_frame(staging_desc.Height, staging_desc.Width, CV_8UC4, mappedTex.pData, mappedTex.RowPitch);

        D3D11_BOX client_box{};
        bool client_box_available = get_client_box_on_monitor(this->source_handle, staging_desc.Width, staging_desc.Height, &client_box);
        if (client_box_available)
        {
            if (client_box.right > staging_desc.Width || client_box.bottom > staging_desc.Height || client_box.left >= client_box.right || client_box.top >= client_box.bottom)
            {
                m_d3dContext->Unmap(staging_texture.get(), 0);
                return fail();
            }

            mapped_frame(cv::Rect(client_box.left, client_box.top, client_box.right - client_box.left, client_box.bottom - client_box.top)).copyTo(this->source_frame);
        }
        else
        {
            mapped_frame.copyTo(this->source_frame);
        }

        m_d3dContext->Unmap(staging_texture.get(), 0);

        if (this->source_frame.empty())
            return fail();
        if (this->source_frame.cols < 480 || this->source_frame.rows < 360)
            return fail();
        if (!has_visible_content(this->source_frame))
            return fail();

        frame = this->source_frame;
        m_lastFrameTime = frame_time;
        m_hasLastFrameTime = true;
        return true;
    }
} // namespace tianli::frame::capture
