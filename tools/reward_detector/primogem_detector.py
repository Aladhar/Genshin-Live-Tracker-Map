"""Screenshot-only Primogem/reward popup detector."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import numpy as np

from .capture import DEFAULT_REWARD_ROI, PixelRegion, RelativeRegion, crop
from .image_io import load_png


KNOWN_PRIMOGEM_AMOUNTS = (1, 2, 3, 5, 10, 15, 20, 30, 40, 60, 80)


@dataclass(frozen=True)
class Template:
    name: str
    path: Path
    image: np.ndarray


@dataclass(frozen=True)
class Match:
    template: str
    score: float
    rect: PixelRegion
    scale: float = 1.0

    def to_dict(self) -> dict:
        return {
            "template": self.template,
            "score": self.score,
            "scale": self.scale,
            "rect": [self.rect.left, self.rect.top, self.rect.width, self.rect.height],
        }


@dataclass
class DetectionResult:
    detected: bool
    confidence: float
    kind: str = "none"
    roi_name: str = "reward_stack"
    roi: PixelRegion | None = None
    match: Match | None = None
    amount: int | None = None
    amount_score: float = 0.0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "detected": self.detected,
            "confidence": round(self.confidence, 6),
            "kind": self.kind,
            "roiName": self.roi_name,
            "roi": None
            if self.roi is None
            else [self.roi.left, self.roi.top, self.roi.width, self.roi.height],
            "match": None if self.match is None else self.match.to_dict(),
            "amount": self.amount,
            "amountScore": round(self.amount_score, 6),
            "notes": self.notes,
        }


def default_templates_dir() -> Path:
    return Path(__file__).resolve().parent / "templates"


def load_templates(root: str | Path | None = None) -> list[Template]:
    """Load PNG templates from `templates/primogem` and `templates/reward_popup`."""

    root = Path(root) if root else default_templates_dir()
    templates: list[Template] = []
    for folder_name in ("primogem", "reward_popup"):
        folder = root / folder_name
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.png")):
            templates.append(Template(path.stem, path, load_png(path)))
    return templates


def load_digit_templates(root: str | Path | None = None) -> dict[str, np.ndarray]:
    root = Path(root) if root else default_templates_dir()
    digits_dir = root / "primogem" / "digits"
    digits: dict[str, np.ndarray] = {}
    for digit in "0123456789":
        path = digits_dir / f"{digit}.png"
        if path.exists():
            digits[digit] = load_png(path)
    return digits


def detect_primogem_reward(
    image: np.ndarray,
    *,
    templates_dir: str | Path | None = None,
    roi: RelativeRegion | PixelRegion | None = None,
    roi_name: str = "reward_stack",
    threshold: float = 0.78,
    scales: Iterable[float] = (0.75, 0.85, 1.0, 1.15, 1.30, 1.45),
) -> DetectionResult:
    """Detect a Primogem reward icon/text inside a normalized reward ROI."""

    if image.size == 0:
        return DetectionResult(False, 0.0, notes=["empty image"])

    roi = roi or DEFAULT_REWARD_ROI
    roi_pixels = roi.to_pixels(image.shape) if isinstance(roi, RelativeRegion) else roi.clamp(image.shape)
    roi_image = crop(image, roi_pixels)
    templates = load_templates(templates_dir)
    if not templates:
        return DetectionResult(False, 0.0, roi_name=roi_name, roi=roi_pixels, notes=["no templates loaded"])

    best: tuple[float, Template, PixelRegion, float] | None = None
    for template in templates:
        for scale in scales:
            scaled = resize_nearest(template.image, scale)
            if scaled.shape[0] < 2 or scaled.shape[1] < 2:
                continue
            score, top, left = match_template(roi_image, scaled)
            if best is None or score > best[0]:
                best = (score, template, PixelRegion(left, top, scaled.shape[1], scaled.shape[0]), scale)

    if best is None:
        return DetectionResult(False, 0.0, roi_name=roi_name, roi=roi_pixels, notes=["template matching skipped"])

    best_score, best_template, best_rect, best_scale = best
    notes: list[str] = []
    if best_score < threshold:
        return DetectionResult(
            False,
            float(best_score),
            roi_name=roi_name,
            roi=roi_pixels,
            match=Match(best_template.name, float(best_score), best_rect, best_scale),
            notes=[f"below threshold {threshold:.2f}"],
        )

    amount, amount_score = detect_amount(roi_image, best_rect, templates_dir=templates_dir)
    confidence = float(best_score)
    if amount is not None:
        confidence = min(1.0, 0.72 * confidence + 0.28 * amount_score)
    else:
        notes.append("primogem icon detected, amount not read")

    return DetectionResult(
        True,
        confidence,
        kind="primogem_reward",
        roi_name=roi_name,
        roi=roi_pixels,
        match=Match(best_template.name, float(best_score), best_rect, best_scale),
        amount=amount,
        amount_score=float(amount_score),
        notes=notes,
    )


def detect_amount(
    roi_image: np.ndarray,
    icon_rect: PixelRegion,
    *,
    templates_dir: str | Path | None = None,
    threshold: float = 0.58,
) -> tuple[int | None, float]:
    digits = load_digit_templates(templates_dir)
    if not digits:
        return None, 0.0

    search = PixelRegion(
        icon_rect.left + icon_rect.width,
        icon_rect.top - max(2, icon_rect.height // 4),
        max(24, icon_rect.width * 5),
        max(16, int(icon_rect.height * 1.7)),
    ).clamp(roi_image.shape)
    search_image = crop(roi_image, search)
    if search_image.size == 0:
        return None, 0.0

    best_amount: int | None = None
    best_score = 0.0
    for amount in KNOWN_PRIMOGEM_AMOUNTS:
        template = build_amount_template(str(amount), digits)
        if template.size == 0:
            continue
        for scale in (0.75, 0.9, 1.0, 1.15, 1.3):
            scaled = resize_nearest(template, scale)
            score, _top, _left = match_template(search_image, scaled)
            if score > best_score:
                best_amount = amount
                best_score = score

    if best_amount is None or best_score < threshold:
        return None, best_score
    return best_amount, best_score


def build_amount_template(text: str, digits: dict[str, np.ndarray]) -> np.ndarray:
    glyphs = [digits[char] for char in text if char in digits]
    if not glyphs:
        return np.zeros((0, 0, 3), dtype=np.uint8)

    heights = [glyph.shape[0] for glyph in glyphs]
    widths = [glyph.shape[1] for glyph in glyphs]
    height = max(heights)
    spacing = max(1, height // 5)
    width = sum(widths) + spacing * (len(glyphs) - 1)
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    x = 0
    for glyph in glyphs:
        y = (height - glyph.shape[0]) // 2
        canvas[y : y + glyph.shape[0], x : x + glyph.shape[1], : glyph.shape[2]] = glyph[:, :, :3]
        x += glyph.shape[1] + spacing
    return canvas


def resize_nearest(image: np.ndarray, scale: float) -> np.ndarray:
    if math.isclose(scale, 1.0):
        return image
    height, width = image.shape[:2]
    new_height = max(1, int(round(height * scale)))
    new_width = max(1, int(round(width * scale)))
    y_index = np.clip((np.arange(new_height) / scale).astype(int), 0, height - 1)
    x_index = np.clip((np.arange(new_width) / scale).astype(int), 0, width - 1)
    return image[y_index][:, x_index]


def to_gray(image: np.ndarray) -> np.ndarray:
    arr = np.asarray(image)
    if arr.ndim == 2:
        return arr.astype(np.float32)
    rgb = arr[:, :, :3].astype(np.float32)
    return rgb[:, :, 0] * 0.299 + rgb[:, :, 1] * 0.587 + rgb[:, :, 2] * 0.114


def match_template(image: np.ndarray, template: np.ndarray) -> tuple[float, int, int]:
    """Return best normalized cross-correlation score and top/left."""

    try:
        import cv2  # type: ignore
    except ModuleNotFoundError:
        return _match_template_numpy(image, template)

    search = to_gray(image).astype(np.float32)
    templ = to_gray(template).astype(np.float32)
    if search.shape[0] < templ.shape[0] or search.shape[1] < templ.shape[1]:
        return 0.0, 0, 0
    result = cv2.matchTemplate(search, templ, cv2.TM_CCOEFF_NORMED)
    _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(result)
    return float(max_val), int(max_loc[1]), int(max_loc[0])


def _match_template_numpy(image: np.ndarray, template: np.ndarray) -> tuple[float, int, int]:
    search = to_gray(image).astype(np.float32)
    templ = to_gray(template).astype(np.float32)
    th, tw = templ.shape
    ih, iw = search.shape
    if ih < th or iw < tw:
        return 0.0, 0, 0

    templ_centered = templ - templ.mean()
    templ_energy = float(np.sqrt(np.sum(templ_centered * templ_centered)))
    if templ_energy < 1e-6:
        return 0.0, 0, 0

    from numpy.lib.stride_tricks import sliding_window_view

    windows = sliding_window_view(search, (th, tw))
    means = windows.mean(axis=(-1, -2))
    centered = windows - means[:, :, None, None]
    numerator = np.sum(centered * templ_centered, axis=(-1, -2))
    energy = np.sqrt(np.sum(centered * centered, axis=(-1, -2))) * templ_energy
    scores = np.divide(numerator, energy, out=np.zeros_like(numerator), where=energy > 1e-6)
    flat_index = int(np.argmax(scores))
    top, left = np.unravel_index(flat_index, scores.shape)
    return float(scores[top, left]), int(top), int(left)

