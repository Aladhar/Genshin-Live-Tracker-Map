from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tracker_core.localization.template_matcher import localize_minimap  # noqa: E402
from tracker_core.map_data.kongying_loader import KongYingMapData  # noqa: E402
from tracker_core.utils.paths import ensure_dir, resolve_repo_path  # noqa: E402


def read_image_bgr(path: Path):
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("opencv-python is required for the localization smoke test.") from exc
    image = cv2.imread(path.as_posix(), cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Could not read smoke-test image: {path}")
    return image


def write_image(path: Path, image) -> None:
    import cv2

    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(path.as_posix(), image)


def pick_smoke_asset(data: KongYingMapData, preferred_asset_name: str | None = None):
    assets = data.list_match_image_asset_records(categories={"map_tile"}, exclude_keywords=("outline", "overlay"))
    if preferred_asset_name:
        for asset in assets:
            if asset.asset_name == preferred_asset_name:
                return asset

    for asset in assets:
        if asset.tile_x is not None and asset.tile_y is not None and asset.path.exists():
            image = read_image_bgr(asset.path)
            if image.shape[0] >= 768 and image.shape[1] >= 768:
                return asset

    raise RuntimeError("No suitable processed map tile found for smoke test.")


def make_synthetic_minimap(source_image, left: int, top: int, source_size: int, output_size: int):
    import cv2
    import numpy as np

    crop = source_image[top : top + source_size, left : left + source_size].copy()
    resized = cv2.resize(crop, (output_size, output_size), interpolation=cv2.INTER_AREA)
    mask = np.zeros((output_size, output_size), dtype=np.uint8)
    cv2.circle(mask, (output_size // 2, output_size // 2), int(output_size * 0.43), 255, -1)
    synthetic = resized.copy()
    synthetic[mask == 0] = 0
    return synthetic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a deterministic localization smoke test using extracted map PNGs.")
    parser.add_argument("--config", default="config/tracker_windows.json", help="Tracker config path.")
    parser.add_argument(
        "--asset-name",
        default="UI_MapBack_-1_0",
        help="Optional processed asset name to crop from.",
    )
    parser.add_argument("--left", type=int, default=650, help="Known source crop left coordinate.")
    parser.add_argument("--top", type=int, default=650, help="Known source crop top coordinate.")
    parser.add_argument("--output-size", type=int, default=260, help="Synthetic minimap output size.")
    parser.add_argument("--scale", type=float, default=0.8, help="Map-source crop size as output_size * scale.")
    parser.add_argument("--tolerance", type=float, default=3.0, help="Allowed local-pixel error.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = resolve_repo_path(args.config)
    with config_path.open("r", encoding="utf-8") as file_obj:
        config = json.load(file_obj)

    data = KongYingMapData(config.get("kongying_manifest", "data/kongying/manifest.json"))
    asset = pick_smoke_asset(data, args.asset_name)
    source_image = read_image_bgr(asset.path)
    source_size = max(32, int(round(args.output_size * args.scale)))

    if args.left + source_size > source_image.shape[1] or args.top + source_size > source_image.shape[0]:
        raise RuntimeError(
            f"Smoke crop {args.left},{args.top},{source_size} does not fit {source_image.shape[1]}x{source_image.shape[0]}"
        )

    synthetic = make_synthetic_minimap(source_image, args.left, args.top, source_size, args.output_size)
    debug_dir = ensure_dir(config.get("debug_output_dir", "debug_output"))
    write_image(debug_dir / "smoke_synthetic_minimap.png", synthetic)

    expected_local_x = args.left + source_size / 2.0
    expected_local_y = args.top + source_size / 2.0
    expected_global_x, expected_global_y = asset.global_pixel(expected_local_x, expected_local_y)

    result = localize_minimap(
        synthetic,
        kongying_data=data,
        max_assets=0,
        debug_output_enabled=True,
        debug_dir=debug_dir,
        exclude_keywords=tuple(config.get("match_exclude_keywords", ["outline", "overlay"])),
        scales=(args.scale,),
        min_confidence=0.85,
        min_score_margin=0.01,
        mask_radius_ratio=float(config.get("match_mask_radius_ratio", 0.43)),
        inner_exclusion_ratio=0.0,
        preprocess_mode=str(config.get("match_preprocess_mode", "gray")),
        method_name=str(config.get("match_method", "ccoeff_normed")),
    )

    result_dict = result.to_dict()
    local_error_x = None if result.candidate_local_x is None else abs(result.candidate_local_x - expected_local_x)
    local_error_y = None if result.candidate_local_y is None else abs(result.candidate_local_y - expected_local_y)
    same_asset = result.matched_asset == asset.repo_path
    passed = bool(
        result.accepted
        and same_asset
        and local_error_x is not None
        and local_error_y is not None
        and local_error_x <= args.tolerance
        and local_error_y <= args.tolerance
    )

    payload = {
        "passed": passed,
        "source_asset": asset.to_dict(),
        "source_crop": {
            "left": args.left,
            "top": args.top,
            "source_size": source_size,
            "output_size": args.output_size,
            "scale": args.scale,
        },
        "expected": {
            "local_x": expected_local_x,
            "local_y": expected_local_y,
            "global_x": expected_global_x,
            "global_y": expected_global_y,
        },
        "actual": {
            "local_x": result.candidate_local_x,
            "local_y": result.candidate_local_y,
            "global_x": result.candidate_global_x,
            "global_y": result.candidate_global_y,
            "confidence": result.confidence,
            "matched_asset": result.matched_asset,
            "accepted": result.accepted,
            "error": result.error,
        },
        "error_pixels": {
            "local_x": local_error_x,
            "local_y": local_error_y,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
