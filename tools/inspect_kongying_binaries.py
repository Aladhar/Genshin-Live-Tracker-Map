from __future__ import annotations

import argparse
import json
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tracker_core.map_data.kongying_import_policy import UNSAFE_EXTENSIONS, sha256_file  # noqa: E402


MACHINE_TYPES = {
    0x014C: "x86",
    0x0200: "Intel Itanium",
    0x8664: "x64",
    0xAA64: "ARM64",
}


def read_c_string(payload: bytes, offset: int, limit: int = 512) -> str:
    if offset < 0 or offset >= len(payload):
        return ""
    end = payload.find(b"\x00", offset, min(len(payload), offset + limit))
    if end == -1:
        end = min(len(payload), offset + limit)
    return payload[offset:end].decode("ascii", errors="replace")


def rva_to_offset(rva: int, sections: list[dict[str, int | str]]) -> int | None:
    for section in sections:
        virtual_address = int(section["virtual_address"])
        virtual_size = int(section["virtual_size"])
        raw_size = int(section["raw_size"])
        raw_pointer = int(section["raw_pointer"])
        span = max(virtual_size, raw_size)
        if virtual_address <= rva < virtual_address + span:
            return raw_pointer + (rva - virtual_address)
    return None


def parse_pe(payload: bytes) -> dict[str, Any]:
    if len(payload) < 0x40 or payload[:2] != b"MZ":
        return {"format": "unknown", "error": "missing_mz_header"}

    pe_offset = struct.unpack_from("<I", payload, 0x3C)[0]
    if pe_offset + 24 >= len(payload) or payload[pe_offset : pe_offset + 4] != b"PE\x00\x00":
        return {"format": "unknown", "error": "missing_pe_header"}

    file_header_offset = pe_offset + 4
    machine, section_count, timestamp, _, _, optional_header_size, characteristics = struct.unpack_from(
        "<HHIIIHH", payload, file_header_offset
    )
    optional_offset = file_header_offset + 20
    magic = struct.unpack_from("<H", payload, optional_offset)[0]
    is_pe32_plus = magic == 0x20B

    if magic not in {0x10B, 0x20B}:
        return {"format": "pe", "error": f"unsupported_optional_header_magic_{magic:#x}"}

    address_of_entry_point = struct.unpack_from("<I", payload, optional_offset + 16)[0]
    image_base_offset = optional_offset + (24 if is_pe32_plus else 28)
    image_base = struct.unpack_from("<Q" if is_pe32_plus else "<I", payload, image_base_offset)[0]
    subsystem_offset = optional_offset + (92 if is_pe32_plus else 68)
    subsystem = struct.unpack_from("<H", payload, subsystem_offset)[0]
    data_directory_offset = optional_offset + (112 if is_pe32_plus else 96)
    import_table_rva = 0
    import_table_size = 0
    if data_directory_offset + 16 <= optional_offset + optional_header_size:
        import_table_rva, import_table_size = struct.unpack_from("<II", payload, data_directory_offset + 8)

    section_offset = optional_offset + optional_header_size
    sections: list[dict[str, int | str]] = []
    for index in range(section_count):
        offset = section_offset + index * 40
        if offset + 40 > len(payload):
            break
        raw_name = payload[offset : offset + 8].split(b"\x00", 1)[0]
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from("<IIII", payload, offset + 8)
        sections.append(
            {
                "name": raw_name.decode("ascii", errors="replace"),
                "virtual_size": virtual_size,
                "virtual_address": virtual_address,
                "raw_size": raw_size,
                "raw_pointer": raw_pointer,
            }
        )

    imported_libraries: list[str] = []
    import_offset = rva_to_offset(import_table_rva, sections) if import_table_rva else None
    if import_offset is not None:
        for descriptor_offset in range(import_offset, min(len(payload), import_offset + import_table_size + 20), 20):
            if descriptor_offset + 20 > len(payload):
                break
            original_first_thunk, _, _, name_rva, first_thunk = struct.unpack_from("<IIIII", payload, descriptor_offset)
            if original_first_thunk == 0 and name_rva == 0 and first_thunk == 0:
                break
            name_offset = rva_to_offset(name_rva, sections)
            if name_offset is not None:
                library = read_c_string(payload, name_offset)
                if library and library not in imported_libraries:
                    imported_libraries.append(library)

    return {
        "format": "pe",
        "machine": MACHINE_TYPES.get(machine, f"unknown_{machine:#x}"),
        "section_count": section_count,
        "timestamp_raw": timestamp,
        "characteristics_hex": f"{characteristics:#x}",
        "is_dll": bool(characteristics & 0x2000),
        "is_pe32_plus": is_pe32_plus,
        "image_base": image_base,
        "entry_point_rva": address_of_entry_point,
        "subsystem": subsystem,
        "sections": sections,
        "imported_libraries": imported_libraries,
    }


def inspect_binaries(source_root: Path) -> dict[str, Any]:
    binaries = []
    for path in sorted(item for item in source_root.rglob("*") if item.is_file() and item.suffix.lower() in UNSAFE_EXTENSIONS):
        payload = path.read_bytes()
        binaries.append(
            {
                "path": path.as_posix(),
                "filename": path.name,
                "extension": path.suffix.lower(),
                "file_size": path.stat().st_size,
                "sha256": sha256_file(path),
                "static_pe_info": parse_pe(payload),
                "safety_note": "Static metadata only. This file was not loaded, executed, imported, or copied into the runtime tracker.",
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_root": source_root.as_posix(),
        "binary_count": len(binaries),
        "binaries": binaries,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Statically inspect KongYing PE binaries without executing them.")
    parser.add_argument("--source", default="KongYingMap-RC1.0.1", help="Source KongYing folder.")
    parser.add_argument("--output", default="data/kongying/binary_inventory.json", help="JSON output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_root = (REPO_ROOT / args.source).resolve()
    output_path = (REPO_ROOT / args.output).resolve()
    if not source_root.exists():
        raise FileNotFoundError(f"KongYing source folder not found: {source_root}")

    inventory = inspect_binaries(source_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file_obj:
        json.dump(inventory, file_obj, indent=2, ensure_ascii=False)
        file_obj.write("\n")
    print(json.dumps({"output": args.output, "binary_count": inventory["binary_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

