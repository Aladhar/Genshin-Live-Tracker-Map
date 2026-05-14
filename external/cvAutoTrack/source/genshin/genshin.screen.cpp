#include "pch.h"
#include "genshin.screen.h"
#include "frame/frame.include.h"
#include <chrono>
using namespace std::chrono_literals;

namespace
{
    void clear_screen_images(tianli::global::GenshinScreen& screen)
    {
        screen.img_screen.release();
        screen.img_paimon_maybe.release();
        screen.img_paimon.release();
        screen.img_minimap_cailb_maybe.release();
        screen.img_minimap_cailb.release();
        screen.img_minimap_maybe.release();
        screen.img_minimap.release();
        screen.img_avatar_maybe.release();
        screen.img_avatar.release();
        screen.img_uid_maybe.release();
        screen.img_uid.release();
        screen.img_star_maybe.release();
        screen.img_star.release();
        screen.img_map_flag_maybe.release();
        screen.img_map_flag.release();
        screen.img_map_flag_icon_maybe.release();
        screen.img_map_flag_icon.release();
        screen.img_left_give_items_maybe.release();
        screen.img_left_give_items.release();
        screen.img_right_pick_items_maybe.release();
        screen.img_right_pick_items.release();
        screen.img_hp_maybe.release();
        screen.img_hp.release();
    }
}

void TianLi::Genshin::get_genshin_screen(const tianli::global::GenshinHandle& genshin_handle, tianli::global::GenshinScreen& out_genshin_screen)
{
    // auto& giHandle = genshin_handle.handle;
    auto& giRect = genshin_handle.rect;
    auto& giRectClient = genshin_handle.rect_client;
    // auto& giScale = genshin_handle.scale;
    auto& giFrame = out_genshin_screen.img_screen;

    auto now_time = std::chrono::system_clock::now();
    if (now_time - out_genshin_screen.last_time > 20ms || giFrame.empty())
    {
        cv::Mat fresh_frame;
        if (genshin_handle.config.frame_source->get_frame(fresh_frame) == false || fresh_frame.empty())
        {
            clear_screen_images(out_genshin_screen);
            return;
        }

        giFrame = fresh_frame;
        out_genshin_screen.last_time = now_time;
    }

    {
        if (giFrame.empty())
            return;
        cv::resize(giFrame, giFrame, genshin_handle.size_frame);

        out_genshin_screen.rect_client = cv::Rect(giRect.left, giRect.top, giRectClient.right - giRectClient.left, giRectClient.bottom - giRectClient.top);

        // 获取maybe区域
        out_genshin_screen.img_paimon_maybe = giFrame(genshin_handle.rect_paimon_maybe);
        out_genshin_screen.img_minimap_cailb_maybe = giFrame(genshin_handle.rect_minimap_cailb_maybe);
        out_genshin_screen.img_minimap_maybe = giFrame(genshin_handle.rect_minimap_maybe);
        out_genshin_screen.img_uid_maybe = giFrame(genshin_handle.rect_uid_maybe);
        out_genshin_screen.img_left_give_items_maybe = giFrame(genshin_handle.rect_left_give_items_maybe);
        out_genshin_screen.img_right_pick_items_maybe = giFrame(genshin_handle.rect_right_pick_items_maybe);
        out_genshin_screen.img_left_give_items = giFrame(genshin_handle.rect_left_give_items);
        out_genshin_screen.img_right_pick_items = giFrame(genshin_handle.rect_right_pick_items);

        out_genshin_screen.config.rect_paimon_maybe = genshin_handle.rect_paimon_maybe;
        out_genshin_screen.config.rect_minimap_cailb_maybe = genshin_handle.rect_minimap_cailb_maybe;
        out_genshin_screen.config.rect_minimap_maybe = genshin_handle.rect_minimap_maybe;

        out_genshin_screen.img_uid = giFrame(genshin_handle.rect_uid);
    }
}
