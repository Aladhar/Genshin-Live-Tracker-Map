"""Fetch and summarize Kongying's official live public map config.

This sync deliberately uses official Kongying public surfaces:

- https://assets.yuanshen.site/webapp.json for live map/tile/plugin config.
- https://cloud.yuanshen.site/api/* read endpoints for marker/item data.

The API endpoints currently require a bearer token. This script records that as
an explicit blocker instead of inventing marker data from GitHub source code.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


WEBAPP_URL = "https://assets.yuanshen.site/webapp.json"
API_BASE = "https://cloud.yuanshen.site/api"
DOCS_HOME_EN = "https://yuanshen.site/docs/en/"
DOCS_HOME_ZH = "https://yuanshen.site/docs/"
CLIENT_CHANGELOG_ZH = "https://yuanshen.site/docs/blog/posts/changelog-client"
HOT_UPDATE_ZH = "https://yuanshen.site/docs/blog/posts/hotupdatelog-client"
WEB_CHANGELOG_ZH = "https://yuanshen.site/docs/blog/posts/changelog-web"
GITHUB_ORG = "https://github.com/kongying-tavern"
API_PROBES = {
    "area.list": ("POST", "/area/get/list", {"parentId": -1, "isTraverse": 1}),
    "item_type.list_all": ("POST", "/item_type/get/list_all", {}),
    "item.list": ("POST", "/item/get/list", {"current": 0, "size": 1}),
    "icon.list": ("POST", "/icon/get/list", {"current": 0, "size": 1}),
    "marker_doc.md5": ("GET", "/marker_doc/list_page_bin_md5", None),
}


LATEST_PUBLIC_CONFIG_TERMS = [
    "A:MD:SHENDIAN",
    "A:MD:FENGXISHAN",
    "空之神殿",
    "远古圣山",
    "FAVONIUS_KNIGHT_RUIN",
    "https://tiles.yuanshen.site/d/underground/6.5/",
    "https://tiles.yuanshen.site/d/underground/6.3/",
    "https://tiles.yuanshen.site/d/underground/6.2/",
    "https://tiles.yuanshen.site/d/underground/6.0/",
    "伦波岛",
    "希汐岛",
    "帕哈岛",
    "HIISI_ISLAND",
    "LEMPO_ISLAND",
    "PAHA_ISLE",
    "A:NDKL:NDKL",
    "A:NDKL:NDKL2",
]

OFFICIAL_LOG_COVERAGE = [
    {
        "id": "hotfix-2026-04-07-6.5",
        "date": "2026-04-07",
        "source": HOT_UPDATE_ZH,
        "note": "Kongying hot update says 6.5 resources and some base-map resources were updated.",
        "terms": ["https://tiles.yuanshen.site/d/underground/6.5/", "A:MD:SHENDIAN", "A:MD:FENGXISHAN"],
    },
    {
        "id": "hotfix-2026-04-08-sky-temple-library",
        "date": "2026-04-08",
        "source": HOT_UPDATE_ZH,
        "note": "Kongying hot update says Sky Temple library layered resources were updated.",
        "terms": ["空之神殿", "MAHAVAIPULYA_CHAMBER_LIB_FL4", "MAHAVAIPULYA_CHAMBER_LIB_FL1"],
    },
    {
        "id": "hotfix-2026-04-09-ancient-sacred-mountain",
        "date": "2026-04-09",
        "source": HOT_UPDATE_ZH,
        "note": "Kongying hot update references Ancient Sacred Mountain cloud/resource fixes.",
        "terms": ["远古圣山", "ANCIENT_SACRED_MT", "SACRED_MT_HEART"],
    },
    {
        "id": "client-2025-12-03-6.2-layer",
        "date": "2025-12-03",
        "source": CLIENT_CHANGELOG_ZH,
        "note": "Kongying client changelog says one 6.2 underground layer was added.",
        "terms": ["https://tiles.yuanshen.site/d/underground/6.2/"],
    },
    {
        "id": "hotfix-2025-09-10-6.0-nod-krai",
        "date": "2025-09-10",
        "source": HOT_UPDATE_ZH,
        "note": "Kongying hot update says 6.0 regions/resources were added.",
        "terms": ["A:NDKL:NDKL", "伦波岛", "希汐岛", "帕哈岛", "LEMPO_ISLAND", "HIISI_ISLAND", "PAHA_ISLE"],
    },
    {
        "id": "web-2025-09-10-nod-krai-icon",
        "date": "2025-09-10",
        "source": WEB_CHANGELOG_ZH,
        "note": "Kongying web changelog says the Nod-Krai icon was added.",
        "terms": ["A:NDKL:NDKL", "A:NDKL:NDKL2"],
    },
    {
        "id": "hotfix-2025-07-29-5.8",
        "date": "2025-07-29",
        "source": HOT_UPDATE_ZH,
        "note": "Kongying hot update says 5.8 regions/resources were added.",
        "terms": ["A:NT:NATA5", "https://tiles.yuanshen.site/d/underground/5.8/"],
    },
]

AUTH_GATED_LOG_SIGNALS = [
    {
        "id": "web-2026-01-06-new-point-api",
        "date": "2026-01-06",
        "source": WEB_CHANGELOG_ZH,
        "note": "Kongying web changelog says point acquisition now supports the new point data API.",
        "requiredApiProbe": "item.list",
    },
    {
        "id": "hotfix-2026-01-14-moon-four-resources",
        "date": "2026-01-14",
        "source": HOT_UPDATE_ZH,
        "note": "Kongying hot update says Moon IV related resources were updated; these are not exposed in public webapp tile config.",
        "requiredApiProbe": "item.list",
    },
    {
        "id": "live-marker-item-icon-export",
        "date": "latest",
        "source": API_BASE,
        "note": "Chest, oculus, item, icon, and marker parity requires official marker/item/icon endpoints or an official client cache/export.",
        "requiredApiProbe": "marker_doc.md5",
    },
]


@dataclass(frozen=True)
class ProbeResult:
    name: str
    method: str
    path: str
    status: int | None
    ok: bool
    reason: str


def fetch_json(url: str, *, token: str | None = None, timeout: int = 30) -> Any:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def request_api(
    method: str,
    path: str,
    payload: dict[str, Any] | None,
    *,
    token: str | None,
    timeout: int = 30,
) -> tuple[int, bytes]:
    headers = {"Accept": "application/json"}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"{API_BASE}{path}", data=data, headers=headers, method=method)
    with urlopen(request, timeout=timeout) as response:
        return response.status, response.read()


def probe_api(token: str | None = None) -> list[ProbeResult]:
    results: list[ProbeResult] = []
    for name, (method, path, payload) in API_PROBES.items():
        try:
            status, _body = request_api(method, path, payload, token=token)
            results.append(ProbeResult(name, method, path, status, status == 200, "ok"))
        except HTTPError as exc:
            reason = "requires authorization" if exc.code in (401, 403) and token is None else exc.reason
            results.append(ProbeResult(name, method, path, exc.code, False, reason))
        except URLError as exc:
            results.append(ProbeResult(name, method, path, None, False, str(exc.reason)))
    return results


def summarize_webapp(webapp: dict[str, Any]) -> dict[str, Any]:
    tiles = webapp.get("tiles", {})
    plugins = webapp.get("plugins", {})
    tile_entries = []
    overlay_entries = []

    for key, value in tiles.items():
        tile_entries.append(
            {
                "key": key,
                "name": value.get("name", ""),
                "code": value.get("code", ""),
                "extend": value.get("extend", ""),
                "center": value.get("center") or value.get("settings", {}).get("center"),
                "size": value.get("size"),
                "tilesOffset": value.get("tilesOffset"),
                "extension": value.get("extension", "png"),
            }
        )

    for key, plugin in plugins.items():
        overlay_config = plugin.get("overlayConfig") or {}
        overlays = overlay_config.get("overlays") or []
        overlay_count = 0
        chunk_count = 0
        labels: list[str] = []
        values: list[str] = []
        for group in overlays:
            labels.append(str(group.get("label", "")))
            values.append(str(group.get("value", "")))
            for child in group.get("children", []) or []:
                overlay_count += 1
                labels.append(str(child.get("label", "")))
                values.append(str(child.get("value", "")))
                chunk_count += len(child.get("chunks", []) or [])

        overlay_entries.append(
            {
                "key": key,
                "hasUnderground": "underground" in (plugin.get("extra") or []),
                "hasOverlay": bool(plugin.get("overlay")),
                "urlTemplate": overlay_config.get("urlTemplate", ""),
                "overlayGroups": len(overlays),
                "overlayItems": overlay_count,
                "chunks": chunk_count,
                "labels": [label for label in labels if label],
                "values": [value for value in values if value],
            }
        )

    searchable = json.dumps(webapp, ensure_ascii=False).lower()
    term_status = {
        term: (term.lower() in searchable)
        for term in LATEST_PUBLIC_CONFIG_TERMS
    }
    log_coverage = []
    for signal in OFFICIAL_LOG_COVERAGE:
        terms = signal["terms"]
        terms_present = {term: (term.lower() in searchable) for term in terms}
        log_coverage.append(
            {
                "id": signal["id"],
                "date": signal["date"],
                "source": signal["source"],
                "note": signal["note"],
                "present": all(terms_present.values()),
                "terms": terms_present,
            }
        )

    return {
        "source": WEBAPP_URL,
        "tileCount": len(tile_entries),
        "pluginCount": len(overlay_entries),
        "tiles": tile_entries,
        "overlays": overlay_entries,
        "latestOfficialTermStatus": term_status,
        "officialLogCoverage": log_coverage,
    }


def write_outputs(
    *,
    webapp: dict[str, Any],
    summary: dict[str, Any],
    probes: list[ProbeResult],
    output_dir: Path,
) -> tuple[Path, Path, Path, Path]:
    data_dir = output_dir / "data"
    report_dir = output_dir / "reports"
    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    webapp_path = data_dir / "webapp.json"
    summary_path = data_dir / "map_summary.json"
    report_json_path = report_dir / "live_map_sync_report.json"
    report_md_path = report_dir / "live_map_sync_report.md"

    webapp_path.write_text(json.dumps(webapp, indent=2, ensure_ascii=False) + "\n")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    report = {
        "officialSources": {
            "webapp": WEBAPP_URL,
            "apiBase": API_BASE,
            "docsEnglish": DOCS_HOME_EN,
            "docsChinese": DOCS_HOME_ZH,
            "clientChangelog": CLIENT_CHANGELOG_ZH,
            "hotUpdateLog": HOT_UPDATE_ZH,
            "webChangelog": WEB_CHANGELOG_ZH,
            "githubOrgDevReferenceOnly": GITHUB_ORG,
        },
        "publicConfigSynced": True,
        "tileCount": summary["tileCount"],
        "pluginCount": summary["pluginCount"],
        "latestOfficialTermStatus": summary["latestOfficialTermStatus"],
        "officialLogCoverage": summary["officialLogCoverage"],
        "authGatedLogSignals": AUTH_GATED_LOG_SIGNALS,
        "apiProbeResults": [probe.__dict__ for probe in probes],
        "verificationLimit": (
            "Public webapp tile/layer config was synced. Full item/pin/marker parity cannot be "
            "claimed without an official authenticated export or client cache, because live API "
            "read endpoints returned authorization errors without a bearer token."
        ),
    }
    report_json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Kongying Live Map Sync Report",
        "",
        "## Official Sources",
        f"- Public webapp config: {WEBAPP_URL}",
        f"- Live API base: {API_BASE}",
        f"- Docs EN: {DOCS_HOME_EN}",
        f"- Docs ZH: {DOCS_HOME_ZH}",
        f"- Client changelog: {CLIENT_CHANGELOG_ZH}",
        f"- Hot update log: {HOT_UPDATE_ZH}",
        f"- Web changelog: {WEB_CHANGELOG_ZH}",
        f"- GitHub org: {GITHUB_ORG} (source/dev reference only)",
        "",
        "## Synced Public Config",
        f"- Tiles: {summary['tileCount']}",
        f"- Plugin configs: {summary['pluginCount']}",
        "",
        "## Latest-Term Coverage",
    ]
    for term, present in summary["latestOfficialTermStatus"].items():
        lines.append(f"- {term}: {'present' if present else 'missing'}")

    lines.extend(["", "## Official Log Cross-Reference"])
    for signal in summary["officialLogCoverage"]:
        state = "covered" if signal["present"] else "missing"
        lines.append(f"- {signal['date']} {signal['id']}: {state}")
        lines.append(f"  - Source: {signal['source']}")
        lines.append(f"  - Note: {signal['note']}")

    lines.extend(["", "## Auth-Gated Map/Item Signals"])
    for signal in AUTH_GATED_LOG_SIGNALS:
        lines.append(f"- {signal['date']} {signal['id']}: needs authenticated export/API access")
        lines.append(f"  - Source: {signal['source']}")
        lines.append(f"  - Note: {signal['note']}")

    lines.extend(["", "## API Probe Results"])
    for probe in probes:
        status = probe.status if probe.status is not None else "network-error"
        lines.append(f"- {probe.name} {probe.method} {probe.path}: {status} ({probe.reason})")

    lines.extend(
        [
            "",
            "## Verification Limit",
            report["verificationLimit"],
            "",
            "## Update Checklist",
            "- Treat `data/webapp.json` as the latest public official tile/layer config snapshot.",
            "- Use `data/map_summary.json` for region/layer comparison in tools.",
            "- For 100% marker/item/pin parity, import an official authenticated export or local client cache; do not infer live pins from GitHub alone.",
            "- Re-run this tool with `KONGYING_TOKEN` only if you have an official token you are allowed to use locally.",
            "- After importing authenticated marker data, rerun nearest-pin smoke tests against the exported chest/oculus candidate set.",
        ]
    )
    report_md_path.write_text("\n".join(lines) + "\n")
    return webapp_path, summary_path, report_json_path, report_md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync Kongying official live public map config.")
    parser.add_argument("--offline-webapp", type=Path, help="Use an already fetched webapp.json instead of network.")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument(
        "--token-env",
        default="KONGYING_TOKEN",
        help="Optional env var containing a Kongying bearer token for API probes/exports.",
    )
    args = parser.parse_args(argv)

    if args.offline_webapp:
        webapp = json.loads(args.offline_webapp.read_text())
    else:
        webapp = fetch_json(WEBAPP_URL)

    token = os.environ.get(args.token_env)
    probes = probe_api(token)
    summary = summarize_webapp(webapp)
    paths = write_outputs(webapp=webapp, summary=summary, probes=probes, output_dir=args.output_dir)
    for path in paths:
        print(path)
    blocked = [probe for probe in probes if probe.status in (401, 403)]
    return 2 if blocked and token else 0


if __name__ == "__main__":
    raise SystemExit(main())
