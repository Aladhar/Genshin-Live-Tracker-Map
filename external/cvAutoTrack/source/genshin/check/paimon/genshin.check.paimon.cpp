#include "pch.h"
#include "genshin.check.paimon.h"
#include <cmath>
#include <limits>

namespace
{
    cv::Vec3b get_point_vec3b(const cv::Mat& mat, int x, int y, bool is_need_cvt)
    {
        if (is_need_cvt)
        {
            auto screen_color_v4 = mat.at<cv::Vec4b>(y, x);
            return cv::Vec3b(screen_color_v4[0], screen_color_v4[1], screen_color_v4[2]);
        }
        return mat.at<cv::Vec3b>(y, x);
    }

    bool rect_contains_keypoints(const cv::Mat& mat, const cv::Rect& roi, const std::vector<std::pair<cv::Point, cv::Vec3b>>& paimon_keys)
    {
        if (mat.empty())
            return false;

        for (const auto& paimon_key : paimon_keys)
        {
            const auto point = roi.tl() + paimon_key.first;
            if (point.x < 0 || point.y < 0 || point.x >= mat.cols || point.y >= mat.rows)
                return false;
        }
        return true;
    }

    double cala_keypoint_diff(const cv::Mat& mat, const cv::Rect& roi, const std::vector<std::pair<cv::Point, cv::Vec3b>>& paimon_keys, bool is_need_cvt)
    {
        double paimon_check_diff = 0;
        for (auto& paimon_key : paimon_keys)
        {
            auto& [_point, color] = paimon_key;
            auto [x, y] = roi.tl() + _point;
            auto screen_color = get_point_vec3b(mat, x, y, is_need_cvt);
            auto color_diff = cv::norm(screen_color, color);
            paimon_check_diff = paimon_check_diff + color_diff / paimon_keys.size();
        }
        return paimon_check_diff;
    }

    struct template_match_result
    {
        double score = -1.0;
        cv::Point location;
        cv::Size size;
    };

    cv::Mat make_compatible_mask(const cv::Mat& mask, const cv::Size& size, int source_channels)
    {
        if (mask.empty())
            return {};

        cv::Mat resized_mask;
        cv::resize(mask, resized_mask, size, 0, 0, cv::INTER_NEAREST);
        if (resized_mask.channels() == source_channels || resized_mask.channels() == 1)
            return resized_mask;

        std::vector<cv::Mat> channels;
        cv::split(resized_mask, channels);
        return channels.empty() ? cv::Mat() : channels.back();
    }

    template_match_result match_template_multiscale(const cv::Mat& source, const cv::Mat& templ, const cv::Mat& mask = cv::Mat())
    {
        template_match_result best;
        if (source.empty() || templ.empty())
            return best;

        const std::vector<double> scales = { 1.00, 0.95, 1.05, 0.90, 1.10, 0.85, 1.15, 0.80, 1.20 };
        for (const auto scale : scales)
        {
            cv::Mat scaled_template;
            cv::resize(templ, scaled_template, cv::Size(), scale, scale, cv::INTER_AREA);
            if (scaled_template.empty() || scaled_template.cols < 4 || scaled_template.rows < 4)
                continue;
            if (source.cols < scaled_template.cols || source.rows < scaled_template.rows)
                continue;

            auto scaled_mask = make_compatible_mask(mask, scaled_template.size(), source.channels());

            cv::Mat template_result;
            if (scaled_mask.empty())
                cv::matchTemplate(source, scaled_template, template_result, cv::TM_CCOEFF_NORMED);
            else
                cv::matchTemplate(source, scaled_template, template_result, cv::TM_CCOEFF_NORMED, scaled_mask);

            double min_val = 0.0;
            double max_val = 0.0;
            cv::Point min_loc;
            cv::Point max_loc;
            cv::minMaxLoc(template_result, &min_val, &max_val, &min_loc, &max_loc);
            if (!std::isfinite(max_val))
                continue;
            if (max_val > best.score)
            {
                best.score = max_val;
                best.location = max_loc;
                best.size = scaled_template.size();
            }
        }
        return best;
    }

    bool check_paimon_search_impl(const tianli::global::check_paimon_search_params& params, const tianli::global::GenshinScreen& genshin_screen, tianli::global::GenshinPaimon& out_genshin_paimon)
    {
        auto giPaimonRef = genshin_screen.img_paimon_maybe;
        auto& rect_origin = genshin_screen.config.rect_paimon_maybe;
        auto template_not_handle_mode = params.paimon_template;
        auto template_handle_mode = params.paimon_template_handle_mode;
        auto template_mask_not_handle_mode = cv::Mat();
        auto template_mask_handle_mode = cv::Mat();

        if (giPaimonRef.empty() || params.paimon_template_handle_mode.empty())
            return false;
        if (giPaimonRef.cols < params.paimon_template.cols || giPaimonRef.rows < params.paimon_template.rows)
            return false;

        double check_match_paimon_param = out_genshin_paimon.config.check_match_paimon_params;
        if (genshin_screen.config.is_used_alpha == false)
        {
            cv::cvtColor(genshin_screen.img_paimon_maybe, giPaimonRef, cv::COLOR_RGBA2GRAY);
            template_not_handle_mode = params.paimon_template_no_alpha;
            template_handle_mode = params.paimon_template_no_alpha_handle_mode;
            template_mask_not_handle_mode = params.paimon_template;
            template_mask_handle_mode = params.paimon_template_handle_mode;
            check_match_paimon_param = out_genshin_paimon.config.check_match_paimon_params_no_alpha;
        }

        std::vector<cv::Mat> split_paimon;
        cv::split(giPaimonRef, split_paimon);
        if (split_paimon.empty())
            return false;

        const auto paimon_match = match_template_multiscale(split_paimon.back(), template_not_handle_mode, template_mask_not_handle_mode);
        if (paimon_match.score >= check_match_paimon_param && paimon_match.score < 0.999999)
        {
            out_genshin_paimon.is_handle_mode = false;
            out_genshin_paimon.is_visial = true;
            out_genshin_paimon.rect_paimon = cv::Rect(rect_origin.tl() + paimon_match.location, paimon_match.size);
            out_genshin_paimon.is_search_mode = true;
            out_genshin_paimon.config.rect_paimon_keypoint = out_genshin_paimon.rect_paimon;
            return true;
        }
        if (paimon_match.score <= 0.2)
        {
            out_genshin_paimon.is_visial = false;
            return false;
        }

        const auto paimon_handle_match = match_template_multiscale(split_paimon.back(), template_handle_mode, template_mask_handle_mode);
        if (paimon_handle_match.score > check_match_paimon_param)
        {
            out_genshin_paimon.is_handle_mode = true;
            out_genshin_paimon.is_visial = true;
            out_genshin_paimon.rect_paimon = cv::Rect(rect_origin.tl() + paimon_handle_match.location, paimon_handle_match.size);
            out_genshin_paimon.is_search_mode = true;
            out_genshin_paimon.config.rect_paimon_keypoint_handle = out_genshin_paimon.rect_paimon;
            return true;
        }

        out_genshin_paimon.is_visial = false;
        return false;
    }

    bool check_paimon_impl(const tianli::global::GenshinScreen& genshin_screen, tianli::global::GenshinPaimon& out_genshin_paimon)
    {
        auto paimon_keys = out_genshin_paimon.config.paimon_check_vec;
        auto paimon_handle_keys = out_genshin_paimon.config.paimon_handle_check_vec;
        auto rect_keypoint = out_genshin_paimon.config.rect_paimon_keypoint;
        auto rect_keypoint_handle = out_genshin_paimon.config.rect_paimon_keypoint_handle;
        auto giPaimonRef = genshin_screen.img_paimon_maybe;
        if (giPaimonRef.empty())
            return false;

        bool is_need_cvt = giPaimonRef.channels() == 4;

        double paimon_check_diff = rect_contains_keypoints(giPaimonRef, rect_keypoint, paimon_keys)
            ? cala_keypoint_diff(giPaimonRef, rect_keypoint, paimon_keys, is_need_cvt)
            : std::numeric_limits<double>::max();
        if (paimon_check_diff < out_genshin_paimon.config.check_match_paimon_keypoint_params)
        {
            out_genshin_paimon.is_handle_mode = false;
            out_genshin_paimon.is_visial = true;
            out_genshin_paimon.rect_paimon = out_genshin_paimon.config.rect_paimon_keypoint;
            return true;
        }

        double paimon_handle_check_diff = rect_contains_keypoints(giPaimonRef, rect_keypoint_handle, paimon_handle_keys)
            ? cala_keypoint_diff(giPaimonRef, rect_keypoint_handle, paimon_handle_keys, is_need_cvt)
            : std::numeric_limits<double>::max();
        if (paimon_handle_check_diff < out_genshin_paimon.config.check_match_paimon_keypoint_params)
        {
            out_genshin_paimon.is_handle_mode = true;
            out_genshin_paimon.is_visial = true;
            out_genshin_paimon.rect_paimon = out_genshin_paimon.config.rect_paimon_keypoint_handle;
            return true;
        }

        return check_paimon_search_impl(*genshin_screen.paimon_search_params, genshin_screen, out_genshin_paimon);
    }
} // namespace

bool TianLi::Genshin::Check::check_paimon(const tianli::global::GenshinScreen& genshin_screen, tianli::global::GenshinPaimon& out_genshin_paimon)
{
    return check_paimon_impl(genshin_screen, out_genshin_paimon);
}
