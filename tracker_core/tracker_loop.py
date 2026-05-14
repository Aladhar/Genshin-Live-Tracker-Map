from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tracker_core.capture.windows_capture import capture_from_config
from tracker_core.localization.template_matcher import localize_minimap
from tracker_core.map_data.kongying_loader import KongYingMapData
from tracker_core.minimap.crop import crop_minimap
from tracker_core.utils.paths import load_json, resolve_repo_path


def result_payload(result: dict[str, Any]) -> dict[str, Any]:
    payload = dict(result)
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    return payload


def run_tracker_loop(config_path: str | Path, once: bool = False) -> None:
    config = load_json(config_path)
    data = KongYingMapData(config.get("kongying_manifest", "data/kongying/manifest.json"))
    interval_seconds = float(config.get("tracker_interval_seconds", 0.75))

    while True:
        try:
            frame = capture_from_config(config)
            minimap = crop_minimap(frame, config)
            result = localize_minimap(
                minimap,
                kongying_data=data,
                max_assets=int(config.get("max_match_assets", 50)),
                debug_output_enabled=bool(config.get("debug_output_enabled", True)),
                debug_dir=config.get("debug_output_dir", "debug_output"),
                exclude_keywords=tuple(config.get("match_exclude_keywords", ["outline", "overlay"])),
                scales=tuple(float(value) for value in config.get("match_scales", [0.75, 0.85, 1.0, 1.15])),
                min_confidence=float(config.get("min_match_confidence", 0.58)),
                min_score_margin=float(config.get("min_match_score_margin", 0.03)),
                mask_radius_ratio=float(config.get("match_mask_radius_ratio", 0.43)),
                inner_exclusion_ratio=float(config.get("match_inner_exclusion_ratio", 0.075)),
                preprocess_mode=str(config.get("match_preprocess_mode", "gray")),
                method_name=str(config.get("match_method", "ccoeff_normed")),
            )
            print(json.dumps(result_payload(result.to_dict()), ensure_ascii=False), flush=True)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            print(
                json.dumps(
                    {
                        "x": None,
                        "y": None,
                        "confidence": 0.0,
                        "matched_asset": None,
                        "error": str(exc),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )

        if once:
            return
        time.sleep(interval_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Windows Genshin tracker loop.")
    parser.add_argument("--config", default="config/tracker_windows.json", help="Tracker config path.")
    parser.add_argument("--once", action="store_true", help="Run one capture/localization iteration.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_tracker_loop(resolve_repo_path(args.config), once=args.once)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
