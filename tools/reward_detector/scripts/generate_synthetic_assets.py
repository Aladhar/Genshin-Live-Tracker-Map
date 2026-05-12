"""Generate local synthetic templates and smoke-test fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ..image_io import write_png


DIGITS = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
}


def make_primogem_icon(size: int = 32) -> np.ndarray:
    image = np.zeros((size, size, 3), dtype=np.uint8)
    center = (size - 1) / 2.0
    radius = size * 0.42
    for y in range(size):
        for x in range(size):
            dx = abs(x - center)
            dy = abs(y - center)
            diamond = dx / radius + dy / radius
            if diamond <= 1.0:
                glow = 1.0 - diamond
                image[y, x] = (
                    int(120 + 95 * glow),
                    int(75 + 105 * glow),
                    int(210 + 35 * glow),
                )
            if dx < size * 0.10 and dy < size * 0.35 or dy < size * 0.10 and dx < size * 0.35:
                if diamond <= 1.25:
                    image[y, x] = (232, 220, 255)
    return image


def render_digit(digit: str, scale: int = 4) -> np.ndarray:
    pattern = DIGITS[digit]
    height = len(pattern) * scale
    width = len(pattern[0]) * scale
    image = np.zeros((height, width, 3), dtype=np.uint8)
    for row, line in enumerate(pattern):
        for col, value in enumerate(line):
            if value == "1":
                image[row * scale : (row + 1) * scale, col * scale : (col + 1) * scale] = (245, 244, 236)
    return image


def draw_patch(canvas: np.ndarray, patch: np.ndarray, left: int, top: int) -> None:
    height, width = patch.shape[:2]
    canvas[top : top + height, left : left + width, :3] = patch[:, :, :3]


def make_reward_sample() -> np.ndarray:
    canvas = np.zeros((360, 640, 3), dtype=np.uint8)
    canvas[:] = (26, 34, 42)
    canvas[0:80, :] = (36, 58, 68)
    canvas[260:, :] = (42, 46, 48)

    panel_left, panel_top = 360, 108
    canvas[panel_top - 8 : panel_top + 48, panel_left - 14 : panel_left + 124] = (52, 49, 60)
    canvas[panel_top - 6 : panel_top + 46, panel_left - 12 : panel_left + 122] = (74, 68, 82)
    icon = make_primogem_icon(32)
    draw_patch(canvas, icon, panel_left, panel_top)
    digit = render_digit("5", 4)
    draw_patch(canvas, digit, panel_left + 44, panel_top + 7)
    return canvas


def make_blank() -> np.ndarray:
    image = np.zeros((360, 640, 3), dtype=np.uint8)
    image[:] = (22, 27, 31)
    return image


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    templates = root / "templates"
    fixtures = root / "smoke_tests" / "fixtures"

    write_png(templates / "primogem" / "primogem_icon.png", make_primogem_icon())
    for digit in DIGITS:
        write_png(templates / "primogem" / "digits" / f"{digit}.png", render_digit(digit))
    write_png(templates / "reward_popup" / "reward_panel.png", make_reward_sample()[96:170, 340:506])
    write_png(templates / "chest_prompt" / "chest_prompt_placeholder.png", make_blank()[0:32, 0:96])
    write_png(templates / "oculus" / "oculus_placeholder.png", make_primogem_icon(28))

    write_png(fixtures / "primogem_reward_sample.png", make_reward_sample())
    write_png(fixtures / "blank.png", make_blank())
    (fixtures / "pins.json").write_text(
        json.dumps(
            {
                "pins": [
                    {"id": "chest-near", "kind": "chest", "title": "Common Chest", "x": 106, "y": 98, "mapId": 1},
                    {"id": "oculus-near", "kind": "oculus", "title": "Pyroculus", "x": 132, "y": 102, "mapId": 1},
                    {"id": "chest-far", "kind": "chest", "title": "Precious Chest", "x": 400, "y": 500, "mapId": 1},
                ]
            },
            indent=2,
        )
    )
    (templates / "README.md").write_text(
        "\n".join(
            [
                "# Templates",
                "",
                "Synthetic placeholders for offline smoke tests.",
                "",
                "Online visual references checked for ROI design:",
                "- Kongying/cvAutoTrack local docs and source place reward gain detections in the left/middle reward stack ROI.",
                "- Genshin gameplay videos and chest guides show Primogem gain toasts near the middle/right reward stack rather than a fixed pixel coordinate.",
                "- Chest/Primogem reference pages used for reward amounts and visual route/video links:",
                "  - https://genshin-impact.fandom.com/wiki/Chest",
                "  - https://genshin-impact.fandom.com/wiki/Primogem",
                "  - https://www.youtube.com/watch?v=i5CcIB8jBmQ",
                "",
                "Replace these placeholders with user-captured crops from your own screenshots for real use.",
            ]
        )
        + "\n"
    )
    print(f"Generated templates and fixtures under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
