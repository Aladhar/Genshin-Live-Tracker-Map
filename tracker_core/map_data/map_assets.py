from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from tracker_core.utils.paths import resolve_repo_path


REGION_PATTERNS = (
    ("DXKQMap", "mapimg_dxkqmap"),
    ("DXKQOutline", "mapimg_dxkqoutline"),
    ("JRZHMap", "mapimg_jrzhmap"),
    ("JRZHOutline", "mapimg_jrzhoutline"),
    ("LXSJMap", "mapimg_lxsjmap"),
    ("LXSJOutline", "mapimg_lxsjoutline"),
    ("MainMap", "mapimg_mainmap"),
    ("MapOutline", "mapimg_mapoutline"),
    ("QD28", "mapimg_qd28"),
    ("QunDaoMapAfter", "mapimg_qundaomap_after"),
    ("QunDaoOutline", "mapimg_qundaooutline"),
    ("QunDapMapBefore", "mapimg_qundapmap_before"),
    ("XMLK", "mapimg_xmlk"),
    ("XMLKOutline", "mapimg_xmlkoutline"),
    ("XMOverlay", "mapimg_xmoverlay"),
    ("YXGMap", "mapimg_yxgmap"),
    ("YXGOutline", "mapimg_yxgoutline"),
    ("OldMapSMBase", "old_map_sm_base"),
    ("OldMapSM", "old_map_sm"),
    ("OldMapSD", "old_map_sd"),
    ("OldMapSY", "old_map_sy"),
    ("OldMapYL", "old_map_yl"),
)

TILE_PATTERNS = (
    re.compile(r"^(?:Final_)?UI_MapBack_(-?\d+)_(-?\d+)$"),
    re.compile(r"^UI_MapBack_TheChasm_(-?\d+)_(-?\d+)$"),
    re.compile(r"^UI_Map_Penumbra_(-?\d+)_(-?\d+)$"),
    re.compile(r"^(-?\d+)_(-?\d+)$"),
    re.compile(r"^(\d+)-(\d+)$"),
)


@dataclass(frozen=True)
class MapImageAsset:
    path: Path
    repo_path: str
    category: str
    asset_name: str
    source_bundle: str | None
    region: str | None
    tile_x: int | None
    tile_y: int | None
    image_width: int | None
    image_height: int | None
    object_type: str | None = None

    @classmethod
    def from_processed_entry(cls, entry: dict[str, Any]) -> "MapImageAsset":
        output_path = str(entry.get("output_path", ""))
        asset_name = str(entry.get("asset_name") or Path(output_path).stem)
        tile_x, tile_y = parse_tile_coordinates(asset_name)
        source_bundle = entry.get("source_bundle")
        return cls(
            path=resolve_repo_path(output_path),
            repo_path=output_path,
            category=str(entry.get("category", "unknown_safe")),
            asset_name=asset_name,
            source_bundle=str(source_bundle) if source_bundle else None,
            region=parse_region(source_bundle or output_path, asset_name),
            tile_x=tile_x,
            tile_y=tile_y,
            image_width=_optional_int(entry.get("image_width")),
            image_height=_optional_int(entry.get("image_height")),
            object_type=str(entry.get("object_type")) if entry.get("object_type") else None,
        )

    @classmethod
    def from_path(cls, path: Path, category: str = "map_tile") -> "MapImageAsset":
        tile_x, tile_y = parse_tile_coordinates(path.stem)
        return cls(
            path=path,
            repo_path=path.as_posix(),
            category=category,
            asset_name=path.stem,
            source_bundle=None,
            region=parse_region(path.as_posix(), path.stem),
            tile_x=tile_x,
            tile_y=tile_y,
            image_width=None,
            image_height=None,
            object_type=None,
        )

    def global_pixel(self, local_x: float, local_y: float) -> tuple[float | None, float | None]:
        if self.tile_x is None or self.tile_y is None or self.image_width is None or self.image_height is None:
            return None, None
        return self.tile_x * self.image_width + local_x, self.tile_y * self.image_height + local_y

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["path"] = self.repo_path
        return payload


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_region(source_text: str, asset_name: str = "") -> str | None:
    normalized = source_text.replace("\\", "/").lower()
    for region, marker in REGION_PATTERNS:
        if marker in normalized:
            return region

    if "ui_mapback_thechasm" in asset_name.lower():
        return "DXKQMap"
    if "ui_map_penumbra" in asset_name.lower():
        return "LXSJMap"
    if "ui_mapback_" in asset_name.lower():
        return "MainMap"
    return None


def parse_tile_coordinates(asset_name: str) -> tuple[int | None, int | None]:
    for pattern in TILE_PATTERNS:
        match = pattern.match(asset_name)
        if not match:
            continue
        return int(match.group(1)), int(match.group(2))
    return None, None

