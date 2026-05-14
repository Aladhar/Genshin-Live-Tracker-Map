from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.build_kongying_manifest import build_manifest  # noqa: E402
from tracker_core.map_data.kongying_import_policy import decide_import  # noqa: E402


def copy_safe_assets(source_root: Path, raw_root: Path, dry_run: bool = False) -> dict[str, int]:
    if not source_root.exists():
        raise FileNotFoundError(f"KongYing source folder not found: {source_root}")

    stats = {"copied": 0, "skipped": 0, "excluded": 0}
    for source_path in sorted(path for path in source_root.rglob("*") if path.is_file()):
        decision = decide_import(source_path)
        if not decision.should_copy:
            stats["excluded"] += 1
            continue

        relative = source_path.relative_to(source_root)
        destination = raw_root / relative
        if destination.exists() and destination.stat().st_size == source_path.stat().st_size:
            stats["skipped"] += 1
            continue

        stats["copied"] += 1
        if dry_run:
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)

    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safely import KongYing map assets as data-only files.")
    parser.add_argument("--source", default="KongYingMap-RC1.0.1", help="Source KongYing folder.")
    parser.add_argument("--raw-root", default="data/kongying/raw", help="Destination for imported raw assets.")
    parser.add_argument("--manifest", default="data/kongying/manifest.json", help="Manifest output path.")
    parser.add_argument("--dry-run", action="store_true", help="Show counts without copying files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_root = (REPO_ROOT / args.source).resolve()
    raw_root = (REPO_ROOT / args.raw_root).resolve()
    manifest_path = (REPO_ROOT / args.manifest).resolve()

    stats = copy_safe_assets(source_root=source_root, raw_root=raw_root, dry_run=args.dry_run)
    manifest = build_manifest(source_root=source_root, raw_root=raw_root, manifest_path=manifest_path)
    print(
        json.dumps(
            {
                "dry_run": args.dry_run,
                "copy_stats": stats,
                "manifest": args.manifest,
                "summary": manifest["summary"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

