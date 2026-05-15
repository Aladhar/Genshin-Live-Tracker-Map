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
from tracker_core.minimap.crop import crop_minimap_region
from tracker_core.utils.paths import load_json, resolve_repo_path


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


def result_to_frontend_payload(
    result: dict[str, Any],
    config: dict[str, Any],
    frame_shape: tuple[int, ...],
    crop_box: Any | None,
) -> dict[str, Any]:
    accepted = bool(result.get("accepted"))
    x = result.get("x")
    y = result.get("y")

    # Leaflet uses [lat, lng]. Our tracker result is x/y pixel-ish map coords.
    # Usually: lat = y, lng = x.
    map_position = None
    if accepted and x is not None and y is not None:
        map_position = {
            "lat": float(y),
            "lng": float(x),
        }

    return {
        "schema_version": 1,
        "platform": str(config.get("platform", "mac")),
        "timestamp": utc_now(),
        "frame_source": "live_screen",
        "frame_shape": list(frame_shape[:3]),
        "crop_box": crop_box.to_dict() if crop_box is not None else None,
        "accepted": accepted,
        "map_position": map_position,
        "result": result,
    }


def write_latest_payload(payload: dict[str, Any], output_path: str | Path) -> None:
    path = resolve_repo_path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def error_payload(exc: Exception, config: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "platform": str(config.get("platform", "mac")),
        "timestamp": utc_now(),
        "frame_source": "live_screen",
        "frame_shape": None,
        "crop_box": None,
        "accepted": False,
        "map_position": None,
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


def run_tracker_loop(config_path: str | Path, once: bool = False) -> None:
    config = load_json(config_path)
    data = KongYingMapData(config.get("kongying_manifest", "data/kongying/manifest.json"))
    interval_seconds = float(config.get("tracker_interval_seconds", 0.75))
    latest_output_path = config.get("latest_output_path")
    capture_from_config = choose_capture(config)

    while True:
        try:
            frame = capture_from_config(config)

            # New auto crop path. This returns both minimap image and crop metadata.
            minimap, crop_box = crop_minimap_region(frame, config, clean=True)

            result = localize_minimap(
                minimap,
                kongying_data=data,
                max_assets=int(config.get("max_match_assets", 0)),
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
            )

            payload = result_to_frontend_payload(
                result=result.to_dict(),
                config=config,
                frame_shape=frame.shape,
                crop_box=crop_box,
            )

            if latest_output_path:
                write_latest_payload(payload, latest_output_path)

            print(json.dumps(payload, ensure_ascii=False), flush=True)

        except KeyboardInterrupt:
            raise
        except Exception as exc:
            payload = error_payload(exc, config)

            if latest_output_path:
                write_latest_payload(payload, latest_output_path)

            print(json.dumps(payload, ensure_ascii=False), flush=True)

        if once:
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_tracker_loop(resolve_repo_path(args.config), once=args.once)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())