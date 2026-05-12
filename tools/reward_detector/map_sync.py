"""Kongying map/content reference check helper.

This module records the official sources used for this prototype and scans the
local vendored Kongying trees for the latest area/update names mentioned in the
official logs. GitHub repos are treated as source/dev references, not live data.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


OFFICIAL_SOURCES = [
    {
        "name": "Kongying docs",
        "url": "https://yuanshen.site/docs/en/",
        "role": "official product/docs source",
    },
    {
        "name": "Client hot update log",
        "url": "https://yuanshen.site/docs/en/blog/posts/hotupdatelog-client",
        "role": "official client/map/resource hot updates",
    },
    {
        "name": "Client release notes",
        "url": "https://yuanshen.site/docs/en/blog/posts/changelog-client",
        "role": "official client release notes",
    },
    {
        "name": "Kongying GitHub org",
        "url": "https://github.com/kongying-tavern",
        "role": "source/dev reference only",
    },
    {
        "name": "cvAutoTrack",
        "url": "https://github.com/GengGode/cvAutoTrack",
        "role": "source/dev reference for screenshot-only tracking",
    },
]


LATEST_CONTENT_TERMS = [
    {
        "term": "Hiisi Island",
        "source": "2025-09-10-35 hot update",
        "expected": "latest map/resources area in official hot update log",
    },
    {
        "term": "Lempo Isle",
        "source": "2025-09-10-35 hot update",
        "expected": "latest map/resources area in official hot update log",
    },
    {
        "term": "Paha Isle",
        "source": "2025-09-10-35 hot update",
        "expected": "latest map/resources area in official hot update log",
    },
    {
        "term": "Easybreeze Holiday Resort",
        "source": "2025-07-29-848 hot update",
        "expected": "new map/resources plus layered-map scaling controls",
    },
    {
        "term": "version 5.6",
        "source": "2025-05-07-118 hot update",
        "expected": "version 5.6 map/resources",
    },
    {
        "term": "layered map",
        "source": "web/client logs",
        "expected": "layered map references and controls",
    },
    {
        "term": "chest",
        "source": "map item categories",
        "expected": "chest item/pin references",
    },
    {
        "term": "oculus",
        "source": "map item categories",
        "expected": "oculus item/pin references",
    },
]


SCAN_ROOTS = (
    "external/docs/src/en",
    "external/docs/src/zh",
    "external/map_front_v3/src",
    "external/map_front_v3/public",
    "external/map_register_v3/src",
    "external/genshin-map-cloud",
)


@dataclass(frozen=True)
class TermStatus:
    term: str
    present: bool
    matches: list[str]
    source: str
    expected: str


def scan_term(root: Path, term: str) -> list[str]:
    matches: list[str] = []
    lowered = term.lower()
    for scan_root in SCAN_ROOTS:
        folder = root / scan_root
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {
                ".md",
                ".ts",
                ".js",
                ".vue",
                ".java",
                ".json",
                ".yml",
                ".yaml",
            }:
                continue
            try:
                text = path.read_text(errors="ignore")
            except OSError:
                continue
            if lowered in text.lower():
                matches.append(str(path.relative_to(root)))
                if len(matches) >= 12:
                    return matches
    return matches


def build_update_check(root: str | Path) -> dict:
    root = Path(root)
    statuses = []
    for item in LATEST_CONTENT_TERMS:
        matches = scan_term(root, item["term"])
        statuses.append(
            TermStatus(
                term=item["term"],
                present=bool(matches),
                matches=matches,
                source=item["source"],
                expected=item["expected"],
            )
        )

    missing = [status.term for status in statuses if not status.present]
    checklist = []
    if missing:
        checklist.append(f"Backfill local references for missing terms: {', '.join(missing)}.")
    checklist.extend(
        [
            "Fetch/export live Kongying area, item, icon, marker, and tile/plugin config data from official endpoints or client cache.",
            "Compare live export against local source tree before editing vendored repos.",
            "Verify newest areas include maps, layered maps, resources, chests, oculi, and hot-update metadata.",
            "Use GitHub repositories only to understand schemas and source behavior; do not treat repo age as live-data freshness.",
            "Keep any marker completion writes local/reviewable unless detection confidence is high.",
        ]
    )

    return {
        "officialSources": OFFICIAL_SOURCES,
        "status": [
            {
                "term": status.term,
                "present": status.present,
                "source": status.source,
                "expected": status.expected,
                "matches": status.matches,
            }
            for status in statuses
        ],
        "checklist": checklist,
    }


def write_report(report: dict, debug_dir: str | Path) -> tuple[Path, Path]:
    debug_dir = Path(debug_dir)
    debug_dir.mkdir(parents=True, exist_ok=True)
    json_path = debug_dir / "kongying_content_check.json"
    md_path = debug_dir / "kongying_content_check.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    lines = ["# Kongying Content Check", ""]
    lines.append("## Sources")
    for source in report["officialSources"]:
        lines.append(f"- {source['name']}: {source['url']} ({source['role']})")
    lines.extend(["", "## Local Term Scan"])
    for status in report["status"]:
        flag = "present" if status["present"] else "missing"
        lines.append(f"- {status['term']}: {flag} ({status['source']})")
    lines.extend(["", "## Update Checklist"])
    for item in report["checklist"]:
        lines.append(f"- {item}")
    md_path.write_text("\n".join(lines) + "\n")
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check local Kongying references against latest official log terms.")
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[2])
    parser.add_argument("--debug-dir", default=Path(__file__).resolve().parent / "debug_output")
    args = parser.parse_args(argv)

    report = build_update_check(args.repo_root)
    json_path, md_path = write_report(report, args.debug_dir)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

