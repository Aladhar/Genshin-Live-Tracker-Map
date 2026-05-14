from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return repo_root() / candidate


def ensure_dir(path: str | Path) -> Path:
    resolved = resolve_repo_path(path)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def load_json(path: str | Path) -> dict[str, Any]:
    resolved = resolve_repo_path(path)
    try:
        with resolved.open("r", encoding="utf-8") as file_obj:
            return json.load(file_obj)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"JSON file not found: {resolved}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {resolved}: {exc}") from exc


def write_json(path: str | Path, payload: Any) -> Path:
    resolved = resolve_repo_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as file_obj:
        json.dump(payload, file_obj, indent=2, ensure_ascii=False)
        file_obj.write("\n")
    return resolved

