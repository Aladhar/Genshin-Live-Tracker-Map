from __future__ import annotations

from pathlib import Path

import numpy as np

from tracker_core.utils.cv_images import write_image

from tracker_core.utils.paths import ensure_dir


def draw_live_marker(
    image_bgr: np.ndarray,
    x: float,
    y: float,
    rotation_degrees: float | None = None,
    color: tuple[int, int, int] = (0, 64, 255),
) -> np.ndarray:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("opencv-python is required to draw the live marker.") from exc

    output = image_bgr.copy()
    center = (int(round(x)), int(round(y)))
    cv2.circle(output, center, 12, color, 3)
    cv2.circle(output, center, 3, color, -1)

    if rotation_degrees is not None:
        radians = np.deg2rad(rotation_degrees)
        end = (
            int(round(center[0] + np.sin(radians) * 28)),
            int(round(center[1] - np.cos(radians) * 28)),
        )
        cv2.arrowedLine(output, center, end, color, 3, tipLength=0.35)

    return output


def save_live_marker_debug(image_bgr: np.ndarray, path: str | Path = "debug_output/latest_marker.png") -> Path:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("opencv-python is required to save marker debug output.") from exc

    output_path = ensure_dir(Path(path).parent) / Path(path).name
    write_image(output_path, image_bgr)
    return output_path

