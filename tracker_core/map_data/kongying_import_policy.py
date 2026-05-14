from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

UNSAFE_EXTENSIONS = {
    ".exe",
    ".dll",
    ".bat",
    ".cmd",
    ".ps1",
    ".msi",
    ".scr",
    ".sys",
    ".pyd",
    ".so",
    ".dylib",
}

JUNK_FILENAMES = {".ds_store", "thumbs.db", "desktop.ini"}

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".gif",
    ".tif",
    ".tiff",
    ".ico",
}

TEXT_METADATA_EXTENSIONS = {
    ".json",
    ".yaml",
    ".yml",
    ".csv",
    ".txt",
    ".md",
    ".info",
    ".config",
    ".version",
    ".hash",
}

SMALL_BINARY_METADATA_EXTENSIONS = {".bytes"}

MAP_BUNDLE_MARKERS = (
    "mapimg",
    "mainmap",
    "mapback",
    "_map_",
    "_map-",
    "_map.",
    "_map",
    "old_map",
    "overlay",
    "outline",
    "layeredmap",
)

ICON_BUNDLE_MARKERS = (
    "sprite",
    "atlas",
    "poi",
    "simpleimg",
    "content_img",
    "uiraw_atlas",
)

EXCLUDED_BUNDLE_MARKERS = (
    "dll",
    "shader",
    "audio",
    "font",
    "scene",
    "prefab",
    "material",
    "animation",
    "gizmo",
    "vectrosity",
    "textmesh",
    "resource",
)


@dataclass(frozen=True)
class ImportDecision:
    should_copy: bool
    category: str
    reason: str


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_probably_map_bundle(path: Path) -> bool:
    name = path.name.lower()
    return any(marker in name for marker in MAP_BUNDLE_MARKERS)


def is_probably_icon_bundle(path: Path) -> bool:
    name = path.name.lower()
    return any(marker in name for marker in ICON_BUNDLE_MARKERS)


def is_excluded_bundle(path: Path) -> bool:
    name = path.name.lower()
    return any(marker in name for marker in EXCLUDED_BUNDLE_MARKERS)


def guess_category(path: Path) -> str:
    name = path.name.lower()
    path_text = path.as_posix().lower()
    ext = path.suffix.lower()

    if ext in IMAGE_EXTENSIONS:
        if any(marker in path_text for marker in ("map", "tile", "overlay", "outline")):
            return "map_tile"
        return "icon"

    if ext == ".bundle":
        if is_probably_map_bundle(path):
            return "map_tile"
        if is_probably_icon_bundle(path):
            return "icon"
        return "unknown_safe"

    if ext in TEXT_METADATA_EXTENSIONS or ext in SMALL_BINARY_METADATA_EXTENSIONS:
        if any(marker in name for marker in ("coord", "point", "position", "marker")):
            return "coordinate_data"
        return "metadata"

    return "unknown_safe"


def decide_import(path: Path) -> ImportDecision:
    ext = path.suffix.lower()
    name = path.name.lower()

    if name in JUNK_FILENAMES:
        return ImportDecision(False, "excluded", "junk_os_metadata")

    if ext in UNSAFE_EXTENSIONS:
        return ImportDecision(False, "excluded", "unsafe_executable_extension")

    if ext in IMAGE_EXTENSIONS:
        return ImportDecision(True, guess_category(path), "safe_image_asset")

    if ext in TEXT_METADATA_EXTENSIONS:
        return ImportDecision(True, guess_category(path), "safe_readable_metadata")

    if ext in SMALL_BINARY_METADATA_EXTENSIONS:
        return ImportDecision(True, guess_category(path), "package_manifest_metadata")

    if ext == ".bundle":
        if is_excluded_bundle(path):
            return ImportDecision(False, "excluded", "non_map_runtime_or_media_bundle")
        if is_probably_map_bundle(path) or is_probably_icon_bundle(path):
            return ImportDecision(True, guess_category(path), "inert_map_or_icon_unityfs_bundle")
        return ImportDecision(False, "excluded", "unclassified_unity_bundle")

    return ImportDecision(False, "excluded", "unsupported_or_runtime_binary")


def extract_printable_strings(payload: bytes, minimum_length: int = 4) -> list[str]:
    strings: list[str] = []
    current = bytearray()
    for value in payload:
        if 32 <= value <= 126:
            current.append(value)
        else:
            if len(current) >= minimum_length:
                strings.append(current.decode("ascii", errors="ignore"))
            current.clear()
    if len(current) >= minimum_length:
        strings.append(current.decode("ascii", errors="ignore"))
    return strings


ASSET_PATH_RE = re.compile(
    r"Assets/AssetRaw/[A-Za-z0-9_./& ()+\-]+?\.(?:png|jpg|jpeg|webp|spriteatlasv2|json|bytes)",
    re.IGNORECASE,
)


def extract_asset_references(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() != ".bytes" or not path.exists():
        return []

    payload = path.read_bytes()
    references: list[dict[str, str]] = []
    seen: set[str] = set()
    for text in extract_printable_strings(payload):
        for match in ASSET_PATH_RE.findall(text):
            normalized = match.strip()
            if normalized in seen:
                continue
            seen.add(normalized)
            references.append(
                {
                    "asset_path": normalized,
                    "extension": Path(normalized).suffix.lower(),
                    "category_guess": guess_category(Path(normalized)),
                }
            )
    return references

