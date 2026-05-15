from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tracker_core.capture.mac_capture import capture_from_config  # noqa: E402
from tracker_core.localization.template_matcher import localize_minimap  # noqa: E402
from tracker_core.map_data.kongying_loader import KongYingMapData  # noqa: E402
from tracker_core.map_data.map_assets import MapImageAsset  # noqa: E402
from tracker_core.minimap.crop import CropBox, crop_minimap_region  # noqa: E402
from tracker_core.utils.cv_images import read_image_bgr  # noqa: E402
from tracker_core.utils.paths import load_json, resolve_repo_path, write_json  # noqa: E402


class FilteredKongYingMapData:
    def __init__(
        self,
        base: KongYingMapData,
        *,
        regions: set[str],
        asset_names: set[str] | None = None,
        center_tile: tuple[int, int] | None = None,
        tile_radius: int | None = None,
    ) -> None:
        self.base = base
        self.regions = regions
        self.asset_names = asset_names or set()
        self.center_tile = center_tile
        self.tile_radius = tile_radius

    def list_regions(self) -> list[str]:
        return self.base.list_regions()

    def list_match_image_asset_records(
        self,
        categories: set[str] | None = None,
        exclude_keywords: tuple[str, ...] = ("outline", "overlay"),
    ) -> list[MapImageAsset]:
        assets = self.base.list_match_image_asset_records(categories=categories, exclude_keywords=exclude_keywords)
        filtered = []
        for asset in assets:
            if self.regions and asset.region not in self.regions:
                continue
            if self.asset_names and asset.asset_name not in self.asset_names:
                continue
            if self.center_tile and self.tile_radius is not None:
                if asset.tile_x is None or asset.tile_y is None:
                    continue
                if abs(asset.tile_x - self.center_tile[0]) > self.tile_radius:
                    continue
                if abs(asset.tile_y - self.center_tile[1]) > self.tile_radius:
                    continue
            filtered.append(asset)
        return filtered


def load_frame_from_image(path: Path):
    frame = read_image_bgr(path)
    if frame is None:
        raise RuntimeError(f"Could not load frame image: {path}")
    return frame


def frontend_map_position(result_dict: dict[str, Any], config: dict[str, Any]) -> dict[str, float] | None:
    if not result_dict.get("accepted"):
        return None

    tile_x = result_dict.get("tile_x")
    tile_y = result_dict.get("tile_y")
    local_x = result_dict.get("local_x")
    local_y = result_dict.get("local_y")
    map_width = result_dict.get("map_width")
    map_height = result_dict.get("map_height")
    if None in (tile_x, tile_y, local_x, local_y, map_width, map_height):
        x = result_dict.get("x")
        y = result_dict.get("y")
        return {"lat": x, "lng": y} if x is not None and y is not None else None

    tile_unit = float(config.get("frontend_tile_unit", 1024))
    lat = float(tile_x) * tile_unit + float(local_x) * tile_unit / float(map_width)
    lng = float(tile_y) * tile_unit + float(local_y) * tile_unit / float(map_height)
    return {"lat": lat, "lng": lng}

Genshin Live Tracker & Map where is LocalHost UI Map being updated from trackercapture from MAC


def payload_from_result(
    result,
    *,
    config: dict[str, Any],
    crop_box: CropBox,
    frame_source: str,
    frame_shape: tuple[int, ...],
) -> dict[str, Any]:
    result_dict = result.to_dict()
    accepted = bool(result_dict.get("accepted"))
    map_position = frontend_map_position(result_dict, config)
    return {
        "schema_version": 1,
        "platform": "mac",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "frame_source": frame_source,
        "frame_shape": list(frame_shape),
        "crop_box": crop_box.to_dict(),
        "accepted": accepted,
        "map_position": map_position,
        "result": result_dict,
    }


def write_latest_payload(config: dict[str, Any], payload: dict[str, Any]) -> None:
    output_path = config.get("latest_output_path")
    if not output_path:
        return
    write_json(output_path, payload)


def run_once(
    config: dict[str, Any],
    data: KongYingMapData,
    *,
    frame_path: str | None = None,
    center_tile: tuple[int, int] | None = None,
) -> tuple[dict[str, Any], tuple[int, int] | None]:
    if frame_path:
        frame = load_frame_from_image(resolve_repo_path(frame_path))
        frame_source = frame_path
    else:
        frame = capture_from_config(config)
        frame_source = "live_screen"

    crop, crop_box = crop_minimap_region(frame, config)
    tile_radius = int(config.get("nearby_tile_radius", 1)) if center_tile else None
    initial_asset_names = set(str(name) for name in config.get("initial_tile_names", []) if str(name).strip())
    filtered_data = FilteredKongYingMapData(
        data,
        regions=set(config.get("match_regions", ["MainMap"])),
        asset_names=None if center_tile else initial_asset_names,
        center_tile=center_tile,
        tile_radius=tile_radius,
    )
    result = localize_minimap(
        crop,
        kongying_data=filtered_data,
        max_assets=0,
        debug_output_enabled=bool(config.get("debug_output_enabled", True)),
        debug_dir=config.get("debug_output_dir", "debug_output/mac"),
        exclude_keywords=tuple(config.get("match_exclude_keywords", ["outline", "overlay"])),
        scales=tuple(float(value) for value in config.get("match_scales", [0.7, 0.8, 0.9])),
        min_confidence=float(config.get("min_match_confidence", 0.7)),
        min_score_margin=float(config.get("min_match_score_margin", 0.1)),
        mask_radius_ratio=float(config.get("match_mask_radius_ratio", 0.48)),
        inner_exclusion_ratio=float(config.get("match_inner_exclusion_ratio", 0.13)),
        preprocess_mode=str(config.get("match_preprocess_mode", "raw_gray")),
        method_name=str(config.get("match_method", "sqdiff_normed")),
    )
    payload = payload_from_result(result, config=config, crop_box=crop_box, frame_source=frame_source, frame_shape=frame.shape)
    write_latest_payload(config, payload)

    result_dict = result.to_dict()
    next_center_tile = center_tile
    if result_dict.get("accepted") and result_dict.get("tile_x") is not None and result_dict.get("tile_y") is not None:
        next_center_tile = (int(result_dict["tile_x"]), int(result_dict["tile_y"]))
    return payload, next_center_tile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the fast Mac Genshin minimap tracker.")
    parser.add_argument("--config", default="config/tracker_mac.json", help="Mac tracker config path.")
    parser.add_argument("--frame", default=None, help="Debug screenshot path. If omitted, captures the screen.")
    parser.add_argument("--once", action="store_true", help="Run one tracker update.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_json(args.config)
    data = KongYingMapData(config.get("kongying_manifest", "data/kongying/manifest.json"))
    interval_seconds = float(config.get("tracker_interval_seconds", 0.75))
    center_tile: tuple[int, int] | None = None

    while True:
        payload, center_tile = run_once(config, data, frame_path=args.frame, center_tile=center_tile)
        print(json.dumps(payload, indent=2, ensure_ascii=False), flush=True)
        if args.once:
            return 0 if payload.get("accepted") else 1
        time.sleep(interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
