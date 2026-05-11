#pragma once

namespace TianLi::Match
{
    struct template_match_detection
    {
        cv::Rect rect;
        double score = 0.0;
        double scale = 1.0;
    };

    struct template_match_options
    {
        double threshold = 0.82;
        double min_scale = 0.80;
        double max_scale = 1.25;
        double scale_step = 0.05;
        double max_iou = 0.25;
        int max_matches = 8;
    };

    inline cv::Mat to_gray_image(const cv::Mat& image)
    {
        if (image.empty())
            return {};
        if (image.channels() == 1)
            return image.clone();

        cv::Mat gray;
        switch (image.channels())
        {
            case 4: cv::cvtColor(image, gray, cv::COLOR_BGRA2GRAY); break;
            case 3: cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY); break;
            default: image.copyTo(gray); break;
        }
        return gray;
    }

    inline cv::Mat make_alpha_mask(const cv::Mat& image)
    {
        if (image.channels() != 4)
            return {};

        std::vector<cv::Mat> channels;
        cv::split(image, channels);
        if (channels.size() < 4)
            return {};

        cv::Mat mask;
        cv::threshold(channels[3], mask, 0, 255, cv::THRESH_BINARY);
        return mask;
    }

    inline double rect_iou(const cv::Rect& a, const cv::Rect& b)
    {
        const auto intersection = (a & b).area();
        if (intersection <= 0)
            return 0.0;
        const auto union_area = a.area() + b.area() - intersection;
        if (union_area <= 0)
            return 0.0;
        return static_cast<double>(intersection) / static_cast<double>(union_area);
    }

    inline std::vector<template_match_detection> detect_template_multiscale(const cv::Mat& roi, const cv::Mat& templ, const template_match_options& options = {})
    {
        std::vector<template_match_detection> detections;
        if (roi.empty() || templ.empty())
            return detections;

        const cv::Mat roi_gray = to_gray_image(roi);
        const cv::Mat templ_gray = to_gray_image(templ);
        const cv::Mat templ_mask = make_alpha_mask(templ);

        for (double scale = options.min_scale; scale <= options.max_scale + 1e-6; scale += options.scale_step)
        {
            const auto scaled_width = std::max(1, cvRound(templ_gray.cols * scale));
            const auto scaled_height = std::max(1, cvRound(templ_gray.rows * scale));
            if (scaled_width > roi_gray.cols || scaled_height > roi_gray.rows)
                continue;

            cv::Mat scaled_template;
            cv::resize(templ_gray, scaled_template, cv::Size(scaled_width, scaled_height), 0, 0, cv::INTER_LINEAR);

            cv::Mat scaled_mask;
            if (!templ_mask.empty())
            {
                cv::resize(templ_mask, scaled_mask, cv::Size(scaled_width, scaled_height), 0, 0, cv::INTER_NEAREST);
                cv::threshold(scaled_mask, scaled_mask, 0, 255, cv::THRESH_BINARY);
                if (cv::countNonZero(scaled_mask) == 0)
                    continue;
            }

            cv::Mat result;
            const auto method = scaled_mask.empty() ? cv::TM_CCOEFF_NORMED : cv::TM_CCORR_NORMED;
            if (scaled_mask.empty())
                cv::matchTemplate(roi_gray, scaled_template, result, method);
            else
                cv::matchTemplate(roi_gray, scaled_template, result, method, scaled_mask);

            for (int matched = 0; matched < options.max_matches; ++matched)
            {
                double min_val = 0.0;
                double max_val = 0.0;
                cv::Point min_loc;
                cv::Point max_loc;
                cv::minMaxLoc(result, &min_val, &max_val, &min_loc, &max_loc);
                if (max_val < options.threshold)
                    break;

                detections.push_back({
                    cv::Rect(max_loc.x, max_loc.y, scaled_template.cols, scaled_template.rows),
                    max_val,
                    scale,
                });

                result(cv::Rect(max_loc.x, max_loc.y, scaled_template.cols, scaled_template.rows)) = 0;
            }
        }

        std::sort(detections.begin(), detections.end(), [](const auto& lhs, const auto& rhs) {
            if (lhs.score == rhs.score)
                return lhs.rect.area() < rhs.rect.area();
            return lhs.score > rhs.score;
        });

        std::vector<template_match_detection> filtered;
        filtered.reserve(detections.size());
        for (const auto& detection : detections)
        {
            const auto overlapped = std::any_of(filtered.begin(), filtered.end(), [&](const auto& accepted) { return rect_iou(accepted.rect, detection.rect) > options.max_iou; });
            if (overlapped)
                continue;
            filtered.push_back(detection);
            if (filtered.size() >= static_cast<size_t>(options.max_matches))
                break;
        }

        std::sort(filtered.begin(), filtered.end(), [](const auto& lhs, const auto& rhs) {
            if (lhs.rect.y == rhs.rect.y)
                return lhs.rect.x < rhs.rect.x;
            return lhs.rect.y < rhs.rect.y;
        });

        return filtered;
    }
} // namespace TianLi::Match
