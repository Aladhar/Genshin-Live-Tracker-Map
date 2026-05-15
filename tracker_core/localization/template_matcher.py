from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from tracker_core.map_data.kongying_loader import KongYingMapData
from tracker_core.map_data.map_assets import MapImageAsset
from tracker_core.utils.cv_images import read_image_bgr, write_image
from tracker_core.utils.paths import ensure_dir, repo_root


class LocalizationError(RuntimeError):
    pass


_MAP_PREPROCESS_CACHE: dict[tuple[str, str, int], np.ndarray] = {}


@dataclass(frozen=True)
class MatchCandidate:
    score: float
    asset: MapImageAsset
    scale: float
    top_left_x: int
    top_left_y: int
    template_width: int
    template_height: int
    local_x: float
    local_y: float
    global_x: float | None
    global_y: float | None
    map_width: int
    map_height: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "matched_asset": _repo_relative(self.asset.path),
            "asset_name": self.asset.asset_name,
            "region": self.asset.region,
            "tile_x": self.asset.tile_x,
            "tile_y": self.asset.tile_y,
            "scale": self.scale,
            "top_left_x": self.top_left_x,
            "top_left_y": self.top_left_y,
            "template_width": self.template_width,
            "template_height": self.template_height,
            "local_x": self.local_x,
            "local_y": self.local_y,
            "global_x": self.global_x,
            "global_y": self.global_y,
            "map_width": self.map_width,
            "map_height": self.map_height,
        }


@dataclass(frozen=True)
class LocalizationResult:
    x: float | None
    y: float | None
    confidence: float
    matched_asset: str | None
    error: str | None = None
    accepted: bool = False
    rejection_reason: str | None = None
    score_margin: float | None = None
    scale: float | None = None
    region: str | None = None
    tile_x: int | None = None
    tile_y: int | None = None
    local_x: float | None = None
    local_y: float | None = None
    global_x: float | None = None
    global_y: float | None = None
    candidate_x: float | None = None
    candidate_y: float | None = None
    candidate_local_x: float | None = None
    candidate_local_y: float | None = None
    candidate_global_x: float | None = None
    candidate_global_y: float | None = None
    candidate_count: int = 0
    top_candidates: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root()).as_posix()
    except ValueError:
        return path.as_posix()


def _read_image_bgr(path: Path) -> np.ndarray | None:
    try:
        return read_image_bgr(path)
    except RuntimeError as exc:
        raise LocalizationError("opencv-python is required for template matching.") from exc


def _write_image(path: Path, image: np.ndarray) -> None:
    try:
        write_image(path, image)
    except RuntimeError:
        return


def _require_cv2():
    try:
        import cv2
    except ImportError as exc:
        raise LocalizationError("opencv-python is required for template matching.") from exc

    return cv2


def _preprocess_for_match(image: np.ndarray, mode: str = "gray") -> np.ndarray:
    cv2 = _require_cv2()

    if len(image.shape) == 2:
        gray = image
    else:
        gray = cv2.cvtColor(image[..., :3], cv2.COLOR_BGR2GRAY)

    if mode == "edges":
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        edges = cv2.Canny(blurred, 45, 120)
        return cv2.dilate(edges, np.ones((2, 2), dtype=np.uint8), iterations=1)

    if mode == "raw_gray":
        return gray

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalized = clahe.apply(gray)
    return cv2.GaussianBlur(equalized, (3, 3), 0)


def _preprocessed_map_image(asset: MapImageAsset, map_image: np.ndarray, mode: str) -> np.ndarray:
    try:
        mtime_ns = asset.path.stat().st_mtime_ns
    except OSError:
        mtime_ns = 0

    cache_key = (str(asset.path), mode, mtime_ns)
    cached = _MAP_PREPROCESS_CACHE.get(cache_key)
    if cached is not None:
        return cached

    processed = _preprocess_for_match(map_image, mode)
    _MAP_PREPROCESS_CACHE[cache_key] = processed
    return processed


def build_circular_minimap_mask(
    shape: tuple[int, ...],
    radius_ratio: float = 0.43,
    inner_exclusion_ratio: float = 0.075,
) -> np.ndarray:
    cv2 = _require_cv2()

    height, width = shape[:2]
    center = (width // 2, height // 2)
    radius = max(4, int(min(width, height) * radius_ratio))
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)

    if inner_exclusion_ratio > 0:
        inner_radius = int(min(width, height) * inner_exclusion_ratio)
        if inner_radius > 0:
            cv2.circle(mask, center, inner_radius, 0, -1)

    return mask


def _resize_template_and_mask(
    template: np.ndarray,
    mask: np.ndarray,
    scale: float,
) -> tuple[np.ndarray, np.ndarray]:
    cv2 = _require_cv2()

    height, width = template.shape[:2]
    next_width = max(8, int(round(width * scale)))
    next_height = max(8, int(round(height * scale)))
    resized_template = cv2.resize(template, (next_width, next_height), interpolation=cv2.INTER_AREA)
    resized_mask = cv2.resize(mask, (next_width, next_height), interpolation=cv2.INTER_NEAREST)
    return resized_template, resized_mask


def _match_template(
    map_image: np.ndarray,
    template: np.ndarray,
    mask: np.ndarray,
    method_name: str,
) -> tuple[float, tuple[int, int]]:
    cv2 = _require_cv2()

    method_map = {
        "ccoeff_normed": cv2.TM_CCOEFF_NORMED,
        "ccorr_normed": cv2.TM_CCORR_NORMED,
        "sqdiff_normed": cv2.TM_SQDIFF_NORMED,
    }
    method = method_map.get(method_name, cv2.TM_CCOEFF_NORMED)

    try:
        result = cv2.matchTemplate(map_image, template, method, mask=mask)
    except cv2.error:
        result = cv2.matchTemplate(map_image, template, method)

    if method == cv2.TM_SQDIFF_NORMED:
        result = np.nan_to_num(result, nan=1.0, posinf=1.0, neginf=1.0)
        min_value, _, min_location, _ = cv2.minMaxLoc(result)
        return 1.0 - float(min_value), (int(min_location[0]), int(min_location[1]))

    result = np.nan_to_num(result, nan=-1.0, posinf=-1.0, neginf=-1.0)
    _, max_value, _, max_location = cv2.minMaxLoc(result)
    return float(max_value), (int(max_location[0]), int(max_location[1]))


def _save_mask_debug(mask: np.ndarray, output_path: Path) -> None:
    _write_image(output_path, mask)


def _save_template_debug(template_bgr: np.ndarray, mask: np.ndarray, output_path: Path) -> None:
    masked = template_bgr.copy()
    masked[mask == 0] = 0
    _write_image(output_path, masked)


def _save_match_debug(
    map_image: np.ndarray,
    candidate: MatchCandidate,
    output_path: Path,
) -> None:
    try:
        import cv2
    except ImportError:
        return

    debug = map_image.copy()
    x = candidate.top_left_x
    y = candidate.top_left_y
    cv2.rectangle(debug, (x, y), (x + candidate.template_width, y + candidate.template_height), (0, 0, 255), 3)
    label = f"{candidate.score:.3f} scale={candidate.scale:.2f}"
    cv2.putText(debug, label, (max(0, x), max(28, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    _write_image(output_path, debug)


def _save_candidate_contact_sheet(
    minimap_crop: np.ndarray,
    candidates: list[MatchCandidate],
    output_path: Path,
    max_items: int = 5,
) -> None:
    try:
        import cv2
    except ImportError:
        return

    tile_size = 260
    panels: list[np.ndarray] = []
    minimap_panel = cv2.resize(minimap_crop[..., :3], (tile_size, tile_size), interpolation=cv2.INTER_AREA)
    cv2.putText(minimap_panel, "minimap", (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
    panels.append(minimap_panel)

    for candidate in candidates[:max_items]:
        map_image = _read_image_bgr(candidate.asset.path)
        if map_image is None:
            continue
        x0 = candidate.top_left_x
        y0 = candidate.top_left_y
        x1 = min(map_image.shape[1], x0 + candidate.template_width)
        y1 = min(map_image.shape[0], y0 + candidate.template_height)
        if x1 <= x0 or y1 <= y0:
            continue
        crop = map_image[y0:y1, x0:x1]
        panel = cv2.resize(crop, (tile_size, tile_size), interpolation=cv2.INTER_AREA)
        label = f"{candidate.score:.3f} s={candidate.scale:.2f}"
        cv2.putText(panel, label, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
        cv2.putText(panel, candidate.asset.asset_name[:24], (8, 248), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)
        panels.append(panel)

    if not panels:
        return
    sheet = np.hstack(panels)
    _write_image(output_path, sheet)


def _candidate_from_match(
    asset: MapImageAsset,
    map_image: np.ndarray,
    score: float,
    top_left: tuple[int, int],
    scale: float,
    template_width: int,
    template_height: int,
) -> MatchCandidate:
    local_x = top_left[0] + template_width / 2.0
    local_y = top_left[1] + template_height / 2.0
    global_x, global_y = asset.global_pixel(local_x, local_y)
    return MatchCandidate(
        score=score,
        asset=asset,
        scale=scale,
        top_left_x=top_left[0],
        top_left_y=top_left[1],
        template_width=template_width,
        template_height=template_height,
        local_x=local_x,
        local_y=local_y,
        global_x=global_x,
        global_y=global_y,
        map_width=int(map_image.shape[1]),
        map_height=int(map_image.shape[0]),
    )


def _result_from_candidates(
    candidates: list[MatchCandidate],
    min_confidence: float,
    min_score_margin: float,
) -> LocalizationResult:
    if not candidates:
        return LocalizationResult(
            x=None,
            y=None,
            confidence=0.0,
            matched_asset=None,
            error="No candidate map image was large enough or readable for template matching.",
            accepted=False,
            candidate_count=0,
            top_candidates=[],
        )

    candidates = sorted(candidates, key=lambda item: item.score, reverse=True)
    best = candidates[0]
    second_score = candidates[1].score if len(candidates) > 1 else None
    score_margin = None if second_score is None else best.score - second_score

    rejection_reason = None
    if best.score < min_confidence:
        rejection_reason = f"low_confidence:{best.score:.3f}<{min_confidence:.3f}"
    elif score_margin is not None and score_margin < min_score_margin:
        rejection_reason = f"ambiguous_margin:{score_margin:.3f}<{min_score_margin:.3f}"

    accepted = rejection_reason is None
    best_x = best.global_x if best.global_x is not None else best.local_x
    best_y = best.global_y if best.global_y is not None else best.local_y

    return LocalizationResult(
        x=best_x if accepted else None,
        y=best_y if accepted else None,
        confidence=best.score,
        matched_asset=_repo_relative(best.asset.path),
        error=None if accepted else rejection_reason,
        accepted=accepted,
        rejection_reason=rejection_reason,
        score_margin=score_margin,
        scale=best.scale,
        region=best.asset.region,
        tile_x=best.asset.tile_x,
        tile_y=best.asset.tile_y,
        local_x=best.local_x if accepted else None,
        local_y=best.local_y if accepted else None,
        global_x=best.global_x if accepted else None,
        global_y=best.global_y if accepted else None,
        candidate_x=best_x,
        candidate_y=best_y,
        candidate_local_x=best.local_x,
        candidate_local_y=best.local_y,
        candidate_global_x=best.global_x,
        candidate_global_y=best.global_y,
        candidate_count=len(candidates),
        top_candidates=[candidate.to_dict() for candidate in candidates[:8]],
    )


def _write_result_debug(result: LocalizationResult, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file_obj:
        json.dump(result.to_dict(), file_obj, indent=2, ensure_ascii=False)
        file_obj.write("\n")


def localize_minimap(
    minimap_crop: np.ndarray,
    kongying_data: KongYingMapData | None = None,
    max_assets: int = 50,
    debug_output_enabled: bool = True,
    debug_dir: str | Path = "debug_output",
    exclude_keywords: tuple[str, ...] = ("outline", "overlay"),
    scales: tuple[float, ...] = (0.75, 0.85, 1.0, 1.15),
    min_confidence: float = 0.58,
    min_score_margin: float = 0.03,
    mask_radius_ratio: float = 0.43,
    inner_exclusion_ratio: float = 0.075,
    preprocess_mode: str = "gray",
    method_name: str = "ccoeff_normed",
) -> LocalizationResult:
    data = kongying_data or KongYingMapData()
    image_assets = data.list_match_image_asset_records(categories={"map_tile"}, exclude_keywords=exclude_keywords)
    if max_assets > 0:
        image_assets = image_assets[:max_assets]

    if not image_assets:
        return LocalizationResult(
            x=None,
            y=None,
            confidence=0.0,
            matched_asset=None,
            error=(
                "No directly loadable KongYing image assets found. "
                "Run `python tools/extract_kongying_textures.py --overwrite` from the repo root."
            ),
            accepted=False,
            candidate_count=0,
            top_candidates=[],
        )

    try:
        import cv2  # noqa: F401
    except ImportError:
        return LocalizationResult(
            x=None,
            y=None,
            confidence=0.0,
            matched_asset=None,
            error="opencv-python is required for template matching. Install dependencies with `pip install -r requirements.txt`.",
            accepted=False,
            candidate_count=0,
            top_candidates=[],
        )

    base_template = _preprocess_for_match(minimap_crop, preprocess_mode)
    base_mask = build_circular_minimap_mask(minimap_crop.shape, mask_radius_ratio, inner_exclusion_ratio)
    scaled_templates = [
        (scale, *_resize_template_and_mask(base_template, base_mask, scale))
        for scale in scales
    ]

    candidates: list[MatchCandidate] = []

    for asset in image_assets:
        map_image = _read_image_bgr(asset.path)
        if map_image is None:
            continue
        map_processed = _preprocessed_map_image(asset, map_image, preprocess_mode)

        for scale, template, mask in scaled_templates:
            template_height, template_width = template.shape[:2]
            map_height, map_width = map_processed.shape[:2]
            if map_width < template_width or map_height < template_height:
                continue

            score, top_left = _match_template(map_processed, template, mask, method_name)
            candidate = _candidate_from_match(
                asset=asset,
                map_image=map_image,
                score=score,
                top_left=top_left,
                scale=scale,
                template_width=template_width,
                template_height=template_height,
            )
            candidates.append(candidate)

    result = _result_from_candidates(candidates, min_confidence, min_score_margin)

    if debug_output_enabled:
        output_dir = ensure_dir(debug_dir)
        _save_mask_debug(base_mask, output_dir / "latest_match_mask.png")
        _save_template_debug(minimap_crop, base_mask, output_dir / "latest_match_template.png")
        sorted_candidates = sorted(candidates, key=lambda item: item.score, reverse=True)
        if sorted_candidates:
            best = sorted_candidates[0]
            map_image = _read_image_bgr(best.asset.path)
            if map_image is not None:
                _save_match_debug(map_image, best, output_dir / "latest_match.png")
            _save_candidate_contact_sheet(minimap_crop, sorted_candidates, output_dir / "latest_match_candidates.png")
        _write_result_debug(result, output_dir / "latest_match.json")

    return result
