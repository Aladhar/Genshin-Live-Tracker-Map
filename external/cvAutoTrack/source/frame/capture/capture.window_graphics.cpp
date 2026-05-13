#include "capture.window_graphics.h"

namespace tianli::frame::capture
{
    bool capture_window_graphics::get_frame(cv::Mat& frame)
    {
        if (this->is_callback)
            set_capture_handle(this->source_handle_callback());

        if (m_framePool == nullptr)
        {
            uninitialized();
            if (initialization() == false)
                return false;
        }

        winrt::Windows::Graphics::Capture::Direct3D11CaptureFrame new_frame{ nullptr };
        for (int attempt = 0; attempt < 5 && new_frame == nullptr; ++attempt)
        {
            new_frame = m_framePool.TryGetNextFrame();
            if (new_frame == nullptr)
                Sleep(10);
        }
        if (new_frame == nullptr)
            return false;

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
            return false;

        m_d3dContext->CopyResource(staging_texture.get(), frameSurface.get());

        D3D11_MAPPED_SUBRESOURCE mappedTex{};
        if (FAILED(m_d3dContext->Map(staging_texture.get(), 0, D3D11_MAP_READ, 0, &mappedTex)))
            return false;

        if (mappedTex.pData == nullptr)
        {
            m_d3dContext->Unmap(staging_texture.get(), 0);
            return false;
        }

        cv::Mat mapped_frame(staging_desc.Height, staging_desc.Width, CV_8UC4, mappedTex.pData, mappedTex.RowPitch);

        D3D11_BOX client_box{};
        bool client_box_available = utils::window_graphics::get_client_box(this->source_handle, staging_desc.Width, staging_desc.Height, &client_box);
        if (client_box_available)
        {
            if (client_box.right > staging_desc.Width || client_box.bottom > staging_desc.Height || client_box.left >= client_box.right || client_box.top >= client_box.bottom)
            {
                m_d3dContext->Unmap(staging_texture.get(), 0);
                return false;
            }

            mapped_frame(cv::Rect(client_box.left, client_box.top, client_box.right - client_box.left, client_box.bottom - client_box.top)).copyTo(this->source_frame);
        }
        else
        {
            mapped_frame.copyTo(this->source_frame);
        }

        m_d3dContext->Unmap(staging_texture.get(), 0);

        if (this->source_frame.empty())
            return false;
        if (this->source_frame.cols < 480 || this->source_frame.rows < 360)
            return false;

        frame = this->source_frame;
        return true;
    }
} // namespace tianli::frame::capture
