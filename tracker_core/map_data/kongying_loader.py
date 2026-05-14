from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tracker_core.map_data.map_assets import MapImageAsset
from tracker_core.map_data.kongying_import_policy import IMAGE_EXTENSIONS
from tracker_core.utils.paths import repo_root, resolve_repo_path


class KongYingDataError(RuntimeError):
    pass


class KongYingMapData:
    def __init__(
        self,
        manifest_path: str | Path = "data/kongying/manifest.json",
        processed_root: str | Path = "data/kongying/processed",
        processed_manifest_path: str | Path = "data/kongying/processed_manifest.json",
    ) -> None:
        self.manifest_path = resolve_repo_path(manifest_path)
        self.processed_root = resolve_repo_path(processed_root)
        self.processed_manifest_path = resolve_repo_path(processed_manifest_path)
        self.manifest = self._load_manifest()
        self.processed_manifest = self._load_processed_manifest()

    def _load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            raise KongYingDataError(
                f"KongYing manifest is missing: {self.manifest_path}. "
                "Run `python tools/import_kongying_assets.py` from the repo root."
            )

        try:
            with self.manifest_path.open("r", encoding="utf-8") as file_obj:
                return json.load(file_obj)
        except json.JSONDecodeError as exc:
            raise KongYingDataError(f"Invalid KongYing manifest JSON: {self.manifest_path}: {exc}") from exc

    def _load_processed_manifest(self) -> dict[str, Any]:
        if not self.processed_manifest_path.exists():
            return {}
        try:
            with self.processed_manifest_path.open("r", encoding="utf-8") as file_obj:
                return json.load(file_obj)
        except json.JSONDecodeError as exc:
            raise KongYingDataError(
                f"Invalid KongYing processed manifest JSON: {self.processed_manifest_path}: {exc}"
            ) from exc

    def list_regions(self) -> list[str]:
        regions: set[str] = set()

        for reference in self.manifest.get("asset_references", []):
            asset_path = reference.get("asset_path", "")
            match = re.search(r"/MapIMG/([^/]+)/", asset_path, flags=re.IGNORECASE)
            if match:
                regions.add(match.group(1))

        for asset in self.list_map_assets():
            text = f"{asset.get('repo_path', '')}/{asset.get('filename', '')}".lower()
            for region in ("mainmap", "dxkqmap", "jrzhmap", "lxsjmap", "xmlk", "qd28", "qundao", "yxg"):
                if region in text:
                    regions.add(region)

        return sorted(regions)

    def list_map_assets(self) -> list[dict[str, Any]]:
        return [
            entry
            for entry in self.manifest.get("files", [])
            if entry.get("category") in {"map_tile", "icon", "coordinate_data", "metadata"}
        ]

    def list_direct_image_assets(self, categories: set[str] | None = None) -> list[Path]:
        categories = categories or {"map_tile"}
        candidates: list[Path] = []
        for entry in self.manifest.get("files", []):
            if entry.get("category") in categories and entry.get("extension") in IMAGE_EXTENSIONS:
                candidates.append(resolve_repo_path(entry["repo_path"]))

        if self.processed_manifest:
            for entry in self.processed_manifest.get("files", []):
                if entry.get("category") not in categories:
                    continue
                path_text = entry.get("output_path")
                if not path_text:
                    continue
                path = resolve_repo_path(path_text)
                if path.exists() and path.suffix.lower() in IMAGE_EXTENSIONS:
                    candidates.append(path)
        elif self.processed_root.exists():
            for path in sorted(self.processed_root.rglob("*")):
                if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
                    candidates.append(path)

        return candidates

    def list_match_image_assets(
        self,
        categories: set[str] | None = None,
        exclude_keywords: tuple[str, ...] = ("outline", "overlay"),
    ) -> list[Path]:
        return [asset.path for asset in self.list_match_image_asset_records(categories, exclude_keywords)]

    def list_match_image_asset_records(
        self,
        categories: set[str] | None = None,
        exclude_keywords: tuple[str, ...] = ("outline", "overlay"),
    ) -> list[MapImageAsset]:
        candidates = self.list_direct_image_asset_records(categories=categories or {"map_tile"})
        if not exclude_keywords:
            return candidates

        filtered: list[MapImageAsset] = []
        lowered_keywords = tuple(keyword.lower() for keyword in exclude_keywords)
        for asset in candidates:
            path_text = asset.path.as_posix().lower()
            if any(keyword in path_text for keyword in lowered_keywords):
                continue
            filtered.append(asset)

        return filtered or candidates

    def list_direct_image_asset_records(self, categories: set[str] | None = None) -> list[MapImageAsset]:
        categories = categories or {"map_tile"}
        candidates: list[MapImageAsset] = []

        for entry in self.manifest.get("files", []):
            if entry.get("category") in categories and entry.get("extension") in IMAGE_EXTENSIONS:
                path = resolve_repo_path(entry["repo_path"])
                if path.exists():
                    candidates.append(MapImageAsset.from_path(path, category=str(entry.get("category", "map_tile"))))

        if self.processed_manifest:
            for entry in self.processed_manifest.get("files", []):
                if entry.get("category") not in categories:
                    continue
                path_text = entry.get("output_path")
                if not path_text:
                    continue
                path = resolve_repo_path(path_text)
                if path.exists() and path.suffix.lower() in IMAGE_EXTENSIONS:
                    candidates.append(MapImageAsset.from_processed_entry(entry))
        elif self.processed_root.exists():
            for path in sorted(self.processed_root.rglob("*")):
                if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
                    candidates.append(MapImageAsset.from_path(path))

        return candidates

    def find_metadata_files(self) -> list[dict[str, Any]]:
        return [entry for entry in self.manifest.get("files", []) if entry.get("category") == "metadata"]

    def get_metadata(self) -> dict[str, Any]:
        return {
            "manifest_path": self.manifest_path.as_posix(),
            "summary": self.manifest.get("summary", {}),
            "processed_summary": self.processed_manifest.get("summary", {}),
            "metadata_files": self.find_metadata_files(),
            "asset_references": self.manifest.get("asset_references", []),
            "regions": self.list_regions(),
        }

    def load_tile(self, path: str | Path) -> Any:
        resolved = resolve_repo_path(path)
        if not resolved.exists():
            raise KongYingDataError(f"Map asset not found: {resolved}")

        if resolved.suffix.lower() not in IMAGE_EXTENSIONS:
            raise KongYingDataError(
                f"Map asset is not a directly loadable image: {resolved}. "
                "Raw KongYing UnityFS bundles must be extracted into data/kongying/processed first."
            )

        try:
            from PIL import Image
        except ImportError as exc:
            raise KongYingDataError("Pillow is required to load map image assets.") from exc

        return Image.open(resolved).convert("RGB")

    def as_repo_relative(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(repo_root()).as_posix()
        except ValueError:
            return path.as_posix()


def load_default_kongying_data() -> KongYingMapData:
    return KongYingMapData()
