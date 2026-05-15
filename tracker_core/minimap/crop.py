from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from tracker_core.utils.paths import ensure_dir


class MinimapCropError(RuntimeError):
    pass


@dataclass(frozen=True)
class CropBox:
    x: int
    y: int
    width: int
    height: int
    source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "source": self.source,
        }


@dataclass(frozen=True)
class MinimapCropConfig:
    x: int = 24
    y: int = 32
    width: int = 260
    height: int = 260
    debug_output_enabled: bool = True
    debug_output_dir: str = "debug_output"

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "MinimapCropConfig":
        return cls(
            x=int(config.get("minimap_crop_x", cls.x)),
            y=int(config.get("minimap_crop_y", cls.y)),
            width=int(config.get("minimap_crop_width", cls.width)),
            height=int(config.get("minimap_crop_height", cls.height)),
            debug_output_enabled=bool(config.get("debug_output_enabled", cls.debug_output_enabled)),
            debug_output_dir=str(config.get("debug_output_dir", cls.debug_output_dir)),
        )


def _save_debug_image(frame_bgr: np.ndarray, output_path: Path) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise MinimapCropError("Pillow is required to save minimap debug crops.") from exc

    rgb = frame_bgr[..., :3][..., ::-1]
    Image.fromarray(rgb).save(output_path)


def _require_cv2():
    try:
        import cv2
    except ImportError as exc:
        raise MinimapCropError("opencv-python is required for automatic minimap cropping.") from exc

    return cv2


def _clamp_box(x0: int, y0: int, x1: int, y1: int, frame_width: int, frame_height: int, source: str) -> CropBox:
    x0 = max(0, min(x0, frame_width - 1))
    y0 = max(0, min(y0, frame_height - 1))
    x1 = max(x0 + 1, min(x1, frame_width))
    y1 = max(y0 + 1, min(y1, frame_height))
    return CropBox(x=x0, y=y0, width=x1 - x0, height=y1 - y0, source=source)


def fixed_ratio_crop_box(frame_shape: tuple[int, ...], crop_config: dict[str, Any]) -> CropBox:
    frame_height, frame_width = frame_shape[:2]
    x = int(round(frame_width * float(crop_config.get("fixed_x_ratio", 0.025))))
    y = int(round(frame_height * float(crop_config.get("fixed_y_ratio", 0.015))))
    if crop_config.get("fixed_size_ratio") is not None:
        size = int(round(min(frame_width, frame_height) * float(crop_config.get("fixed_size_ratio", 0.24))))
        width = size
        height = size
    else:
        width = int(round(frame_width * float(crop_config.get("fixed_width_ratio", 0.145))))
        height = int(round(frame_height * float(crop_config.get("fixed_height_ratio", 0.24))))
    return _clamp_box(x, y, x + width, y + height, frame_width, frame_height, "fixed_ratio")


def auto_minimap_crop_box(frame: np.ndarray, crop_config: dict[str, Any]) -> CropBox | None:
    """Find the circular minimap in the top-left screenshot ROI."""

    try:
        cv2 = _require_cv2()
    except MinimapCropError:
        return None

    frame_height, frame_width = frame.shape[:2]
    roi_x = int(round(frame_width * float(crop_config.get("roi_x_ratio", 0.0))))
    roi_y = int(round(frame_height * float(crop_config.get("roi_y_ratio", 0.0))))
    roi_w = int(round(frame_width * float(crop_config.get("roi_width_ratio", 0.28))))
    roi_h = int(round(frame_height * float(crop_config.get("roi_height_ratio", 0.34))))
    roi_box = _clamp_box(roi_x, roi_y, roi_x + roi_w, roi_y + roi_h, frame_width, frame_height, "roi")
    roi = frame[roi_box.y : roi_box.y + roi_box.height, roi_box.x : roi_box.x + roi_box.width]

    gray = cv2.cvtColor(roi[..., :3], cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    min_dim = min(frame_width, frame_height)
    min_radius = max(48, int(min_dim * float(crop_config.get("min_radius_ratio", 0.085))))
    max_radius = max(min_radius + 16, int(min_dim * float(crop_config.get("max_radius_ratio", 0.17))))
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=float(crop_config.get("hough_dp", 1.2)),
        minDist=max(80, min_radius),
        param1=float(crop_config.get("hough_param1", 80)),
        param2=float(crop_config.get("hough_param2", 24)),
        minRadius=min_radius,
        maxRadius=max_radius,
    )
    if circles is None:
        return None

    expected_x = frame_width * float(crop_config.get("expected_center_x_ratio", 0.092))
    expected_y = frame_height * float(crop_config.get("expected_center_y_ratio", 0.15))
    candidates: list[tuple[float, int, int, int]] = []
    for circle in np.round(circles[0]).astype(int):
        cx = int(circle[0]) + roi_box.x
        cy = int(circle[1]) + roi_box.y
        radius = int(circle[2])
        padding = int(round(radius * float(crop_config.get("padding_ratio", 0.05))))
        x0 = cx - radius - padding
        y0 = cy - radius - padding
        x1 = cx + radius + padding
        y1 = cy + radius + padding
        if cx - radius > frame_width * 0.36 or cy - radius > frame_height * 0.40:
            continue
        if x0 < 0 or y0 < 0 or x1 > frame_width or y1 > frame_height:
            continue
        distance_score = ((cx - expected_x) / max(1.0, frame_width * 0.18)) ** 2
        distance_score += ((cy - expected_y) / max(1.0, frame_height * 0.22)) ** 2
        radius_score = -0.10 * (radius / max_radius)
        candidates.append((distance_score + radius_score, cx, cy, radius))

    if not candidates:
        return None

    _, cx, cy, radius = sorted(candidates, key=lambda item: item[0])[0]
    padding = int(round(radius * float(crop_config.get("padding_ratio", 0.05))))
    return _clamp_box(
        cx - radius - padding,
        cy - radius - padding,
        cx + radius + padding,
        cy + radius + padding,
        frame_width,
        frame_height,
        "auto_circle",
    )


def clean_minimap_noise(crop: np.ndarray, crop_config: dict[str, Any]) -> np.ndarray:
    if not bool(crop_config.get("clean_noise", True)):
        return crop

    cv2 = _require_cv2()
    cleaned = crop.copy()
    height, width = cleaned.shape[:2]
    center = (width // 2, height // 2)
    min_dim = min(width, height)

    mask = np.zeros((height, width), dtype=np.uint8)
    marker_radius = max(6, int(min_dim * float(crop_config.get("player_marker_radius_ratio", 0.055))))
    cv2.circle(mask, center, marker_radius, 255, -1)

    ring_margin = max(2, int(min_dim * float(crop_config.get("outer_ring_margin_ratio", 0.035))))
    outer_radius = min_dim // 2
    cv2.circle(mask, center, outer_radius, 255, ring_margin)

    if mask.any():
        cleaned = cv2.inpaint(cleaned, mask, 3, cv2.INPAINT_TELEA)
    return cleaned


def crop_minimap_region(frame: np.ndarray, config: dict[str, Any], *, clean: bool = True) -> tuple[np.ndarray, CropBox]:
    if frame is None or not hasattr(frame, "shape") or len(frame.shape) < 2:
        raise MinimapCropError("Expected a numpy image array for minimap cropping.")

    crop_config = dict(config.get("minimap_crop", {}))
    mode = str(crop_config.get("mode", "auto"))
    crop_box = auto_minimap_crop_box(frame, crop_config) if mode == "auto" else None
    if crop_box is None:
        crop_box = fixed_ratio_crop_box(frame.shape, crop_config)

    crop = frame[crop_box.y : crop_box.y + crop_box.height, crop_box.x : crop_box.x + crop_box.width].copy()
    if clean:
        crop = clean_minimap_noise(crop, crop_config)

    if config.get("debug_output_enabled", True):
        output_dir = ensure_dir(config.get("debug_output_dir", "debug_output"))
        _save_debug_image(crop, output_dir / "latest_minimap.png")

    return crop, crop_box


def crop_minimap(frame: np.ndarray, config: dict[str, Any] | MinimapCropConfig) -> np.ndarray:
    if frame is None or not hasattr(frame, "shape") or len(frame.shape) < 2:
        raise MinimapCropError("Expected a numpy image array for minimap cropping.")

    crop_config = config if isinstance(config, MinimapCropConfig) else MinimapCropConfig.from_dict(config)
    frame_height, frame_width = frame.shape[:2]

    x0 = max(0, min(crop_config.x, frame_width))
    y0 = max(0, min(crop_config.y, frame_height))
    x1 = max(x0, min(x0 + crop_config.width, frame_width))
    y1 = max(y0, min(y0 + crop_config.height, frame_height))

    if x1 <= x0 or y1 <= y0:
        raise MinimapCropError(
            f"Invalid minimap crop box ({crop_config.x}, {crop_config.y}, "
            f"{crop_config.width}, {crop_config.height}) for frame {frame_width}x{frame_height}."
        )

    crop = frame[y0:y1, x0:x1].copy()

    if crop_config.debug_output_enabled:
        output_dir = ensure_dir(crop_config.debug_output_dir)
        _save_debug_image(crop, output_dir / "latest_minimap.png")

    return crop
