"""One-shot reward detection plus nearest-pin suggestion CLI."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .capture import DEFAULT_REWARD_ROI, PixelRegion, capture_screenshot, crop, parse_relative_region
from .image_io import load_png, write_png
from .nearest_pin import MapPosition, infer_likely_source, load_pins
from .primogem_detector import default_templates_dir, detect_primogem_reward


def parse_position(value: str) -> MapPosition:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) not in (2, 3):
        raise argparse.ArgumentTypeError("position must be x,y or x,y,mapId")
    return MapPosition(float(parts[0]), float(parts[1]), int(parts[2]) if len(parts) == 3 else None)


def load_position_json(path: str | Path) -> MapPosition | None:
    data = json.loads(Path(path).read_text())
    if "tracker" in data:
        tracker = data["tracker"]
        if not tracker.get("available", False):
            return None
        position = tracker.get("position", {})
        return MapPosition(float(position["x"]), float(position["y"]), position.get("mapId"))
    if {"x", "y"}.issubset(data):
        return MapPosition(float(data["x"]), float(data["y"]), data.get("mapId", data.get("map_id")))
    return None


def run_once(
    *,
    image_path: str | Path | None,
    pins_path: str | Path | None,
    position: MapPosition | None,
    templates_dir: str | Path | None = None,
    debug_dir: str | Path | None = None,
    roi=None,
) -> dict:
    if image_path:
        image = load_png(image_path)
    else:
        image = capture_screenshot()

    roi = roi or DEFAULT_REWARD_ROI
    detection = detect_primogem_reward(image, templates_dir=templates_dir, roi=roi)
    pins = load_pins(pins_path) if pins_path else []
    inference = infer_likely_source(
        detection_confidence=detection.confidence if detection.detected else 0.0,
        detection_kind=detection.kind,
        amount=detection.amount,
        position=position,
        pins=pins,
    )

    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "safety": "screenshot-only; no memory reads, injection, gameplay automation, or account upload",
        "detection": detection.to_dict(),
        "position": None
        if position is None
        else {"x": position.x, "y": position.y, "mapId": position.map_id},
        "pinInference": inference.to_dict(),
    }

    if debug_dir:
        debug_path = Path(debug_dir)
        debug_path.mkdir(parents=True, exist_ok=True)
        (debug_path / "last_detection.json").write_text(json.dumps(record, indent=2))
        if detection.roi is not None:
            write_png(debug_path / "last_reward_roi.png", crop(image, detection.roi))

    return record


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect Primogem/reward popups and suggest nearest map pin.")
    parser.add_argument("--image", help="PNG screenshot to analyze; omitted means live screen capture")
    parser.add_argument("--pins", help="JSON pin list to search")
    parser.add_argument("--position", type=parse_position, help="current map position as x,y or x,y,mapId")
    parser.add_argument("--position-json", help="JSON from cvAutoTrack/Kongying-style tracker")
    parser.add_argument("--templates-dir", default=default_templates_dir(), help="template root")
    parser.add_argument("--debug-dir", default=Path(__file__).resolve().parent / "debug_output")
    parser.add_argument("--roi", type=parse_relative_region, help="relative ROI x,y,width,height")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    position = args.position
    if args.position_json:
        position = load_position_json(args.position_json)
    record = run_once(
        image_path=args.image,
        pins_path=args.pins,
        position=position,
        templates_dir=args.templates_dir,
        debug_dir=args.debug_dir,
        roi=args.roi,
    )
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

