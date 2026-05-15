from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from tracker_core.utils.cv_images import read_image_bgr
from tracker_core.utils.paths import ensure_dir


class MacCaptureError(RuntimeError):
    pass


_WINDOW_ID_CACHE: dict[str, int] = {}


def _save_debug_image(frame_bgr: np.ndarray, output_path: Path) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise MacCaptureError("Pillow is required to save debug screenshots.") from exc

    rgb = frame_bgr[..., :3][..., ::-1]
    Image.fromarray(rgb).save(output_path)


def _capture_with_mss(monitor_index: int) -> np.ndarray:
    import mss

    with mss.mss() as screen_capture:
        monitors = [
            monitor
            for monitor in screen_capture.monitors
            if int(monitor.get("width", 0)) > 0 and int(monitor.get("height", 0)) > 0
        ]
        if not monitors:
            raise MacCaptureError("mss found no non-empty monitors.")
        selected_index = monitor_index if 0 <= monitor_index < len(monitors) else 0
        screenshot = screen_capture.grab(monitors[selected_index])
        frame_bgra = np.asarray(screenshot, dtype=np.uint8)
        return frame_bgra[..., :3]


def _mac_window_list() -> list[dict[str, Any]]:
    swift_code = r'''
import CoreGraphics
import Foundation

let options = CGWindowListOption(arrayLiteral: .optionOnScreenOnly, .excludeDesktopElements)
let windows = CGWindowListCopyWindowInfo(options, kCGNullWindowID) as? [[String: Any]] ?? []
for window in windows {
    let id = window[kCGWindowNumber as String] as? Int ?? 0
    let owner = window[kCGWindowOwnerName as String] as? String ?? ""
    let name = window[kCGWindowName as String] as? String ?? ""
    let bounds = window[kCGWindowBounds as String] as? [String: Any] ?? [:]
    let width = bounds["Width"] as? Int ?? 0
    let height = bounds["Height"] as? Int ?? 0
    let safeOwner = owner.replacingOccurrences(of: "\t", with: " ")
    let safeName = name.replacingOccurrences(of: "\t", with: " ")
    print("\(id)\t\(safeOwner)\t\(safeName)\t\(width)\t\(height)")
}
'''
    env = dict(os.environ)
    env.setdefault("CLANG_MODULE_CACHE_PATH", "/private/tmp/clang-module-cache")
    completed = subprocess.run(
        ["swift", "-e", swift_code],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout or "swift window query failed").strip()
        raise MacCaptureError(f"Could not query macOS windows: {message}")

    windows: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 5:
            continue
        try:
            window_id = int(parts[0])
            width = int(parts[3])
            height = int(parts[4])
        except ValueError:
            continue
        windows.append(
            {
                "id": window_id,
                "owner": parts[1],
                "name": parts[2],
                "width": width,
                "height": height,
            }
        )
    return windows


def _find_window_id(target: str, min_width: int, min_height: int) -> int:
    normalized_target = target.casefold()
    cached = _WINDOW_ID_CACHE.get(normalized_target)
    if cached is not None:
        return cached

    windows = _mac_window_list()
    matches = []
    for window in windows:
        owner = str(window.get("owner", ""))
        name = str(window.get("name", ""))
        if normalized_target not in f"{owner} {name}".casefold():
            continue
        if int(window.get("width", 0)) < min_width or int(window.get("height", 0)) < min_height:
            continue
        matches.append(window)

    if not matches:
        visible = ", ".join(
            f"{window.get('owner')}:{window.get('name')}"
            for window in windows
            if int(window.get("width", 0)) >= min_width and int(window.get("height", 0)) >= min_height
        )
        raise MacCaptureError(f'No visible "{target}" window found. Visible windows: {visible or "none"}')

    best = max(matches, key=lambda item: int(item.get("width", 0)) * int(item.get("height", 0)))
    window_id = int(best["id"])
    _WINDOW_ID_CACHE[normalized_target] = window_id
    return window_id


def _capture_window_id(window_id: int) -> np.ndarray:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as temp_file:
        completed = subprocess.run(
            ["/usr/sbin/screencapture", "-x", f"-l{window_id}", temp_file.name],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            message = (completed.stderr or completed.stdout or "unknown window capture failure").strip()
            raise MacCaptureError(message)

        frame_bgr = read_image_bgr(temp_file.name)
        if frame_bgr is None:
            raise MacCaptureError(f"screencapture produced an unreadable image for window {window_id}.")
        return frame_bgr


def _capture_genshin_window(config: dict[str, Any]) -> np.ndarray:
    target = str(config.get("target_window_title", "Genshin Impact"))
    window_id = _find_window_id(
        target,
        min_width=int(config.get("target_window_min_width", 800)),
        min_height=int(config.get("target_window_min_height", 500)),
    )
    return _capture_window_id(window_id)


def _capture_with_pillow() -> np.ndarray:
    from PIL import ImageGrab

    screenshot = ImageGrab.grab(all_screens=True)
    frame_rgb = np.asarray(screenshot.convert("RGB"), dtype=np.uint8)
    return frame_rgb[..., ::-1]


def _capture_with_screencapture() -> np.ndarray:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as temp_file:
        completed = subprocess.run(
            ["/usr/sbin/screencapture", "-x", temp_file.name],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            message = (completed.stderr or completed.stdout or "unknown screencapture failure").strip()
            raise MacCaptureError(message)

        frame_bgr = read_image_bgr(temp_file.name)
        if frame_bgr is None:
            raise MacCaptureError("screencapture produced an unreadable image.")
        return frame_bgr


def capture_full_screen(
    debug_output_enabled: bool = True,
    debug_dir: str | Path = "debug_output/mac",
    monitor_index: int = 0,
    backend: str = "auto",
    config: dict[str, Any] | None = None,
) -> np.ndarray:
    errors: list[str] = []
    backend_order = {
        "window": ("window",),
        "auto": ("mss", "pillow", "screencapture"),
        "mss": ("mss",),
        "pillow": ("pillow",),
        "screencapture": ("screencapture",),
    }.get(backend, ("mss", "pillow", "screencapture"))

    frame_bgr: np.ndarray | None = None
    for backend_name in backend_order:
        try:
            if backend_name == "window":
                frame_bgr = _capture_genshin_window(config or {})
            elif backend_name == "mss":
                frame_bgr = _capture_with_mss(monitor_index)
            elif backend_name == "pillow":
                frame_bgr = _capture_with_pillow()
            elif backend_name == "screencapture":
                frame_bgr = _capture_with_screencapture()
        except Exception as exc:
            errors.append(f"{backend_name}: {exc}")
            continue
        if frame_bgr is not None:
            break

    if frame_bgr is None:
        joined = "; ".join(errors) or "no capture backends were available"
        raise MacCaptureError(
            "Mac screen capture failed. Grant Screen Recording permission to the terminal/Codex app, "
            f"then rerun. Backends tried: {joined}"
        )

    if debug_output_enabled:
        output_dir = ensure_dir(debug_dir)
        _save_debug_image(frame_bgr, output_dir / "latest_capture.png")

    return frame_bgr


def capture_from_config(config: dict[str, Any]) -> np.ndarray:
    return capture_full_screen(
        debug_output_enabled=bool(config.get("debug_output_enabled", True)),
        debug_dir=config.get("debug_output_dir", "debug_output/mac"),
        monitor_index=int(config.get("monitor_index", 0)),
        backend=str(config.get("capture_backend", "auto")),
        config=config,
    )
