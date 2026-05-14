#include "capture.macos_bridge.h"

#ifdef __APPLE__

#include <algorithm>
#include <cctype>
#include <cmath>
#include <dlfcn.h>

#import <AppKit/AppKit.h>
#import <CoreGraphics/CoreGraphics.h>
#import <CoreVideo/CoreVideo.h>
#import <Foundation/Foundation.h>
#import <ScreenCaptureKit/ScreenCaptureKit.h>

namespace tianli::frame::capture::macos
{
    namespace
    {
        std::string cf_string_to_string(CFStringRef value)
        {
            if (value == nullptr)
                return {};

            char buffer[1024] = {};
            if (CFStringGetCString(value, buffer, sizeof(buffer), kCFStringEncodingUTF8))
                return buffer;
            return {};
        }

        bool cf_bool_value(CFTypeRef value)
        {
            return value == kCFBooleanTrue;
        }

        int cf_int_value(CFTypeRef value)
        {
            if (value == nullptr || CFGetTypeID(value) != CFNumberGetTypeID())
                return 0;
            int result = 0;
            CFNumberGetValue(static_cast<CFNumberRef>(value), kCFNumberIntType, &result);
            return result;
        }

        cv::Rect rect_from_dictionary(CFDictionaryRef bounds)
        {
            if (bounds == nullptr)
                return {};

            CGRect cg_rect = CGRectZero;
            if (!CGRectMakeWithDictionaryRepresentation(bounds, &cg_rect))
                return {};

            return {
                static_cast<int>(std::lround(cg_rect.origin.x)),
                static_cast<int>(std::lround(cg_rect.origin.y)),
                static_cast<int>(std::lround(cg_rect.size.width)),
                static_cast<int>(std::lround(cg_rect.size.height)),
            };
        }

        std::string lowercase_ascii(std::string value)
        {
            std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) {
                return static_cast<char>(std::tolower(ch));
            });
            return value;
        }

        bool contains(const std::string& text, const std::string& token)
        {
            return text.find(token) != std::string::npos;
        }

        bool is_genshin_candidate(const window_info& window)
        {
            const auto haystack = lowercase_ascii(window.owner_name + " " + window.title);
            return contains(haystack, "genshin")
                || contains(haystack, "genshinimpact")
                || contains(haystack, "yuanshen")
                || contains(window.owner_name, "原神")
                || contains(window.title, "原神");
        }

        bool is_capture_sized(const window_info& window)
        {
            return window.bounds.width >= 480 && window.bounds.height >= 360;
        }

        window_info window_info_from_dictionary(CFDictionaryRef dictionary)
        {
            window_info info;
            if (dictionary == nullptr)
                return info;

            info.window_id = static_cast<uint32_t>(cf_int_value(CFDictionaryGetValue(dictionary, kCGWindowNumber)));
            info.owner_pid = cf_int_value(CFDictionaryGetValue(dictionary, kCGWindowOwnerPID));
            info.owner_name = cf_string_to_string(static_cast<CFStringRef>(CFDictionaryGetValue(dictionary, kCGWindowOwnerName)));
            info.title = cf_string_to_string(static_cast<CFStringRef>(CFDictionaryGetValue(dictionary, kCGWindowName)));
            info.bounds = rect_from_dictionary(static_cast<CFDictionaryRef>(CFDictionaryGetValue(dictionary, kCGWindowBounds)));
            info.on_screen = cf_bool_value(CFDictionaryGetValue(dictionary, kCGWindowIsOnscreen));
            info.scale = NSScreen.mainScreen ? NSScreen.mainScreen.backingScaleFactor : 1.0;
            return info;
        }

        bool cg_image_to_mat(CGImageRef image, cv::Mat& frame)
        {
            frame.release();
            if (image == nullptr)
                return false;

            const auto width = static_cast<int>(CGImageGetWidth(image));
            const auto height = static_cast<int>(CGImageGetHeight(image));
            if (width <= 0 || height <= 0)
                return false;

            cv::Mat bgra(height, width, CV_8UC4);
            CGColorSpaceRef color_space = CGColorSpaceCreateDeviceRGB();
            CGContextRef context = CGBitmapContextCreate(
                bgra.data,
                static_cast<size_t>(width),
                static_cast<size_t>(height),
                8,
                bgra.step,
                color_space,
                kCGImageAlphaPremultipliedFirst | kCGBitmapByteOrder32Host);

            if (context == nullptr)
            {
                CGColorSpaceRelease(color_space);
                return false;
            }

            CGContextDrawImage(context, CGRectMake(0, 0, width, height), image);
            CGContextRelease(context);
            CGColorSpaceRelease(color_space);

            frame = bgra;
            return !frame.empty();
        }

        using CGWindowListCreateImageFn = CGImageRef (*)(CGRect, CGWindowListOption, CGWindowID, CGWindowImageOption);

        CGWindowListCreateImageFn legacy_window_image_function()
        {
            return reinterpret_cast<CGWindowListCreateImageFn>(dlsym(RTLD_DEFAULT, "CGWindowListCreateImage"));
        }

        bool capture_with_legacy_core_graphics(uint32_t window_id, cv::Mat& frame)
        {
            auto create_image = legacy_window_image_function();
            if (create_image == nullptr)
                return false;

            const auto options = static_cast<CGWindowImageOption>(
                kCGWindowImageBoundsIgnoreFraming | kCGWindowImageBestResolution);
            CGImageRef image = create_image(
                CGRectNull,
                kCGWindowListOptionIncludingWindow,
                static_cast<CGWindowID>(window_id),
                options);
            if (image == nullptr)
                return false;

            const bool result = cg_image_to_mat(image, frame);
            CGImageRelease(image);
            return result;
        }

        bool capture_display_with_legacy_core_graphics(cv::Mat& frame)
        {
            auto create_image = legacy_window_image_function();
            if (create_image == nullptr)
                return false;

            CGImageRef image = create_image(
                CGRectInfinite,
                kCGWindowListOptionOnScreenOnly,
                kCGNullWindowID,
                kCGWindowImageBestResolution);
            if (image == nullptr)
                return false;

            const bool result = cg_image_to_mat(image, frame);
            CGImageRelease(image);
            return result;
        }

        SCWindow* find_sc_window(uint32_t window_id) API_AVAILABLE(macos(12.3))
        {
            __block SCWindow* result = nil;
            __block bool complete = false;
            dispatch_semaphore_t semaphore = dispatch_semaphore_create(0);

            [SCShareableContent getShareableContentExcludingDesktopWindows:YES
                                                        onScreenWindowsOnly:YES
                                                         completionHandler:^(SCShareableContent* content, NSError* error) {
                                                             if (content != nil && error == nil)
                                                             {
                                                                 for (SCWindow* window in content.windows)
                                                                 {
                                                                     if (window.windowID == window_id)
                                                                     {
                                                                         result = window;
                                                                         break;
                                                                     }
                                                                 }
                                                             }
                                                             complete = true;
                                                             dispatch_semaphore_signal(semaphore);
                                                         }];

            dispatch_time_t timeout = dispatch_time(DISPATCH_TIME_NOW, 5 * NSEC_PER_SEC);
            if (dispatch_semaphore_wait(semaphore, timeout) != 0 || !complete)
                return nil;

            return result;
        }

        bool capture_window_with_screencapturekit(uint32_t window_id, cv::Mat& frame)
        {
            frame.release();
            if (@available(macOS 14.0, *))
            {
                SCWindow* window = find_sc_window(window_id);
                if (window == nil)
                    return false;

                SCContentFilter* filter = [[SCContentFilter alloc] initWithDesktopIndependentWindow:window];
                SCStreamConfiguration* config = [[SCStreamConfiguration alloc] init];
                const CGRect content_rect = filter.contentRect;
                const CGFloat point_scale = filter.pointPixelScale > 0 ? filter.pointPixelScale : NSScreen.mainScreen.backingScaleFactor;
                config.width = static_cast<size_t>(std::max<CGFloat>(1, std::ceil(content_rect.size.width * point_scale)));
                config.height = static_cast<size_t>(std::max<CGFloat>(1, std::ceil(content_rect.size.height * point_scale)));
                config.pixelFormat = kCVPixelFormatType_32BGRA;
                config.showsCursor = NO;
                config.queueDepth = 1;
                config.ignoreShadowsSingleWindow = YES;
                config.shouldBeOpaque = YES;

                __block CGImageRef captured_image = nullptr;
                __block bool complete = false;
                dispatch_semaphore_t semaphore = dispatch_semaphore_create(0);

                [SCScreenshotManager captureImageWithFilter:filter
                                               configuration:config
                                           completionHandler:^(CGImageRef image, NSError* error) {
                                               if (image != nullptr && error == nil)
                                                   captured_image = CGImageRetain(image);
                                               complete = true;
                                               dispatch_semaphore_signal(semaphore);
                                           }];

                dispatch_time_t timeout = dispatch_time(DISPATCH_TIME_NOW, 5 * NSEC_PER_SEC);
                if (dispatch_semaphore_wait(semaphore, timeout) != 0 || !complete || captured_image == nullptr)
                    return false;

                const bool result = cg_image_to_mat(captured_image, frame);
                CGImageRelease(captured_image);
                return result;
            }
            return false;
        }
    } // namespace

    std::vector<window_info> list_windows()
    {
        std::vector<window_info> windows;
        CFArrayRef window_list = CGWindowListCopyWindowInfo(
            static_cast<CGWindowListOption>(kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements),
            kCGNullWindowID);
        if (window_list == nullptr)
            return windows;

        const auto count = CFArrayGetCount(window_list);
        for (CFIndex index = 0; index < count; ++index)
        {
            auto dictionary = static_cast<CFDictionaryRef>(CFArrayGetValueAtIndex(window_list, index));
            auto info = window_info_from_dictionary(dictionary);
            const int layer = cf_int_value(CFDictionaryGetValue(dictionary, kCGWindowLayer));
            if (info.window_id != 0 && info.on_screen && layer == 0 && is_capture_sized(info))
                windows.push_back(info);
        }

        CFRelease(window_list);
        return windows;
    }

    bool find_genshin_window(window_info& window)
    {
        const auto windows = list_windows();
        auto best = windows.end();
        for (auto it = windows.begin(); it != windows.end(); ++it)
        {
            if (!is_genshin_candidate(*it))
                continue;
            if (best == windows.end() || it->bounds.area() > best->bounds.area())
                best = it;
        }

        if (best == windows.end())
            return false;

        window = *best;
        return true;
    }

    bool query_window(uint32_t window_id, window_info& window)
    {
        const auto windows = list_windows();
        auto it = std::find_if(windows.begin(), windows.end(), [window_id](const window_info& info) {
            return info.window_id == window_id;
        });
        if (it == windows.end())
            return false;
        window = *it;
        return true;
    }

    bool has_screen_capture_permission()
    {
        return CGPreflightScreenCaptureAccess();
    }

    bool request_screen_capture_permission()
    {
        return CGRequestScreenCaptureAccess();
    }

    bool capture_window(uint32_t window_id, cv::Mat& frame)
    {
        if (window_id == 0)
            return false;

        if (capture_with_legacy_core_graphics(window_id, frame))
            return true;

        return capture_window_with_screencapturekit(window_id, frame);
    }

    bool capture_main_display(cv::Mat& frame)
    {
        return capture_display_with_legacy_core_graphics(frame);
    }
} // namespace tianli::frame::capture::macos

#else

namespace tianli::frame::capture::macos
{
    std::vector<window_info> list_windows() { return {}; }
    bool find_genshin_window(window_info&) { return false; }
    bool query_window(uint32_t, window_info&) { return false; }
    bool has_screen_capture_permission() { return false; }
    bool request_screen_capture_permission() { return false; }
    bool capture_window(uint32_t, cv::Mat&) { return false; }
    bool capture_main_display(cv::Mat&) { return false; }
} // namespace tianli::frame::capture::macos

#endif
