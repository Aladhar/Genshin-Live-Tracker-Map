"""Screenshot capture and resolution-independent crop helpers.

This module never reads game memory, injects code, or touches game files. It
captures pixels from the screen or from an image file supplied by the user.
"""

from __future__ import annotations

import argparse
import platform
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

from .image_io import load_png, write_png


class CaptureError(RuntimeError):
    """Raised when live screenshot capture is unavailable or denied."""


@dataclass(frozen=True)
class PixelRegion:
    left: int
    top: int
    width: int
    height: int

    @classmethod
    def parse(cls, value: str) -> "PixelRegion":
        parts = [int(part.strip()) for part in value.split(",")]
        if len(parts) != 4:
            raise argparse.ArgumentTypeError("region must be left,top,width,height")
        return cls(*parts)

    def clamp(self, image_shape: tuple[int, ...]) -> "PixelRegion":
        height, width = image_shape[:2]
        left = max(0, min(self.left, width))
        top = max(0, min(self.top, height))
        right = max(left, min(self.left + self.width, width))
        bottom = max(top, min(self.top + self.height, height))
        return PixelRegion(left, top, right - left, bottom - top)


@dataclass(frozen=True)
class RelativeRegion:
    x: float
    y: float
    width: float
    height: float

    def to_pixels(self, image_shape: tuple[int, ...]) -> PixelRegion:
        height, width = image_shape[:2]
        return PixelRegion(
            int(round(self.x * width)),
            int(round(self.y * height)),
            int(round(self.width * width)),
            int(round(self.height * height)),
        ).clamp(image_shape)


# Broad by default: visual references and Kongying's local note place reward
# gain toasts in the middle/right reward stack, but this keeps room for aspect
# ratios and UI scale.
DEFAULT_REWARD_ROI = RelativeRegion(0.48, 0.20, 0.42, 0.58)
CENTER_POPUP_ROI = RelativeRegion(0.30, 0.24, 0.40, 0.36)


def crop(image: np.ndarray, region: PixelRegion | RelativeRegion) -> np.ndarray:
    if isinstance(region, RelativeRegion):
        region = region.to_pixels(image.shape)
    region = region.clamp(image.shape)
    return image[region.top : region.top + region.height, region.left : region.left + region.width].copy()


def capture_screenshot(
    *,
    output_path: str | Path | None = None,
    monitor: int = 1,
    region: PixelRegion | None = None,
) -> np.ndarray:
    """Capture the current screen.

    Uses `mss` when installed. On macOS, falls back to the `screencapture`
    command, which may require Screen Recording permission.
    """

    try:
        from mss import mss  # type: ignore
    except ModuleNotFoundError:
        return _capture_with_platform_tool(output_path=output_path, region=region)

    with mss() as sct:
        if region is None:
            monitors = sct.monitors
            source = monitors[monitor] if monitor < len(monitors) else monitors[1]
        else:
            source = {
                "left": region.left,
                "top": region.top,
                "width": region.width,
                "height": region.height,
            }
        shot = sct.grab(source)
        image = np.frombuffer(shot.rgb, dtype=np.uint8).reshape(shot.height, shot.width, 3).copy()

    if output_path:
        write_png(output_path, image)
    return image


def _capture_with_platform_tool(
    *,
    output_path: str | Path | None = None,
    region: PixelRegion | None = None,
) -> np.ndarray:
    system = platform.system()
    if system != "Darwin":
        raise CaptureError("install mss for live capture on this platform")

    out = Path(output_path) if output_path else Path(tempfile.mkstemp(suffix=".png")[1])
    cmd = ["screencapture", "-x"]
    if region is not None:
        cmd.extend(["-R", f"{region.left},{region.top},{region.width},{region.height}"])
    cmd.append(str(out))

    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise CaptureError(result.stderr.strip() or "screencapture failed")
    return load_png(out)


def parse_relative_region(value: str) -> RelativeRegion:
    parts = [float(part.strip()) for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("relative ROI must be x,y,width,height")
    return RelativeRegion(*parts)


def iter_default_rois() -> Iterable[tuple[str, RelativeRegion]]:
    yield "reward_stack", DEFAULT_REWARD_ROI
    yield "center_popup", CENTER_POPUP_ROI

