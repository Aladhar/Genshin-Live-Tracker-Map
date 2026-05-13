#include "pch.h"
#include "genshin.cailb.minimap.h"
#include <cmath>

namespace
{
    struct template_match_result
    {
        double score = -1.0;
        cv::Point location;
        cv::Size size;
    };

    template_match_result match_template_multiscale(const cv::Mat& source, const cv::Mat& templ)
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

            cv::Mat template_result;
            cv::matchTemplate(source, scaled_template, template_result, cv::TM_CCOEFF_NORMED);

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

    bool match_minimap_cailb(const tianli::global::match_minimap_cailb_params& params, const tianli::global::GenshinScreen& genshin_screen, tianli::global::GenshinMinimapCailb& out_genshin_minimap_cailb)
    {
        auto giMinimapCailbRef = genshin_screen.img_minimap_cailb_maybe;
        auto& rect_origin = genshin_screen.config.rect_minimap_cailb_maybe;
        auto& is_handle_mode = genshin_screen.config.is_handle_mode;

        auto template_not_handle_mode = params.split_minimap_cailb_template[3];
        auto template_handle_mode = params.minimap_cailb_template_handle_mode;

        if (giMinimapCailbRef.empty() || params.minimap_cailb_template_handle_mode.empty())
            return false;
        if (giMinimapCailbRef.cols < params.split_minimap_cailb_template[3].cols || giMinimapCailbRef.rows < params.split_minimap_cailb_template[3].rows)
            return false;

        double check_match_minimap_cailb_param = out_genshin_minimap_cailb.config.check_match_minimap_cailb_params;
        if (genshin_screen.config.is_used_alpha == false)
        {
            cv::cvtColor(genshin_screen.img_minimap_cailb_maybe, giMinimapCailbRef, cv::COLOR_RGBA2GRAY);
            template_not_handle_mode = params.minimap_cailb_template_no_alpha;
            template_handle_mode = params.minimap_cailb_template_no_alpha_handle_mode;
            check_match_minimap_cailb_param = out_genshin_minimap_cailb.config.check_match_minimap_cailb_params_no_alpha;
        }

        std::vector<cv::Mat> split_minimap_cailb;
        cv::split(giMinimapCailbRef, split_minimap_cailb);
        if (split_minimap_cailb.empty())
            return false;

        const auto selected_template = is_handle_mode ? template_handle_mode : template_not_handle_mode;
        const auto match = match_template_multiscale(split_minimap_cailb.back(), selected_template);
        if (match.score < check_match_minimap_cailb_param || match.score >= 0.999999)
        {
            out_genshin_minimap_cailb.is_visial = false;
        }
        else
        {
            out_genshin_minimap_cailb.is_visial = true;
            out_genshin_minimap_cailb.rect_minimap_cailb = cv::Rect(rect_origin.tl() + match.location, match.size);
        }

        return true;
    }

    bool cailb_minimap_impl(const tianli::global::GenshinScreen& genshin_screen, tianli::global::GenshinMinimap& out_genshin_minimap)
    {
        auto& paimon_rect = genshin_screen.config.rect_paimon;
        if (paimon_rect.empty())
            return false;

        auto minimap_rect = genshin_screen.config.is_handle_mode ? genshin_screen.config.rect_minimap_handle : genshin_screen.config.rect_minimap;
        if (genshin_screen.config.is_search_mode)
        {
            static tianli::global::GenshinMinimapCailb genshin_minimap_cailb;
            bool is_find_minimap_cailb = match_minimap_cailb(*genshin_screen.minimap_cailb_params, genshin_screen, genshin_minimap_cailb);
            if (is_find_minimap_cailb == false)
                return false;
            if (genshin_minimap_cailb.is_visial == false)
                return false;

            auto& minimap_cailb_rect = genshin_minimap_cailb.rect_minimap_cailb;
            auto minimap_left = paimon_rect.x + paimon_rect.width / 2;
            auto minimap_right = minimap_cailb_rect.x + minimap_cailb_rect.width / 2;
            auto minimap_top = (paimon_rect.y + minimap_cailb_rect.y) / 2;
            auto minimap_width = minimap_right - minimap_left;
            auto minimap_height = minimap_width;
            auto minimap_bottom = minimap_top + minimap_height;
            minimap_rect = cv::Rect(cv::Point(minimap_left, minimap_top), cv::Point(minimap_right, minimap_bottom));
        }

        const cv::Rect frame_rect(0, 0, genshin_screen.img_screen.cols, genshin_screen.img_screen.rows);
        minimap_rect = minimap_rect & frame_rect;
        if (minimap_rect.empty())
            return false;

        auto minimap_center = cv::Point(minimap_rect.x + (minimap_rect.width) / 2, minimap_rect.y + (minimap_rect.height) / 2);
        out_genshin_minimap.img_minimap = genshin_screen.img_screen(minimap_rect);
        out_genshin_minimap.rect_minimap = minimap_rect;
        out_genshin_minimap.point_minimap_center = minimap_center;

        int Avatar_Rect_x = cvRound(minimap_rect.width * 0.4);
        int Avatar_Rect_y = cvRound(minimap_rect.height * 0.4);
        int Avatar_Rect_w = cvRound(minimap_rect.width * 0.2);
        int Avatar_Rect_h = cvRound(minimap_rect.height * 0.2);

        out_genshin_minimap.rect_avatar = cv::Rect(Avatar_Rect_x, Avatar_Rect_y, Avatar_Rect_w, Avatar_Rect_h);
        out_genshin_minimap.img_avatar = out_genshin_minimap.img_minimap(out_genshin_minimap.rect_avatar);

        int Viewer_Rect_x = cvRound(minimap_rect.width * 0.2);
        int Viewer_Rect_y = cvRound(minimap_rect.height * 0.2);
        int Viewer_Rect_w = cvRound(minimap_rect.width * 0.6);
        int Viewer_Rect_h = cvRound(minimap_rect.height * 0.6);

        out_genshin_minimap.rect_viewer = cv::Rect(Viewer_Rect_x, Viewer_Rect_y, Viewer_Rect_w, Viewer_Rect_h);
        out_genshin_minimap.img_viewer = out_genshin_minimap.img_minimap(out_genshin_minimap.rect_viewer);

        int Stars_Rect_x = cvRound(minimap_rect.width * 0.165);
        int Stars_Rect_y = cvRound(minimap_rect.height * 0.165);
        int Stars_Rect_w = cvRound(minimap_rect.width * 0.67);
        int Stars_Rect_h = cvRound(minimap_rect.height * 0.67);

        out_genshin_minimap.rect_stars = cv::Rect(Stars_Rect_x, Stars_Rect_y, Stars_Rect_w, Stars_Rect_h);
        out_genshin_minimap.img_stars = out_genshin_minimap.img_minimap(out_genshin_minimap.rect_stars);

        return true;
    }
} // namespace

bool TianLi::Genshin::Cailb::cailb_minimap(const tianli::global::GenshinScreen& genshin_screen, tianli::global::GenshinMinimap& out_genshin_minimap)
{
    return cailb_minimap_impl(genshin_screen, out_genshin_minimap);
}
