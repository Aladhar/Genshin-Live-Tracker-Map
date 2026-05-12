"""Nearest-pin inference for reward detections and live map positions."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class MapPosition:
    x: float
    y: float
    map_id: int | None = None


@dataclass(frozen=True)
class MapPin:
    id: str
    x: float
    y: float
    kind: str
    map_id: int | None = None
    title: str = ""
    completed: bool = False


@dataclass(frozen=True)
class PinInference:
    pin: MapPin | None
    distance: float | None
    confidence: float
    action: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "pin": None
            if self.pin is None
            else {
                "id": self.pin.id,
                "kind": self.pin.kind,
                "title": self.pin.title,
                "x": self.pin.x,
                "y": self.pin.y,
                "mapId": self.pin.map_id,
            },
            "distance": None if self.distance is None else round(self.distance, 6),
            "confidence": round(self.confidence, 6),
            "action": self.action,
            "reason": self.reason,
        }


def load_pins(path: str | Path) -> list[MapPin]:
    data = json.loads(Path(path).read_text())
    records = data.get("pins", data) if isinstance(data, dict) else data
    return [parse_pin(record) for record in records]


def parse_pin(record: dict) -> MapPin:
    raw_position = record.get("position")
    if isinstance(raw_position, str) and "," in raw_position:
        x_text, y_text = raw_position.split(",", 1)
        x = float(x_text)
        y = float(y_text)
    else:
        x = float(record.get("x", record.get("lat", 0.0)))
        y = float(record.get("y", record.get("lng", 0.0)))

    title = str(record.get("title", record.get("markerTitle", record.get("name", ""))))
    kind = normalize_pin_kind(str(record.get("kind", record.get("type", ""))), title)
    map_id = record.get("mapId", record.get("map_id", record.get("areaId")))
    return MapPin(
        id=str(record.get("id", record.get("markerId", title or f"{x},{y}"))),
        x=x,
        y=y,
        kind=kind,
        map_id=int(map_id) if map_id is not None else None,
        title=title,
        completed=bool(record.get("completed", record.get("finished", False))),
    )


def normalize_pin_kind(raw_kind: str, title: str = "") -> str:
    text = f"{raw_kind} {title}".lower()
    if "oculus" in text or "神瞳" in text:
        return "oculus"
    if "chest" in text or "宝箱" in text:
        return "chest"
    return raw_kind.lower() or "unknown"


def distance(a: MapPosition, pin: MapPin) -> float:
    return math.hypot(a.x - pin.x, a.y - pin.y)


def choose_nearest_pin(
    position: MapPosition,
    pins: Iterable[MapPin],
    *,
    preferred_kinds: set[str] | None = None,
    max_distance: float = 85.0,
) -> tuple[MapPin | None, float | None]:
    preferred_kinds = preferred_kinds or {"chest", "oculus"}
    best_pin: MapPin | None = None
    best_distance: float | None = None

    for pin in pins:
        if pin.completed:
            continue
        if preferred_kinds and pin.kind not in preferred_kinds:
            continue
        if position.map_id is not None and pin.map_id is not None and position.map_id != pin.map_id:
            continue
        pin_distance = distance(position, pin)
        if pin_distance > max_distance:
            continue
        if best_distance is None or pin_distance < best_distance:
            best_pin = pin
            best_distance = pin_distance

    return best_pin, best_distance


def infer_likely_source(
    *,
    detection_confidence: float,
    detection_kind: str,
    amount: int | None,
    position: MapPosition | None,
    pins: Iterable[MapPin],
    max_distance: float = 85.0,
    auto_mark_threshold: float = 0.90,
) -> PinInference:
    if detection_confidence <= 0.0 or detection_kind == "none":
        return PinInference(None, None, 0.0, "none", "no reward detection")
    if position is None:
        return PinInference(None, None, detection_confidence * 0.35, "needs_review", "no current map position")

    preferred = {"chest"} if detection_kind == "primogem_reward" else {"chest", "oculus"}
    pin, pin_distance = choose_nearest_pin(position, pins, preferred_kinds=preferred, max_distance=max_distance)
    if pin is None or pin_distance is None:
        return PinInference(None, None, detection_confidence * 0.45, "needs_review", "no nearby eligible pin")

    proximity = max(0.0, 1.0 - pin_distance / max_distance)
    kind_bonus = 1.0
    if pin.kind == "chest" and detection_kind == "primogem_reward" and amount is not None:
        kind_bonus = 1.08
    confidence = min(1.0, detection_confidence * (0.60 + 0.40 * proximity) * kind_bonus)

    if confidence >= auto_mark_threshold:
        return PinInference(pin, pin_distance, confidence, "auto_mark_candidate", "high confidence nearest matching pin")
    return PinInference(pin, pin_distance, confidence, "needs_review", "confidence below auto-mark threshold")

