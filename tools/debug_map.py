from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tracker_core.localization.template_matcher import localize_minimap
from tracker_core.map_data.kongying_loader import KongYingMapData
from tracker_core.minimap.crop import crop_minimap_region
from tracker_core.utils.cv_images import read_image_bgr, write_image
from tracker_core.utils.paths import ensure_dir, load_json, resolve_repo_path


DEFAULT_DEBUG_DIR = Path("debug_output/mac_debug_map")


def bgr_to_pil(image_bgr: np.ndarray) -> Image.Image:
    return Image.fromarray(image_bgr[..., :3][..., ::-1])


def best_candidate(match_payload: dict[str, Any], index: int) -> dict[str, Any] | None:
    candidates = match_payload.get("top_candidates")
    if not isinstance(candidates, list) or not candidates:
        return None
    if index < 0 or index >= len(candidates):
        return None
    candidate = candidates[index]
    return candidate if isinstance(candidate, dict) else None


def candidate_crop(candidate: dict[str, Any]) -> Image.Image | None:
    asset_path = candidate.get("matched_asset")
    if not asset_path:
        return None

    map_bgr = read_image_bgr(resolve_repo_path(asset_path))
    if map_bgr is None:
        return None

    top_left_x = int(round(float(candidate.get("top_left_x", 0))))
    top_left_y = int(round(float(candidate.get("top_left_y", 0))))
    template_width = int(round(float(candidate.get("template_width", 0))))
    template_height = int(round(float(candidate.get("template_height", 0))))
    if template_width <= 0 or template_height <= 0:
        return None

    x0 = max(0, min(top_left_x, map_bgr.shape[1] - 1))
    y0 = max(0, min(top_left_y, map_bgr.shape[0] - 1))
    x1 = max(x0 + 1, min(x0 + template_width, map_bgr.shape[1]))
    y1 = max(y0 + 1, min(y0 + template_height, map_bgr.shape[0]))
    return bgr_to_pil(map_bgr[y0:y1, x0:x1])


def fit_panel(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    panel = Image.new("RGB", size, (24, 28, 32))
    working = image.convert("RGB")
    working.thumbnail((size[0] - 24, size[1] - 56), Image.Resampling.LANCZOS)
    x = (size[0] - working.width) // 2
    y = 44 + (size[1] - 56 - working.height) // 2
    panel.paste(working, (x, y))
    return panel


def draw_title(panel: Image.Image, title: str, lines: list[str]) -> None:
    draw = ImageDraw.Draw(panel)
    try:
        title_font = ImageFont.truetype("Arial.ttf", 20)
        text_font = ImageFont.truetype("Arial.ttf", 14)
    except OSError:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    draw.text((12, 10), title, fill=(255, 255, 255), font=title_font)
    y = panel.height - 12 - (len(lines) * 18)
    for line in lines:
        draw.text((12, y), line, fill=(220, 225, 230), font=text_font)
        y += 18


def build_comparison(
    minimap: Image.Image,
    candidate: Image.Image | None,
    payload: dict[str, Any],
    candidate_payload: dict[str, Any] | None,
    output_path: Path,
) -> Path:
    panel_size = (360, 430)
    panels: list[Image.Image] = []

    minimap_panel = fit_panel(minimap, panel_size)
    draw_title(minimap_panel, "Raw Captured Minimap", ["no UI inpaint / no cleanup"])
    panels.append(minimap_panel)

    if candidate is not None:
        candidate_panel = fit_panel(candidate, panel_size)
    else:
        candidate_panel = Image.new("RGB", panel_size, (24, 28, 32))

    result_lines = [
        f"accepted: {payload.get('accepted')}",
        f"confidence: {payload.get('confidence')}",
        f"reason: {payload.get('rejection_reason') or payload.get('error')}",
    ]
    if candidate_payload:
        result_lines.extend(
            [
                f"asset: {candidate_payload.get('asset_name')}",
                f"tile: {candidate_payload.get('tile_x')},{candidate_payload.get('tile_y')}",
                f"scale: {candidate_payload.get('scale')}",
            ]
        )
    draw_title(candidate_panel, "Top Map Candidate", result_lines[:6])
    panels.append(candidate_panel)

    sheet = Image.new("RGB", (panel_size[0] * len(panels), panel_size[1]), (18, 20, 24))
    for index, panel in enumerate(panels):
        sheet.paste(panel, (index * panel_size[0], 0))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)
    return output_path


def run_raw_confidence_test(
    minimap_bgr: np.ndarray,
    config: dict[str, Any],
    output_dir: Path,
    max_assets: int,
) -> dict[str, Any]:
    match_data = KongYingMapData(config.get("kongying_manifest", "data/kongying/manifest.json"))
    result = localize_minimap(
        minimap_bgr,
        kongying_data=match_data,
        max_assets=max_assets,
        debug_output_enabled=True,
        debug_dir=output_dir,
        exclude_keywords=tuple(config.get("match_exclude_keywords", ["outline", "overlay"])),
        scales=tuple(float(value) for value in config.get("match_scales", [0.8])),
        min_confidence=float(config.get("min_match_confidence", 0.91)),
        min_score_margin=float(config.get("min_match_score_margin", 0.006)),
        mask_radius_ratio=0.0,
        inner_exclusion_ratio=0.0,
        preprocess_mode=str(config.get("match_preprocess_mode", "raw_gray")),
        method_name=str(config.get("match_method", "sqdiff_normed")),
        color_histogram_weight=float(config.get("match_color_histogram_weight", 0.08)),
    )
    return result.to_dict()


def write_summary(
    output_dir: Path,
    match_payload: dict[str, Any],
    candidate_payload: dict[str, Any] | None,
    comparison_path: Path,
) -> Path:
    summary = {
        "accepted": match_payload.get("accepted"),
        "confidence": match_payload.get("confidence"),
        "error": match_payload.get("error"),
        "rejection_reason": match_payload.get("rejection_reason"),
        "score_margin": match_payload.get("score_margin"),
        "comparison_path": comparison_path.as_posix(),
        "candidate": candidate_payload,
    }
    summary_path = output_dir / "debug_map_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build side-by-side map matching debug images.")
    parser.add_argument("--config", default="config/tracker_mac.json", help="Tracker config path.")
    parser.add_argument("--frame", default="debug_output/mac/latest_capture.png", help="Latest captured frame path.")
    parser.add_argument("--output-dir", default=DEFAULT_DEBUG_DIR.as_posix(), help="Debug output directory.")
    parser.add_argument("--candidate-index", type=int, default=0, help="Top-candidate index to compare.")
    parser.add_argument(
        "--max-assets",
        type=int,
        default=0,
        help="Max map assets to search. 0 means full raw debug search; live loop config remains bounded.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = ensure_dir(args.output_dir)

    config = load_json(args.config)
    frame = read_image_bgr(resolve_repo_path(args.frame))
    if frame is None:
        raise RuntimeError(f"Could not load frame image: {args.frame}")

    minimap_bgr, crop_box = crop_minimap_region(frame, {**config, "debug_output_enabled": False}, clean=False)
    match_payload = run_raw_confidence_test(minimap_bgr, config, output_dir, max_assets=args.max_assets)
    candidate_payload = best_candidate(match_payload, args.candidate_index)
    candidate_image = candidate_crop(candidate_payload) if candidate_payload else None

    write_image(output_dir / "debug_map_raw_minimap.png", minimap_bgr)

    comparison_path = build_comparison(
        minimap=bgr_to_pil(minimap_bgr),
        candidate=candidate_image,
        payload=match_payload,
        candidate_payload=candidate_payload,
        output_path=output_dir / "debug_map_comparison.png",
    )
    summary_path = write_summary(output_dir, match_payload, candidate_payload, comparison_path)

    print(f"crop_box={crop_box.to_dict()}")
    print(f"comparison={comparison_path}")
    print(f"summary={summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
