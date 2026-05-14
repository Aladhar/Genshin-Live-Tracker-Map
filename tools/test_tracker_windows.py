from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tracker_core.capture.windows_capture import capture_from_config  # noqa: E402
from tracker_core.localization.template_matcher import localize_minimap  # noqa: E402
from tracker_core.map_data.kongying_loader import KongYingMapData  # noqa: E402
from tracker_core.minimap.crop import crop_minimap  # noqa: E402
from tracker_core.utils.paths import ensure_dir  # noqa: E402
from tracker_core.utils.paths import load_json, resolve_repo_path  # noqa: E402


def load_frame_from_image(path: Path):
    try:
        import cv2
    except ImportError:
        try:
            import numpy as np
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Pillow and numpy are required to load a test frame when OpenCV is missing.") from exc

        frame_rgb = np.asarray(Image.open(path).convert("RGB"))
        return frame_rgb[..., ::-1].copy()

    frame = cv2.imread(path.as_posix(), cv2.IMREAD_COLOR)
    if frame is None:
        raise RuntimeError(f"Could not load frame image: {path}")
    return frame


def save_debug_capture(frame, config: dict) -> None:
    if not config.get("debug_output_enabled", True):
        return
    try:
        from PIL import Image
    except ImportError:
        return

    output_dir = ensure_dir(config.get("debug_output_dir", "debug_output"))
    Image.fromarray(frame[..., :3][..., ::-1]).save(output_dir / "latest_capture.png")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one Windows tracker test pass.")
    parser.add_argument("--config", default="config/tracker_windows.json", help="Tracker config path.")
    parser.add_argument(
        "--frame",
        default=None,
        help="Optional screenshot path to use instead of live screen capture. Useful for local debugging.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_json(args.config)
    data = KongYingMapData(config.get("kongying_manifest", "data/kongying/manifest.json"))

    if args.frame:
        frame = load_frame_from_image(resolve_repo_path(args.frame))
        save_debug_capture(frame, config)
        capture_source = args.frame
    else:
        frame = capture_from_config(config)
        capture_source = "live_screen"

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

    payload = {
        "capture_source": capture_source,
        "frame_shape": list(frame.shape),
        "minimap_shape": list(minimap.shape),
        "regions": data.list_regions(),
        "result": result.to_dict(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
