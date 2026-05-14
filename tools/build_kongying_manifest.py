from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tracker_core.map_data.kongying_import_policy import (  # noqa: E402
    IMAGE_EXTENSIONS,
    SMALL_BINARY_METADATA_EXTENSIONS,
    TEXT_METADATA_EXTENSIONS,
    UNSAFE_EXTENSIONS,
    decide_import,
    extract_asset_references,
    sha256_file,
)


def rel_to_repo(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def build_manifest(
    source_root: Path,
    raw_root: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    source_root = source_root.resolve()
    raw_root = raw_root.resolve()
    manifest_path = manifest_path.resolve()

    files: list[dict[str, Any]] = []
    excluded_files: list[dict[str, Any]] = []
    asset_references: list[dict[str, str]] = []

    if not source_root.exists():
        raise FileNotFoundError(f"KongYing source folder not found: {source_root}")

    for source_path in sorted(path for path in source_root.rglob("*") if path.is_file()):
        relative = source_path.relative_to(source_root)
        decision = decide_import(source_path)
        size = source_path.stat().st_size

        if decision.should_copy:
            repo_path = raw_root / relative
            entry = {
                "original_path": source_path.as_posix(),
                "repo_path": rel_to_repo(repo_path),
                "filename": source_path.name,
                "extension": source_path.suffix.lower() or "[no_ext]",
                "file_size": size,
                "sha256": sha256_file(repo_path if repo_path.exists() else source_path),
                "category": decision.category,
                "import_reason": decision.reason,
                "copied": repo_path.exists(),
            }
            files.append(entry)
            if source_path.suffix.lower() == ".bytes":
                for reference in extract_asset_references(source_path):
                    reference["manifest_file"] = relative.as_posix()
                    asset_references.append(reference)
        else:
            excluded_files.append(
                {
                    "original_path": source_path.as_posix(),
                    "filename": source_path.name,
                    "extension": source_path.suffix.lower() or "[no_ext]",
                    "file_size": size,
                    "category": decision.category,
                    "reason": decision.reason,
                }
            )

    category_counts = Counter(entry["category"] for entry in files)
    excluded_reason_counts = Counter(entry["reason"] for entry in excluded_files)
    extension_counts = Counter(entry["extension"] for entry in files)

    manifest = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_root": source_root.as_posix(),
        "raw_root": rel_to_repo(raw_root),
        "import_policy": {
            "unsafe_extensions": sorted(UNSAFE_EXTENSIONS),
            "safe_image_extensions": sorted(IMAGE_EXTENSIONS),
            "safe_metadata_extensions": sorted(TEXT_METADATA_EXTENSIONS),
            "small_binary_metadata_extensions": sorted(SMALL_BINARY_METADATA_EXTENSIONS),
            "notes": [
                "Executable/runtime files are never copied or executed.",
                "UnityFS .bundle files are copied only when their names indicate map, overlay, outline, sprite, atlas, or POI assets.",
                "UnityFS bundles remain inert raw data until a later extraction step creates processed image files.",
            ],
        },
        "summary": {
            "source_file_count": len(files) + len(excluded_files),
            "copied_file_count": sum(1 for entry in files if entry["copied"]),
            "importable_file_count": len(files),
            "excluded_file_count": len(excluded_files),
            "imported_total_bytes": sum(entry["file_size"] for entry in files),
            "category_counts": dict(sorted(category_counts.items())),
            "extension_counts": dict(sorted(extension_counts.items())),
            "excluded_reason_counts": dict(sorted(excluded_reason_counts.items())),
            "asset_reference_count": len(asset_references),
        },
        "files": files,
        "asset_references": asset_references,
        "excluded_files": excluded_files,
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as file_obj:
        json.dump(manifest, file_obj, indent=2, ensure_ascii=False)
        file_obj.write("\n")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the KongYing import manifest.")
    parser.add_argument("--source", default="KongYingMap-RC1.0.1", help="Source KongYing folder.")
    parser.add_argument("--raw-root", default="data/kongying/raw", help="Imported raw asset folder.")
    parser.add_argument("--manifest", default="data/kongying/manifest.json", help="Manifest output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = build_manifest(
        source_root=(REPO_ROOT / args.source),
        raw_root=(REPO_ROOT / args.raw_root),
        manifest_path=(REPO_ROOT / args.manifest),
    )
    print(
        json.dumps(
            {
                "manifest": args.manifest,
                "importable_file_count": manifest["summary"]["importable_file_count"],
                "copied_file_count": manifest["summary"]["copied_file_count"],
                "excluded_file_count": manifest["summary"]["excluded_file_count"],
                "asset_reference_count": manifest["summary"]["asset_reference_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

