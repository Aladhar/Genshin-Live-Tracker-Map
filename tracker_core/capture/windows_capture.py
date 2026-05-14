from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from tracker_core.utils.paths import ensure_dir


class CaptureError(RuntimeError):
    pass


def _save_debug_image(frame_bgr: np.ndarray, output_path: Path) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise CaptureError("Pillow is required to save debug screenshots.") from exc

    rgb = frame_bgr[..., :3][..., ::-1]
    Image.fromarray(rgb).save(output_path)


def capture_full_screen(
    debug_output_enabled: bool = True,
    debug_dir: str | Path = "debug_output",
    monitor_index: int = 1,
) -> np.ndarray:
    """Capture the screen without game hooks, injection, admin access, or memory reads.

    Returns an OpenCV-compatible BGR numpy array.
    """

    frame_bgr: np.ndarray
    try:
        import mss

        with mss.mss() as screen_capture:
            monitors = screen_capture.monitors
            if not monitors:
                raise CaptureError("mss found no monitors.")
            selected_index = monitor_index if monitor_index < len(monitors) else 0
            screenshot = screen_capture.grab(monitors[selected_index])
            frame_bgra = np.asarray(screenshot, dtype=np.uint8)
            frame_bgr = frame_bgra[..., :3]
    except ImportError:
        try:
            from PIL import ImageGrab
        except ImportError as exc:
            raise CaptureError("Install `mss` or `Pillow` to capture the screen.") from exc

        screenshot = ImageGrab.grab(all_screens=True)
        frame_rgb = np.asarray(screenshot.convert("RGB"), dtype=np.uint8)
        frame_bgr = frame_rgb[..., ::-1]
    except Exception as exc:
        raise CaptureError(f"Screen capture failed: {exc}") from exc

    if debug_output_enabled:
        output_dir = ensure_dir(debug_dir)
        _save_debug_image(frame_bgr, output_dir / "latest_capture.png")

    return frame_bgr


def capture_from_config(config: dict[str, Any]) -> np.ndarray:
    return capture_full_screen(
        debug_output_enabled=bool(config.get("debug_output_enabled", True)),
        debug_dir=config.get("debug_output_dir", "debug_output"),
        monitor_index=int(config.get("monitor_index", 1)),
    )

