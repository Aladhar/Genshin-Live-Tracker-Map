from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tracker_core.map_data.kongying_import_policy import sha256_file  # noqa: E402


TARGET_OBJECT_TYPES = {"Sprite", "Texture2D"}
DEFAULT_CATEGORIES = ("map_tile",)
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"KongYing manifest not found: {path}")
    with path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def sanitize_filename(value: str, fallback: str) -> str:
    name = value.strip() or fallback
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = re.sub(r"\s+", " ", name)
    name = name.rstrip(" .")
    if not name:
        name = fallback
    if name.upper() in WINDOWS_RESERVED_NAMES:
        name = f"_{name}"
    return name[:180]


def selected_bundle_entries(manifest: dict[str, Any], categories: set[str]) -> list[dict[str, Any]]:
    entries = []
    for entry in manifest.get("files", []):
        if entry.get("extension") != ".bundle":
            continue
        if entry.get("category") not in categories:
            continue
        entries.append(entry)
    return entries


def image_from_object(obj: Any) -> tuple[str, Any] | None:
    data = obj.read()
    image = getattr(data, "image", None)
    if image is None:
        return None
    asset_name = getattr(data, "m_Name", None) or getattr(data, "name", None) or ""
    return str(asset_name), image


def save_image(image: Any, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def extract_bundle(
    entry: dict[str, Any],
    output_root: Path,
    overwrite: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    try:
        import UnityPy
    except ImportError as exc:
        raise RuntimeError("UnityPy is required. Install dependencies with `pip install -r requirements.txt`.") from exc

    bundle_path = REPO_ROOT / entry["repo_path"]
    category = entry.get("category", "unknown_safe")
    bundle_stem = sanitize_filename(bundle_path.stem, fallback="bundle")
    bundle_output_dir = output_root / category / bundle_stem
    extracted: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    seen_images: set[tuple[str, tuple[int, int], str]] = set()
    used_names: Counter[str] = Counter()

    try:
        env = UnityPy.load(bundle_path.as_posix())
        objects = sorted(
            [obj for obj in env.objects if obj.type.name in TARGET_OBJECT_TYPES],
            key=lambda obj: (0 if obj.type.name == "Sprite" else 1, str(getattr(obj, "path_id", ""))),
        )
    except Exception as exc:
        return [], [{"bundle": entry["repo_path"], "error": f"bundle_load_failed: {exc}"}]

    for obj in objects:
        try:
            image_result = image_from_object(obj)
            if image_result is None:
                continue
            asset_name, image = image_result
            image_size = tuple(int(value) for value in getattr(image, "size", (0, 0)))
            image_mode = str(getattr(image, "mode", "unknown"))
            object_type = str(obj.type.name)
            path_id = str(getattr(obj, "path_id", "unknown"))
            safe_name = sanitize_filename(asset_name, fallback=f"{object_type}_{path_id}")
            duplicate_key = (safe_name, image_size, image_mode)
            if duplicate_key in seen_images:
                continue
            seen_images.add(duplicate_key)

            used_names[safe_name] += 1
            suffix = "" if used_names[safe_name] == 1 else f"__{object_type}_{path_id}"
            output_path = bundle_output_dir / f"{safe_name}{suffix}.png"
            if output_path.exists() and not overwrite:
                status = "existing"
            else:
                save_image(image, output_path)
                status = "extracted"

            extracted.append(
                {
                    "source_bundle": entry["repo_path"],
                    "source_sha256": entry.get("sha256"),
                    "category": category,
                    "object_type": object_type,
                    "path_id": path_id,
                    "asset_name": asset_name or safe_name,
                    "image_width": image_size[0],
                    "image_height": image_size[1],
                    "image_mode": image_mode,
                    "output_path": repo_relative(output_path),
                    "output_sha256": sha256_file(output_path) if output_path.exists() else None,
                    "status": status,
                }
            )
        except Exception as exc:
            errors.append(
                {
                    "bundle": entry["repo_path"],
                    "object_type": str(getattr(getattr(obj, "type", None), "name", "unknown")),
                    "path_id": str(getattr(obj, "path_id", "unknown")),
                    "error": str(exc),
                }
            )

    return extracted, errors


def extract_textures(
    manifest_path: Path,
    output_root: Path,
    processed_manifest_path: Path,
    categories: set[str],
    max_bundles: int | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    entries = selected_bundle_entries(manifest, categories)
    if max_bundles is not None:
        entries = entries[:max_bundles]

    extracted_files: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for index, entry in enumerate(entries, start=1):
        print(f"[{index}/{len(entries)}] extracting {entry['repo_path']}", flush=True)
        extracted, bundle_errors = extract_bundle(entry, output_root=output_root, overwrite=overwrite)
        extracted_files.extend(extracted)
        errors.extend(bundle_errors)
        print(f"  extracted {len(extracted)} images, errors {len(bundle_errors)}", flush=True)

    summary = {
        "bundle_count": len(entries),
        "image_count": len(extracted_files),
        "error_count": len(errors),
        "category_counts": dict(Counter(item["category"] for item in extracted_files)),
        "object_type_counts": dict(Counter(item["object_type"] for item in extracted_files)),
    }
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest_path": repo_relative(manifest_path),
        "output_root": repo_relative(output_root),
        "categories": sorted(categories),
        "summary": summary,
        "files": extracted_files,
        "errors": errors,
    }

    processed_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with processed_manifest_path.open("w", encoding="utf-8") as file_obj:
        json.dump(payload, file_obj, indent=2, ensure_ascii=False)
        file_obj.write("\n")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract PNG textures from imported KongYing UnityFS bundles.")
    parser.add_argument("--manifest", default="data/kongying/manifest.json", help="KongYing raw import manifest.")
    parser.add_argument("--output-root", default="data/kongying/processed", help="Processed PNG output directory.")
    parser.add_argument(
        "--processed-manifest",
        default="data/kongying/processed_manifest.json",
        help="Processed extraction manifest output path.",
    )
    parser.add_argument(
        "--category",
        action="append",
        choices=("map_tile", "icon"),
        help="Category to extract. Repeatable. Defaults to map_tile only.",
    )
    parser.add_argument("--include-icons", action="store_true", help="Also extract icon/sprite/atlas bundles.")
    parser.add_argument("--max-bundles", type=int, default=None, help="Limit bundle count for a test run.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing PNG outputs.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    categories = set(args.category or DEFAULT_CATEGORIES)
    if args.include_icons:
        categories.add("icon")

    payload = extract_textures(
        manifest_path=(REPO_ROOT / args.manifest).resolve(),
        output_root=(REPO_ROOT / args.output_root).resolve(),
        processed_manifest_path=(REPO_ROOT / args.processed_manifest).resolve(),
        categories=categories,
        max_bundles=args.max_bundles,
        overwrite=args.overwrite,
    )
    print(json.dumps({"processed_manifest": args.processed_manifest, "summary": payload["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

