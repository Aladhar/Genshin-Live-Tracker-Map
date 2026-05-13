#include "pch.h"
#include "AutoTrack.h"

#include "genshin/genshin.h"
#include "match/match.star.h"
#include "match/match.template.h"
#include "match/match.uid.h"
#include "utils/Utils.h"
#include "utils/convect.string.h"
#include "algorithms/algorithms.direction.h"
#include "algorithms/algorithms.rotation.h"
#include "algorithms/filter/filter.kalman.h"
#include "frame/capture/capture.bitblt.h"
#include "resource/version.h"

#include "match/surf/SurfMatch.h"
#include <cmath>
#include <ctime>

namespace
{
    struct reward_amount_detection
    {
        bool found = false;
        int value = 0;
        double score = 0.0;
        cv::Rect rect;
    };

    cv::Rect clamp_rect(const cv::Rect& rect, const cv::Size& bounds)
    {
        return rect & cv::Rect(0, 0, bounds.width, bounds.height);
    }

    cv::Rect offset_rect(const cv::Rect& rect, const cv::Point& offset)
    {
        return { rect.x + offset.x, rect.y + offset.y, rect.width, rect.height };
    }

    cv::Rect frame_to_client_rect(const tianli::global::GenshinHandle& handle, const cv::Rect& frame_rect)
    {
        const auto client_width = handle.rect_client.right - handle.rect_client.left;
        const auto client_height = handle.rect_client.bottom - handle.rect_client.top;
        if (handle.size_frame.width <= 0 || handle.size_frame.height <= 0 || client_width <= 0 || client_height <= 0)
            return {};

        const auto scale_x = static_cast<double>(client_width) / static_cast<double>(handle.size_frame.width);
        const auto scale_y = static_cast<double>(client_height) / static_cast<double>(handle.size_frame.height);
        return {
            cvRound(frame_rect.x * scale_x),
            cvRound(frame_rect.y * scale_y),
            cvRound(frame_rect.width * scale_x),
            cvRound(frame_rect.height * scale_y),
        };
    }

    std::string rect_to_json_array(const cv::Rect& rect)
    {
        return global::format("[{},{},{},{}]", rect.x, rect.y, rect.width, rect.height);
    }

    std::string format_system_time(const std::chrono::system_clock::time_point& time_point)
    {
        auto time = std::chrono::system_clock::to_time_t(time_point);
        std::tm local_time{};
        localtime_s(&local_time, &time);

        char buffer[32]{};
        if (std::strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", &local_time) == 0)
            return {};
        return buffer;
    }

    bool copy_text_to_buffer(const std::string& text, char* buff, int buff_size, ErrorCode& err)
    {
        if (buff == nullptr || buff_size < 1)
        {
            err = { 291, "Buffer pointer is null or buffer size is less than 1" };
            return false;
        }
        if (static_cast<int>(text.size()) >= buff_size)
        {
            err = { 292, "Buffer is too small" };
            return false;
        }
        strcpy_s(buff, buff_size, text.c_str());
        return true;
    }

    cv::Rect crop_nonzero_bounds(const cv::Mat& binary)
    {
        std::vector<cv::Point> points;
        cv::findNonZero(binary, points);
        if (points.empty())
            return {};
        return cv::boundingRect(points);
    }

    cv::Mat prepare_binary_text(const cv::Mat& image)
    {
        auto gray = TianLi::Match::to_gray_image(image);
        if (gray.empty())
            return {};

        cv::Mat blurred;
        cv::GaussianBlur(gray, blurred, cv::Size(3, 3), 0);

        cv::Mat binary;
        cv::threshold(blurred, binary, 0, 255, cv::THRESH_BINARY | cv::THRESH_OTSU);
        if (cv::countNonZero(binary) > (binary.rows * binary.cols) / 2)
            cv::bitwise_not(binary, binary);

        cv::morphologyEx(binary, binary, cv::MORPH_OPEN, cv::getStructuringElement(cv::MORPH_RECT, cv::Size(2, 2)));
        return binary;
    }

    cv::Mat build_amount_template(int amount, cv::Mat (&digit_templates)[10])
    {
        const auto text = std::to_string(amount);

        std::vector<cv::Mat> glyphs;
        glyphs.reserve(text.size());

        int max_height = 0;
        int total_width = 0;
        for (const auto digit_char : text)
        {
            auto glyph = prepare_binary_text(digit_templates[digit_char - '0']);
            const auto glyph_bounds = crop_nonzero_bounds(glyph);
            if (glyph_bounds.empty())
                continue;
            glyph = glyph(glyph_bounds).clone();
            glyphs.push_back(glyph);
            max_height = std::max(max_height, glyph.rows);
            total_width += glyph.cols;
        }

        if (glyphs.empty() || max_height <= 0)
            return {};

        const auto spacing = std::max(1, max_height / 5);
        total_width += spacing * static_cast<int>(glyphs.size() > 0 ? glyphs.size() - 1 : 0);

        cv::Mat templ(max_height, total_width, CV_8UC1, cv::Scalar(0));
        int cursor_x = 0;
        for (const auto& glyph : glyphs)
        {
            const auto y = (max_height - glyph.rows) / 2;
            glyph.copyTo(templ(cv::Rect(cursor_x, y, glyph.cols, glyph.rows)));
            cursor_x += glyph.cols + spacing;
        }

        return templ;
    }

    reward_amount_detection detect_reward_amount(const cv::Mat& image, cv::Mat (&digit_templates)[10])
    {
        reward_amount_detection best_match;
        if (image.empty())
            return best_match;

        const auto binary = prepare_binary_text(image);
        if (binary.empty())
            return best_match;

        const std::vector<int> known_amounts = { 1, 2, 3, 5, 10, 15, 20, 30, 40, 60, 80 };
        for (const auto amount : known_amounts)
        {
            const auto amount_template = build_amount_template(amount, digit_templates);
            if (amount_template.empty())
                continue;

            TianLi::Match::template_match_options options;
            options.threshold = 0.55;
            options.min_scale = 0.70;
            options.max_scale = 1.35;
            options.scale_step = 0.05;
            options.max_iou = 0.10;
            options.max_matches = 1;

            const auto matches = TianLi::Match::detect_template_multiscale(binary, amount_template, options);
            if (matches.empty())
                continue;

            const auto& match = matches.front();
            if (!best_match.found || match.score > best_match.score)
            {
                best_match = {
                    true,
                    amount,
                    match.score,
                    match.rect,
                };
            }
        }

        return best_match;
    }
} // namespace

AutoTrack::AutoTrack(ErrorCode& err, Resources& res) : err(err), res(res)
{
    err.enableWirteFile();

    genshin_avatar_position.target_map_world_center = res.map_relative_center;
    genshin_avatar_position.target_map_world_scale = res.map_relative_scale;

    genshin_handle.config.frame_source = std::make_shared<tianli::frame::capture::capture_bitblt>();
    genshin_handle.config.frame_source->initialization();

    genshin_screen.minimap_cailb_params = std::make_shared<tianli::global::match_minimap_cailb_params>();
    genshin_screen.paimon_search_params = std::make_shared<tianli::global::check_paimon_search_params>();

    genshin_minimap.matcher = std::make_shared<SurfMatch>(res);

    genshin_avatar_position.config.pos_filter = std::make_shared<tianli::algorithms::filter::filter_kalman>();
}

bool AutoTrack::init()
{
    if (!genshin_minimap.is_init_finish)
    {
        genshin_minimap.is_run_init_start = true;
        TianLi::Genshin::Match::get_avatar_position(genshin_minimap, genshin_avatar_position);
        genshin_minimap.is_run_init_start = false;

        genshin_minimap.is_init_finish = true;
    }
    return genshin_minimap.is_init_finish;
}

bool AutoTrack::uninit()
{
    if (genshin_minimap.is_init_finish)
    {
        genshin_minimap.is_run_uninit_start = true;
        TianLi::Genshin::Match::get_avatar_position(genshin_minimap, genshin_avatar_position);
        genshin_minimap.is_run_uninit_start = false;

        genshin_minimap.is_init_finish = false;
    }
    return !genshin_minimap.is_init_finish;
}

bool AutoTrack::SetHandle(long long int handle)
{
    if (handle == 0)
    {
        genshin_handle.config.is_auto_find_genshin = true;
        return true;
    }
    else
    {
        genshin_handle.config.is_auto_find_genshin = false;
        genshin_handle.handle = (HWND)handle;
    }
    return IsWindow(genshin_handle.handle);
}

bool AutoTrack::SetWorldCenter(double x, double y)
{
    genshin_avatar_position.target_map_world_center.x = x;
    genshin_avatar_position.target_map_world_center.y = y;
    return true;
}

bool AutoTrack::SetWorldScale(double scale)
{
    genshin_avatar_position.target_map_world_scale = scale;
    return true;
}

bool AutoTrack::startServe()
{
    return false;
}

bool AutoTrack::stopServe()
{
    return false;
}

bool AutoTrack::SetDisableFileLog()
{
    err.disableWirteFile();
    return true;
}

bool AutoTrack::SetEnableFileLog()
{
    err.enableWirteFile();
    return true;
}

bool AutoTrack::DebugCapture()
{
    return DebugCapturePath("Capture.png", 12);
}

bool AutoTrack::DebugCapturePath(const char* path_buff, int buff_size)
{
    if (path_buff == NULL || buff_size < 1)
    {
        err = { 251, "Path buffer pointer is null or path buffer size is less than 1" };
        return false;
    }

    if (!try_get_genshin_windows())
    {
        return false;
    }

    if (genshin_screen.img_screen.empty())
    {
        err = { 252, "Frame is empty" };
        return false;
    }
    cv::Mat out_info_img = genshin_screen.img_screen.clone();
    switch (genshin_handle.config.frame_source->type)
    {
        case tianli::frame::frame_source::source_type::bitblt:
            {
                // Draw Paimon rect.
                cv::rectangle(out_info_img, genshin_paimon.rect_paimon, cv::Scalar(0, 0, 255), 2);
                // Draw minimap rect.
                cv::rectangle(out_info_img, genshin_minimap.rect_minimap, cv::Scalar(0, 0, 255), 2);
                cv::Rect Avatar = genshin_minimap.rect_avatar;
                Avatar.x += genshin_minimap.rect_minimap.x;
                Avatar.y += genshin_minimap.rect_minimap.y;

                // Draw avatar rect.
                cv::rectangle(out_info_img, Avatar, cv::Scalar(0, 0, 255), 2);
                // Draw UID rect.
                cv::rectangle(out_info_img, genshin_handle.rect_uid, cv::Scalar(0, 0, 255), 2);
                break;
            }
        case tianli::frame::frame_source::source_type::window_graphics:
            {
                // Draw Paimon rect.
                cv::rectangle(out_info_img, genshin_paimon.rect_paimon, cv::Scalar(0, 0, 255), 2);
                // Draw minimap rect.
                cv::rectangle(out_info_img, genshin_minimap.rect_minimap, cv::Scalar(0, 0, 255), 2);
                cv::Rect Avatar = genshin_minimap.rect_avatar;
                Avatar.x += genshin_minimap.rect_minimap.x;
                Avatar.y += genshin_minimap.rect_minimap.y;

                // Draw avatar rect.
                cv::rectangle(out_info_img, Avatar, cv::Scalar(0, 0, 255), 2);
                // Draw UID rect.
                cv::rectangle(out_info_img, genshin_handle.rect_uid, cv::Scalar(0, 0, 255), 2);
            }
    }

    std::string last_time_str = format_system_time(genshin_screen.last_time);

    cv::putText(out_info_img, last_time_str, cv::Point(out_info_img.cols / 2, out_info_img.rows / 2), 1, 1, cv::Scalar(128, 128, 128, 255), 1, 16, 0);
    auto err_msg_str = err.toJson();
    cv::putText(out_info_img, err_msg_str, cv::Point(0, out_info_img.rows / 2 - 100), 1, 1, cv::Scalar(128, 128, 128, 128), 1, 16, 0);

    auto path = utils::to_utf8(path_buff);

    bool rel = cv::imwrite(path_buff, out_info_img);

    if (!rel)
    {
        err = { 252, std::string("Failed to save frame. Check whether the file path is valid: ") + std::string(path_buff) };
        return false;
    }

    return clear_error_logs();
}

bool AutoTrack::GetTransformOfMap(double& x, double& y, double& a, int& mapId)
{
    double x2 = 0, y2 = 0, a2 = 0;
    int mapId2 = 0;
    if (!genshin_minimap.is_init_finish)
    {
        init();
    }

    if (!GetPositionOfMap(x2, y2, mapId2))
    {
        return false;
    }

    GetDirection(a2);
    x = x2;
    y = y2;
    a = a2;
    mapId = mapId2;
    return clear_error_logs();
}

bool AutoTrack::GetPosition(double& x, double& y)
{
    if (try_get_genshin_windows() == false)
    {
        return false;
    }
    if (!genshin_minimap.is_init_finish)
    {
        init();
    }
    if (getMiniMapRefMat() == false)
    {
        // err = { 1001, "Paimon was not detected while getting position" };
        return false;
    }

    if (genshin_minimap.img_minimap.empty())
    {
        err = { 5, "Genshin minimap area is empty" };
        return false;
    }
    genshin_minimap.config.is_find_paimon = true;

    TianLi::Genshin::Match::get_avatar_position(genshin_minimap, genshin_avatar_position);

    cv::Point2d pos = genshin_avatar_position.position;

    x = pos.x;
    y = pos.y;

    return clear_error_logs();
}

bool AutoTrack::GetPositionOfMap(double& x, double& y, int& mapId)
{
    mapId = 0;
    // The new algorithm outputs raw coordinates directly, so no extra processing is needed.
    bool isSuccess = GetPosition(x, y);
    if (isSuccess != true)
    {
        return false;
    }
    return clear_error_logs();
}

bool AutoTrack::GetDirection(double& a)
{
    if (try_get_genshin_windows() == false)
    {
        return false;
    }
    if (getMiniMapRefMat() == false)
    {
        // err = { 2001, "Paimon was not detected while getting character direction" };
        return false;
    }
    if (genshin_minimap.rect_avatar.empty())
    {
        err = { 11, "Genshin character arrow area is empty" };
        return false;
    }

    tianli::global::direction_calculation_config config;
    direction_calculation(genshin_minimap.img_avatar, a, config);
    if (config.error)
    {
        err = config.err;
        return false;
    }

    return clear_error_logs();
}

bool AutoTrack::GetRotation(double& a)
{
    if (try_get_genshin_windows() == false)
    {
        return false;
    }
    if (getMiniMapRefMat() == false)
    {
        // err = { 3001, "Paimon was not detected while getting camera rotation" };
        return false;
    }

    tianli::global::rotation_calculation_config config;
    rotation_calculation(genshin_minimap.img_minimap, a, config);
    if (config.error)
    {
        err = config.err;
        return false;
    }

    return clear_error_logs();
}

bool AutoTrack::GetUID(int& uid)
{
    if (try_get_genshin_windows() == false)
    {
        return false;
    }

    cv::Mat& giUIDRef = genshin_screen.img_uid;

    std::vector<cv::Mat> channels;

    split(giUIDRef, channels);

    if (genshin_handle.config.frame_source->type == tianli::frame::frame_source::source_type::window_graphics)
    {
        cv::cvtColor(giUIDRef, giUIDRef, cv::COLOR_RGBA2GRAY);
    }
    else
    {
        giUIDRef = channels[3];
    }

    tianli::global::uid_calculation_config config;
    uid_calculation(res, giUIDRef, uid, config);
    if (config.error)
    {
        err = config.err;
        return false;
    }

    return clear_error_logs();
}

bool AutoTrack::GetRewardDetectionsJson(char* json_buff, int buff_size)
{
    if (try_get_genshin_windows() == false)
    {
        return false;
    }

    bool tracker_available = false;
    double tracker_x = 0.0;
    double tracker_y = 0.0;
    int tracker_map_id = 0;

    if (!genshin_minimap.is_init_finish)
    {
        init();
    }

    if (getMiniMapRefMat() && !genshin_minimap.img_minimap.empty())
    {
        genshin_minimap.config.is_find_paimon = true;
        TianLi::Genshin::Match::get_avatar_position(genshin_minimap, genshin_avatar_position);
        tracker_x = genshin_avatar_position.position.x;
        tracker_y = genshin_avatar_position.position.y;
        tracker_map_id = genshin_minimap.matcher ? genshin_minimap.matcher->CurrentAreaId() : 0;
        tracker_available = std::isfinite(tracker_x) && std::isfinite(tracker_y);
    }

    const auto reward_roi_frame = genshin_handle.rect_left_give_items.empty()
        ? genshin_handle.rect_left_give_items_maybe
        : genshin_handle.rect_left_give_items;
    const auto reward_roi_client = frame_to_client_rect(genshin_handle, reward_roi_frame);
    const auto& reward_roi_image = genshin_screen.img_left_give_items.empty()
        ? genshin_screen.img_left_give_items_maybe
        : genshin_screen.img_left_give_items;

    TianLi::Match::template_match_options primogem_options;
    primogem_options.threshold = 0.84;
    primogem_options.min_scale = 0.80;
    primogem_options.max_scale = 1.20;
    primogem_options.scale_step = 0.05;
    primogem_options.max_iou = 0.20;
    primogem_options.max_matches = 4;

    const auto primogem_matches = TianLi::Match::detect_template_multiscale(reward_roi_image, res.PrimogemTemplate, primogem_options);

    const auto client_width = genshin_handle.rect_client.right - genshin_handle.rect_client.left;
    const auto client_height = genshin_handle.rect_client.bottom - genshin_handle.rect_client.top;

    std::string json = "{";
    json += global::format("\"tracker\":{{\"available\":{},\"position\":{{\"x\":{:.6f},\"y\":{:.6f},\"mapId\":{}}}}},", tracker_available ? "true" : "false", tracker_x, tracker_y, tracker_map_id);
    json += global::format("\"layout\":{{\"frame\":[{},{}],\"client\":[{},{}]}},", genshin_handle.size_frame.width, genshin_handle.size_frame.height, client_width, client_height);
    json += global::format("\"rewardRoi\":{{\"frame\":{},\"client\":{}}},", rect_to_json_array(reward_roi_frame), rect_to_json_array(reward_roi_client));
    json += "\"matches\":[";

    for (size_t index = 0; index < primogem_matches.size(); ++index)
    {
        const auto& match = primogem_matches[index];
        const auto match_frame_rect = offset_rect(match.rect, reward_roi_frame.tl());
        const auto match_client_rect = frame_to_client_rect(genshin_handle, match_frame_rect);

        const auto amount_search_rect = clamp_rect(
            cv::Rect(
                match.rect.x + match.rect.width,
                match.rect.y - cvRound(match.rect.height * 0.15),
                cvRound(match.rect.width * 4.50),
                cvRound(match.rect.height * 1.30)),
            reward_roi_image.size());

        const auto amount_detection = amount_search_rect.empty()
            ? reward_amount_detection {}
            : detect_reward_amount(reward_roi_image(amount_search_rect), res.UIDnumber);

        const auto amount_frame_rect = offset_rect(amount_search_rect, reward_roi_frame.tl());
        const auto amount_client_rect = frame_to_client_rect(genshin_handle, amount_frame_rect);

        json += "{";
        json += "\"template\":\"primogem\",";
        json += global::format("\"score\":{:.6f},\"scale\":{:.4f},", match.score, match.scale);
        json += global::format("\"rect\":{{\"roi\":{},\"frame\":{},\"client\":{}}},", rect_to_json_array(match.rect), rect_to_json_array(match_frame_rect), rect_to_json_array(match_client_rect));
        json += global::format("\"amount\":{{\"found\":{}", amount_detection.found ? "true" : "false");
        if (amount_detection.found)
        {
            json += global::format(",\"value\":{},\"score\":{:.6f},\"searchRect\":{{\"roi\":{},\"frame\":{},\"client\":{}}}",
                amount_detection.value,
                amount_detection.score,
                rect_to_json_array(amount_search_rect),
                rect_to_json_array(amount_frame_rect),
                rect_to_json_array(amount_client_rect));
        }
        json += "}";
        json += "}";

        if (index + 1 < primogem_matches.size())
            json += ",";
    }

    json += "]}";

    if (!copy_text_to_buffer(json, json_buff, buff_size, err))
    {
        return false;
    }

    return clear_error_logs();
}

bool AutoTrack::GetAllInfo(double& x, double& y, int& mapId, double& a, double& r, int& uid)
{
    if (try_get_genshin_windows() == false)
    {
        return false;
    }
    if (!genshin_minimap.is_init_finish)
    {
        init();
    }
    if (getMiniMapRefMat() == false)
    {
        // err = { 1001, "Paimon was not detected while getting all information" };
        return false;
    }
    if (genshin_minimap.img_minimap.empty())
    {
        err = { 5, "Genshin minimap area is empty" };
        return false;
    }
    if (genshin_minimap.rect_avatar.empty())
    {
        err = { 11, "Genshin character arrow area is empty" };
        return false;
    }

    // x,y,mapId
    {
        genshin_minimap.config.is_find_paimon = true;
        GetPositionOfMap(x, y, mapId);
    }

    // a
    {
        tianli::global::direction_calculation_config config;
        direction_calculation(genshin_minimap.img_avatar, a, config);
        if (config.error)
        {
            err = config.err;
        }
    }
    // r
    {
        tianli::global::rotation_calculation_config config;
        rotation_calculation(genshin_minimap.img_minimap, r, config);
        if (config.error)
        {
            err = config.err;
        }
    }
    cv::Mat& giUIDRef = genshin_screen.img_uid;
    // uid
    {
        std::vector<cv::Mat> channels;

        cv::split(giUIDRef, channels);

        if (genshin_handle.config.frame_source->type == tianli::frame::frame_source::source_type::window_graphics)
        {
            cv::cvtColor(giUIDRef, giUIDRef, cv::COLOR_RGBA2GRAY);
        }
        else
        {
            giUIDRef = channels[3];
        }

        tianli::global::uid_calculation_config config;
        uid_calculation(res, giUIDRef, uid, config);
        if (config.error)
        {
            err = config.err;
        }
    }

    return clear_error_logs();
}

bool AutoTrack::try_get_genshin_windows()
{
    if (!clear_error_logs())
    {
        err = { 0, "Exited normally" };
        return false;
    }
    if (!getGengshinImpactWnd())
    {
        err = { 101, "Failed to find the Genshin window handle" };
        return false;
    }
    if (!getGengshinImpactScreen())
    {
        err = { 103, "Failed to capture the Genshin frame" };
        return false;
    }
    return true;
}

bool AutoTrack::getGengshinImpactWnd()
{
    TianLi::Genshin::get_genshin_handle(genshin_handle);
    if (genshin_handle.config.frame_source->mode != tianli::frame::frame_source::source_mode::handle)
    {
        return true;
    }
    if (genshin_handle.handle == NULL)
    {
        err = { 10, "Invalid handle or the target window does not exist" };
        return false;
    }

    genshin_handle.config.frame_source->set_capture_handle(genshin_handle.handle);

    return true;
}

bool AutoTrack::getGengshinImpactScreen()
{
    TianLi::Genshin::get_genshin_screen(genshin_handle, genshin_screen);
    if (genshin_screen.img_screen.empty())
    {
        err = { 433, "Screenshot failed" };
        return false;
    }
    return true;
}

bool AutoTrack::getMiniMapRefMat()
{
    if (genshin_screen.img_screen.empty())
    {
        err = { 104, "Genshin frame is empty before minimap detection" };
        return false;
    }
    if (genshin_minimap.rect_minimap.empty() == false)
    {
        const cv::Rect frame_rect(0, 0, genshin_screen.img_screen.cols, genshin_screen.img_screen.rows);
        if ((genshin_minimap.rect_minimap & frame_rect) != genshin_minimap.rect_minimap)
        {
            err = { 105, "Cached minimap rect is outside the captured frame" };
            return false;
        }
    }
    genshin_minimap.img_minimap = genshin_screen.img_screen(genshin_minimap.rect_minimap);

    if (genshin_handle.config.frame_source->type == tianli::frame::frame_source::source_type::window_graphics || genshin_handle.config.is_force_used_no_alpha)
    {
        genshin_screen.config.is_used_alpha = false;
    }
    else
    {
        genshin_screen.config.is_used_alpha = true;
    }

    // Detect Paimon, then calculate minimap coordinates directly.

    if (TianLi::Genshin::Check::check_paimon(genshin_screen, genshin_paimon) == false)
    {
        err = { 106, "Paimon/minimap HUD was not detected. Make sure the normal in-game HUD is visible" };
        return false;
    }
    if (genshin_paimon.is_visial == false)
    {
        err = { 107, "Paimon icon was not visible in the captured frame" };
        return false;
    }

    genshin_screen.config.rect_paimon = genshin_paimon.rect_paimon;
    genshin_screen.config.is_handle_mode = genshin_paimon.is_handle_mode;
    genshin_screen.config.is_search_mode = genshin_paimon.is_search_mode;

    if (TianLi::Genshin::Cailb::cailb_minimap(genshin_screen, genshin_minimap) == false)
    {
        err = { 108, "Failed to calibrate minimap bounds from the captured frame" };
        return false;
    }

    return true;
}
