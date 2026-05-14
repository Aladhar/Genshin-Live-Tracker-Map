from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from tracker_core.utils.paths import ensure_dir


class MinimapCropError(RuntimeError):
    pass


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

