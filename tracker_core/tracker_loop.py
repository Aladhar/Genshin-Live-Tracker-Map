from __future__ import annotations

import argparse
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tracker_core.localization.template_matcher import localize_minimap
from tracker_core.map_data.kongying_loader import KongYingMapData
from tracker_core.map_data.map_assets import MapImageAsset
from tracker_core.minimap.crop import crop_minimap_region
from tracker_core.utils.paths import load_json, resolve_repo_path


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
        assets = self.base.list_match_image_asset_records(
            categories=categories,
            exclude_keywords=exclude_keywords,
        )
        filtered: list[MapImageAsset] = []
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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def choose_capture(config: dict[str, Any]):
    configured_platform = str(config.get("platform", "")).lower()
    capture_backend = str(config.get("capture_backend", "")).lower()

    is_mac = (
        configured_platform == "mac"
        or capture_backend in {"window", "screencapture", "mss", "pillow"}
        or platform.system().lower() == "darwin"
    )

    if is_mac:
        from tracker_core.capture.mac_capture import capture_from_config
    else:
        from tracker_core.capture.windows_capture import capture_from_config

    return capture_from_config


def best_top_candidate(result: dict[str, Any]) -> dict[str, Any]:
    top_candidates = result.get("top_candidates")
    if not isinstance(top_candidates, list) or not top_candidates:
        return {}
    candidate = top_candidates[0]
    return candidate if isinstance(candidate, dict) else {}


def first_present(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def result_to_frontend_map_position(result: dict[str, Any], config: dict[str, Any]) -> dict[str, float] | None:
    if not result.get("accepted"):
        return None

    return result_to_candidate_map_position(result, config)


def result_to_candidate_map_position(result: dict[str, Any], config: dict[str, Any]) -> dict[str, float] | None:
    if result.get("accepted"):
        local_x_keys = ("local_x", "candidate_local_x")
        local_y_keys = ("local_y", "candidate_local_y")
    else:
        local_x_keys = ("candidate_local_x", "local_x")
        local_y_keys = ("candidate_local_y", "local_y")

    candidate = best_top_candidate(result)
    tile_x = first_present(result.get("tile_x"), candidate.get("tile_x"))
    tile_y = first_present(result.get("tile_y"), candidate.get("tile_y"))
    local_x = first_present(
        *(result.get(key) for key in local_x_keys),
        candidate.get("local_x"),
    )
    local_y = first_present(
        *(result.get(key) for key in local_y_keys),
        candidate.get("local_y"),
    )
    map_width = first_present(result.get("map_width"), candidate.get("map_width"))
    map_height = first_present(result.get("map_height"), candidate.get("map_height"))

    if None not in (tile_x, tile_y, local_x, local_y, map_width, map_height):
        tile_unit = float(config.get("frontend_tile_unit", 1024))
        return {
            "lat": float(tile_x) * tile_unit + float(local_x) * tile_unit / float(map_width),
            "lng": float(tile_y) * tile_unit + float(local_y) * tile_unit / float(map_height),
        }

    x = result.get("x")
    y = result.get("y")
    if x is None or y is None:
        x = result.get("candidate_x")
        y = result.get("candidate_y")
    if x is not None and y is not None:
        return {
            "lat": float(x),
            "lng": float(y),
        }

    return None


def result_to_frontend_payload(
    result: dict[str, Any],
    config: dict[str, Any],
    frame_shape: tuple[int, ...],
    crop_box: Any | None,
    iteration: int | None = None,
) -> dict[str, Any]:
    accepted = bool(result.get("accepted"))
    map_position = result_to_frontend_map_position(result, config)
    candidate_position = result_to_candidate_map_position(result, config)

    return {
        "schema_version": 1,
        "platform": str(config.get("platform", "mac")),
        "timestamp": utc_now(),
        "iteration": iteration,
        "frontend_tile_unit": float(config.get("frontend_tile_unit", 1024)),
        "frame_source": "live_screen",
        "frame_shape": list(frame_shape[:3]),
        "crop_box": crop_box.to_dict() if crop_box is not None else None,
        "accepted": accepted,
        "map_position": map_position,
        "candidate_position": candidate_position,
        "result": result,
    }


def write_latest_payload(payload: dict[str, Any], output_path: str | Path) -> None:
    path = resolve_repo_path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def error_payload(exc: Exception, config: dict[str, Any], iteration: int | None = None) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "platform": str(config.get("platform", "mac")),
        "timestamp": utc_now(),
        "iteration": iteration,
        "frontend_tile_unit": float(config.get("frontend_tile_unit", 1024)),
        "frame_source": "live_screen",
        "frame_shape": None,
        "crop_box": None,
        "accepted": False,
        "map_position": None,
        "candidate_position": None,
        "result": {
            "x": None,
            "y": None,
            "confidence": 0.0,
            "matched_asset": None,
            "accepted": False,
            "error": str(exc),
            "timestamp": utc_now(),
        },
    }


def make_filtered_match_data(
    data: KongYingMapData,
    config: dict[str, Any],
    center_tile: tuple[int, int] | None,
) -> FilteredKongYingMapData:
    initial_asset_names = set(
        str(name)
        for name in config.get("initial_tile_names", [])
        if str(name).strip()
    )
    tile_radius = int(config.get("nearby_tile_radius", 1)) if center_tile else None
    return FilteredKongYingMapData(
        data,
        regions=set(config.get("match_regions", ["MainMap"])),
        asset_names=None if center_tile else initial_asset_names,
        center_tile=center_tile,
        tile_radius=tile_radius,
    )


def match_asset_limit(config: dict[str, Any], center_tile: tuple[int, int] | None) -> int:
    configured_limit = int(config.get("max_match_assets", 0))
    if configured_limit > 0:
        return configured_limit
    if center_tile:
        return 0
    return int(config.get("initial_max_match_assets", 64))


def run_tracker_loop(config_path: str | Path, once: bool = False, count: int | None = None) -> None:
    config = load_json(config_path)
    data = KongYingMapData(config.get("kongying_manifest", "data/kongying/manifest.json"))
    interval_seconds = float(config.get("tracker_interval_seconds", 0.75))
    latest_output_path = config.get("latest_output_path")
    capture_from_config = choose_capture(config)
    center_tile: tuple[int, int] | None = None
    iteration = 0

    while True:
        iteration += 1
        try:
            frame = capture_from_config(config)

            # New auto crop path. This returns both minimap image and crop metadata.
            minimap, crop_box = crop_minimap_region(frame, config, clean=False)
            match_data = make_filtered_match_data(data, config, center_tile)

            result = localize_minimap(
                minimap,
                kongying_data=match_data,
                max_assets=match_asset_limit(config, center_tile),
                debug_output_enabled=bool(config.get("debug_output_enabled", True)),
                debug_dir=config.get("debug_output_dir", "debug_output"),
                exclude_keywords=tuple(config.get("match_exclude_keywords", ["outline", "overlay"])),
                scales=tuple(float(value) for value in config.get("match_scales", [0.8])),
                min_confidence=float(config.get("min_match_confidence", 0.91)),
                min_score_margin=float(config.get("min_match_score_margin", 0.006)),
                mask_radius_ratio=float(config.get("match_mask_radius_ratio", 0.48)),
                inner_exclusion_ratio=float(config.get("match_inner_exclusion_ratio", 0.13)),
                preprocess_mode=str(config.get("match_preprocess_mode", "raw_gray")),
                method_name=str(config.get("match_method", "sqdiff_normed")),
                color_histogram_weight=float(config.get("match_color_histogram_weight", 0.0)),
            )

            result_dict = result.to_dict()
            if (
                result_dict.get("accepted")
                and result_dict.get("tile_x") is not None
                and result_dict.get("tile_y") is not None
            ):
                center_tile = (int(result_dict["tile_x"]), int(result_dict["tile_y"]))

            payload = result_to_frontend_payload(
                result=result_dict,
                config=config,
                frame_shape=frame.shape,
                crop_box=crop_box,
                iteration=iteration,
            )

            if latest_output_path:
                write_latest_payload(payload, latest_output_path)

            print(json.dumps(payload, ensure_ascii=False), flush=True)

        except KeyboardInterrupt:
            raise
        except Exception as exc:
            payload = error_payload(exc, config, iteration=iteration)

            if latest_output_path:
                write_latest_payload(payload, latest_output_path)

            print(json.dumps(payload, ensure_ascii=False), flush=True)

        if once or (count is not None and iteration >= count):
            return

        time.sleep(interval_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Genshin live tracker loop.")
    parser.add_argument(
        "--config",
        default="config/tracker_mac.json",
        help="Tracker config path.",
    )
    parser.add_argument("--once", action="store_true", help="Run one capture/localization iteration.")
    parser.add_argument("--count", type=int, default=None, help="Run N capture/localization iterations.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    count = 1 if args.once else args.count
    run_tracker_loop(resolve_repo_path(args.config), once=args.once, count=count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
