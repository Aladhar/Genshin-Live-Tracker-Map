from __future__ import annotations

from pathlib import Path

import numpy as np


def read_image_bgr(path: str | Path):
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("opencv-python is required for image loading.") from exc

    resolved = Path(path)
    try:
        data = np.fromfile(resolved, dtype=np.uint8)
    except OSError:
        return None
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def write_image(path: str | Path, image) -> bool:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("opencv-python is required for image writing.") from exc

    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    suffix = resolved.suffix or ".png"
    ok, encoded = cv2.imencode(suffix, image)
    if not ok:
        return False
    encoded.tofile(resolved)
    return True
